import time
import re
import requests
from typing import Tuple, Optional
from bs4 import BeautifulSoup

import streamlit as st

# ---- Gemini (mensagem amigável se segredo faltar) ----
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

# ---------- util HTTP robusto ----------
def _http_get_json(url: str, params: dict) -> dict:
    """
    Faz GET e tenta parsear JSON com fallback a erros legíveis.
    Lança Exception com mensagem curta e útil (sem stack HTML).
    """
    headers = {
        # Bons modos com Nominatim: inclua contato
        "User-Agent": "GerminAI/1.0 (contato: fernanda@example.com)",
        "Accept": "application/json",
    }

    # backoff leve para 429
    for attempt in range(3):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=8)
        except requests.RequestException as e:
            # problemas de rede/DNS/timeout
            if attempt == 2:
                raise Exception(f"Falha de rede ao acessar serviço de mapas: {e}")
            time.sleep(0.8 * (attempt + 1))
            continue

        # 2xx?
        if 200 <= r.status_code < 300:
            # Tente JSON — se falhar, mostre o início do corpo
            try:
                return r.json()
            except ValueError:
                snippet = (r.text or "")[:200]
                raise Exception(f"Resposta não-JSON do serviço de mapas (início): {snippet!r}")

        # 429 = rate limit
        if r.status_code == 429:
            if attempt == 2:
                raise Exception("Serviço de mapas limitou requisições (429). Tente novamente em instantes.")
            time.sleep(1.2 * (attempt + 1))
            continue

        # Outros códigos: tente extrair mensagem legível
        body = (r.text or "").strip()
        # se vier HTML, limpe
        try:
            clean = BeautifulSoup(body, "html.parser").get_text(" ", strip=True)
        except Exception:
            clean = body
        clean = clean[:240] or f"HTTP {r.status_code}"
        raise Exception(f"Erro do serviço de mapas (HTTP {r.status_code}): {clean}")

    # não chega aqui
    raise Exception("Erro inesperado ao consultar serviço de mapas.")

# cacheia por 1 dia requisições iguais (evita 429)
@st.cache_data(ttl=24 * 3600, show_spinner=False)
def _search_place(text: str) -> list:
    return _http_get_json(
        "https://nominatim.openstreetmap.org/search",
        {"q": text, "format": "json", "accept-language": "pt-BR"},
    )

@st.cache_data(ttl=24 * 3600, show_spinner=False)
def _reverse(lat: float, lon: float) -> dict:
    return _http_get_json(
        "https://nominatim.openstreetmap.org/reverse",
        {"lat": lat, "lon": lon, "format": "json", "zoom": 14, "accept-language": "pt-BR"},
    )

_COORD_RE = re.compile(r"^\s*(-?\d{1,3}\.\d+)\s*,\s*(-?\d{1,3}\.\d+)\s*$")

def geolocalizar_diagnostico_completo(local_input: str) -> Tuple[str, Optional[float], Optional[float]]:
    """
    Retorna (diagnóstico_texto, lat, lon).
    Em caso de falha, lat/lon = None e texto com o motivo.
    """
    local_input = (local_input or "").strip()
    if not local_input:
        return "❌ Informe uma cidade/CEP ou coordenadas.", None, None

    # 1) Coordenadas?
    m = _COORD_RE.match(local_input)
    lat = lon = None
    try:
        if m:
            lat = float(m.group(1))
            lon = float(m.group(2))
        else:
            # 2) Busca por texto
            items = _search_place(local_input)
            if not items:
                return "❌ Localização não reconhecida.", None, None
            lat = float(items[0]["lat"])
            lon = float(items[0]["lon"])

        # 3) Reverse lookup
        rev = _reverse(lat, lon)
        display = rev.get("display_name", "")
        addr = rev.get("address", {}) or {}

        pais = addr.get("country", "desconhecido")
        estado = addr.get("state") or addr.get("state_code", "")
        cidade = addr.get("city") or addr.get("town") or addr.get("village") or "desconhecida"

        # Bioma estimado simples
        bioma = "Bioma estimado"
        solo = "solo típico da região"
        # heurística simples p/ BR sul
        uf = (addr.get("state_code") or "").upper()
        if pais.lower() == "brazil":
            if uf in {"SC", "RS", "PR"} or any(x in estado.lower() for x in ["santa catarina", "paraná", "rio grande do sul"]):
                bioma = "Mata Atlântica (estimado)"
                solo = "latossolo/cambissolo com boa matéria orgânica (estimado)"

        texto = (
            f"🌍 Localização: {cidade}, {estado or uf}, {pais}\n"
            f"🗺️ Bioma estimado: {bioma}\n"
            f"🧱 Tipo de solo provável: {solo}\n"
            f"🌐 Coordenadas: {lat:.6f}, {lon:.6f}\n"
            f"📌 Fonte: Nominatim (OpenStreetMap)"
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
