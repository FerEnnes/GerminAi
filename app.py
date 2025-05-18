import streamlit as st
from germinai_backend import gerar_resposta_final, geolocalizar_diagnostico_completo

st.set_page_config(page_title="GerminAI", page_icon="🌿", layout="centered")

# Cabeçalho
st.markdown("# 🌿 GerminAI")
st.markdown("Seu guia para iniciar uma agricultura sintrópica segundo Ernst Götsch. 🌀")
st.divider()

st.subheader("📋 Preencha as informações do seu terreno")

with st.form("formulario"):
    col1, col2 = st.columns(2)

    with col1:
        local_input = st.text_input("📍 Localização (Cidade/UF, CEP ou coordenadas):")
        tamanho_area = st.text_input("📐 Tamanho da área (m² ou ha):")
        relevo = st.selectbox("🗻 Tipo de relevo:", ["Plano", "Inclinado", "Irregular"])
        existe_plantio = st.text_input("🌾 Já existe algo plantado no local? (se sim, o quê?):")

    with col2:
        sombra = st.selectbox("🌤️ Incidência de luz:", ["Sol pleno", "Sombra", "Misto"])
        objetivo = st.selectbox("🎯 Objetivo da agrofloresta:", ["Alimentação", "Comercial", "Restauração", "Outro"])
        dedicacao = st.slider("⏰ Horas semanais disponíveis:", 1, 40, 5)
        tipos_especies = st.multiselect("🌿 Tipos de espécies desejadas:", ["Frutíferas", "Leguminosas", "Madeireiras", "Todas"])
        preferencia_especies = st.radio("🍃 Preferência por espécies:", ["Nativas", "Exóticas", "Mistas"])

    submitted = st.form_submit_button("🌱 Gerar plano agroflorestal")

if submitted:
    with st.spinner("🔎 Analisando dados e cultivando sugestões..."):
        try:
            diagnostico_texto, latitude, longitude = geolocalizar_diagnostico_completo(local_input)
            st.success("📍 Diagnóstico do Local")
            st.markdown(diagnostico_texto)

            pergunta = "Como iniciar uma agricultura sintrópica segundo Ernst Götsch na sua região, considerando clima, solo e área disponível?"
            resposta = gerar_resposta_final(pergunta, latitude, longitude)

            st.divider()
            st.markdown("### 🌳 Plano Agroflorestal Personalizado")
            st.markdown(resposta)

        except Exception as e:
            st.error(f"Erro ao gerar resposta: {e}")
