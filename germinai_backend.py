import time
import re
import requests
from typing import Tuple, Optional
from bs4 import BeautifulSoup

import streamlit as st

try:
    import google.generativeai as genai
    _API_KEY = st.secrets.get("gemini", {}).get("api_key")
    if not _API_KEY:
        raise KeyError("Falta GEMINI_API_KEY em st.secrets['gemini']['api_key']")
    genai.configure(api_key=_API_KEY)
    _GEMINI_OK = True
except Exception as e:
    _GEMINI_OK = False
    _GEMINI_ERR = str(e)

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


def _http_get_json(url: str, params: dict) -> dict:
    headers = {
        "User-Agent": "GerminAI/1.0 (contato: saas_agrolight@ifc.edu.br)",
        "Accept": "application/json",
    }

    for attempt in range(3):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=8)
        except requests.RequestException as e:
            if attempt == 2:
                raise Exception(f"Falha de rede ao acessar serviço de geocodificação: {e}")
            time.sleep(0.8 * (attempt + 1))
            continue

        if 200 <= r.status_code < 300:
            try:
                return r.json()
            except ValueError:
                snippet = (r.text or "")[:200]
                raise Exception(
                    f"Resposta não-JSON do serviço de geocodificação (início): {snippet!r}"
                )

        if r.status_code == 429:
            if attempt == 2:
                raise Exception(
                    "Serviço de geocodificação limitou requisições (429). Tente novamente em instantes."
                )
            time.sleep(1.2 * (attempt + 1))
            continue

        body = (r.text or "").strip()
        try:
            clean = BeautifulSoup(body, "html.parser").get_text(" ", strip=True)
        except Exception:
            clean = body
        clean = clean[:240] or f"HTTP {r.status_code}"
        raise Exception(f"Erro do serviço de geocodificação (HTTP {r.status_code}): {clean}")

    raise Exception("Erro inesperado ao consultar serviço de geocodificação.")


@st.cache_data(ttl=24 * 3600, show_spinner=False)
def _search_place(text: str) -> dict:
    return _http_get_json(
        GEOCODING_URL,
        {
            "name": text,
            "count": 1,
            "language": "pt",
            "format": "json",
        },
    )


_COORD_RE = re.compile(r"^\s*(-?\d{1,3}\.\d+)\s*,\s*(-?\d{1,3}\.\d+)\s*$")


def geolocalizar_diagnostico_completo(
    local_input: str,
) -> Tuple[str, Optional[float], Optional[float]]:
    local_input = (local_input or "").strip()
    if not local_input:
        return "❌ Informe uma cidade/UF, CEP ou coordenadas.", None, None

    lat = lon = None
    cidade = "desconhecida"
    estado = ""
    pais = "desconhecido"

    try:
        m = _COORD_RE.match(local_input)
        if m:
            lat = float(m.group(1))
            lon = float(m.group(2))
            cidade = "coordenadas informadas manualmente"
            estado = ""
            pais = "desconhecido"
        else:
            data = _search_place(local_input)
            results = data.get("results") or []
            if not results:
                return "❌ Localização não reconhecida pela API de geocodificação.", None, None

            r = results[0]
            lat = float(r["latitude"])
            lon = float(r["longitude"])
            cidade = r.get("name") or "desconhecida"
            estado = r.get("admin1") or ""
            pais = r.get("country") or r.get("country_code", "desconhecido")

        bioma = "Bioma estimado"
        solo = "solo típico da região"

        if pais.lower() == "brazil":
            estado_lower = estado.lower()
            if any(x in estado_lower for x in ["santa catarina", "paraná", "rio grande do sul"]):
                bioma = "Mata Atlântica (estimado)"
                solo = "latossolo/cambissolo com boa matéria orgânica (estimado)"

        texto = (
            f"🌍 Localização aproximada: {cidade}, {estado}, {pais}\n"
            f"🗺️ Bioma estimado: {bioma}\n"
            f"🧱 Tipo de solo provável: {solo}\n"
            f"🌐 Coordenadas: {lat:.6f}, {lon:.6f}\n"
            f"📌 Fonte: Geocoding API do Open-Meteo (não comercial)"
        )
        return texto, lat, lon

    except Exception as e:
        return f"❌ Falha ao obter localização: {e}", None, None


def gerar_resposta_final(pergunta: str, latitude: Optional[float], longitude: Optional[float]) -> str:
    if not _GEMINI_OK:
        return f"⚠️ Não foi possível usar o Gemini: {_GEMINI_ERR}"

    local_hint = "coordenadas não disponíveis"
    if isinstance(latitude, (int, float)) and isinstance(longitude, (int, float)):
        local_hint = f"lat {latitude:.6f}, lon {longitude:.6f}"

    prompt = f"""
Estou desenvolvendo um plano de agricultura sintrópica segundo Ernst Götsch.
Localização aproximada: {local_hint}
Pergunta: {pergunta}

Gere um plano didático dividido em:
1. Diagnóstico do local
2. Espécies recomendadas
3. Estratégia de plantio
4. Cronograma (com podas e manejo)
5. Cuidados iniciais

Use linguagem clara para iniciantes.
Se precisar, estime com base em clima subtropical úmido (sul do Brasil) quando a localização for genérica.
"""

    try:
        modelo = genai.GenerativeModel("gemini-2.0-flash")
        resposta = modelo.generate_content(prompt)
        txt = (resposta.text or "").strip()
        if not txt:
            return "⚠️ O modelo retornou uma resposta vazia. Tente novamente em alguns segundos."
        return txt
    except Exception as e:
        return f"❌ Falha ao gerar plano: {e}"
