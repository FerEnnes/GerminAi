import requests
import re
from bs4 import BeautifulSoup
import google.generativeai as genai

import streamlit as st
genai.configure(api_key=st.secrets["gemini"]["api_key"])


def geolocalizar_diagnostico_completo(local_input):
    def is_coord(texto):
        return re.match(r"^-?\d{1,3}\.\d+,\s*-?\d{1,3}\.\d+$", texto.strip())

    def get_coords_from_text(text):
        url = f"https://nominatim.openstreetmap.org/search?q={text}&format=json"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers)
        data = r.json()
        if not data:
            return None, None, "❌ Localização não reconhecida."
        return data[0]["lat"], data[0]["lon"], data[0]["display_name"]

    def reverse_lookup(lat, lon):
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers)
        data = r.json()
        return data.get("display_name", ""), data.get("address", {})

    if is_coord(local_input):
        lat, lon = local_input.split(",")
        local_formatado, endereco = reverse_lookup(lat.strip(), lon.strip())
    else:
        lat, lon, local_formatado = get_coords_from_text(local_input)
        if lat and lon:
            local_formatado, endereco = reverse_lookup(lat, lon)
        else:
            return "❌ Localização inválida", None, None

    pais = endereco.get("country", "desconhecido")
    estado = endereco.get("state", "")
    cidade = endereco.get("city", endereco.get("town", endereco.get("village", "desconhecida")))

    # Bioma estimado simples
    if pais.lower() == "brazil":
        bioma = "Mata Atlântica" if estado.lower() in ["sc", "rs", "pr"] else "Bioma brasileiro estimado"
        solo = "solo tropical ou subtropical médio"
    else:
        bioma = "Vegetação estimada por latitude"
        solo = "solo tropical ou subtropical médio"

    resposta = f"""🌍 Localização reconhecida: {cidade}, {estado}, {pais}
🗺️ Bioma estimado: {bioma}
🧱 Tipo de solo provável: {solo}
🌐 Coordenadas: {lat}, {lon}
📌 Fonte: Nominatim (OpenStreetMap)"""

    return resposta, float(lat), float(lon)

def gerar_resposta_final(pergunta, latitude, longitude):
    prompt = f"""
    Estou desenvolvendo um plano de agricultura sintrópica segundo Ernst Götsch.
    Localização aproximada: lat {latitude}, lon {longitude}
    Pergunta: {pergunta}

    Gere um plano didático dividido em:
    1. Diagnóstico do local
    2. Espécies recomendadas
    3. Estratégia de plantio
    4. Cronograma (com podas e manejo)
    5. Cuidados iniciais

    Use linguagem clara para iniciantes.
    """

    modelo = genai.GenerativeModel("gemini-2.0-flash")
    resposta = modelo.generate_content(prompt)
    return resposta.text
