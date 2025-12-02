import streamlit as st
from germinai_backend import gerar_resposta_final, geolocalizar_diagnostico_completo

st.set_page_config(page_title="GerminAI", page_icon="🌿", layout="centered")

with st.sidebar:
    st.markdown("### ⚙️ Utilitários")
    if st.button("🔄 Limpar cache e reiniciar"):
        st.cache_data.clear()
        st.rerun()

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
        tipos_especies = st.multiselect(
            "🌿 Tipos de espécies desejadas:",
            ["Frutíferas", "Leguminosas", "Madeireiras", "Todas"],
        )
        preferencia_especies = st.radio(
            "🍃 Preferência por espécies:",
            ["Nativas", "Exóticas", "Mistas"],
        )

    submitted = st.form_submit_button("🌱 Gerar plano agroflorestal")

if submitted:
    with st.spinner("🔎 Analisando dados e cultivando sugestões..."):
        try:
            diagnostico_texto, latitude, longitude = geolocalizar_diagnostico_completo(local_input)

            if latitude is None or longitude is None:
                st.error(diagnostico_texto)
                st.stop()

            st.success("📍 Diagnóstico do Local")
            st.markdown(diagnostico_texto)

            pergunta = (
                "Como iniciar uma agricultura sintrópica segundo Ernst Götsch na sua região, "
                "considerando clima, solo e área disponível?"
            )
            resposta = gerar_resposta_final(pergunta, latitude, longitude)

            st.divider()
            st.markdown("### 🌳 Plano Agroflorestal Personalizado")
            st.markdown(resposta)

            tipos_especies_str = ", ".join(tipos_especies) if tipos_especies else "Não informado"

            plano_txt = f"""Plano Agroflorestal - GerminAI

Local informado: {local_input}
Tamanho da área: {tamanho_area}
Tipo de relevo: {relevo}
Incidência de luz: {sombra}
Objetivo da agrofloresta: {objetivo}
Horas semanais disponíveis: {dedicacao}
Tipos de espécies desejadas: {tipos_especies_str}
Preferência por espécies: {preferencia_especies}
Já existe algo plantado: {existe_plantio or "Não informado"}

------------------------------
Diagnóstico do local
------------------------------
{diagnostico_texto}

------------------------------
Plano agroflorestal personalizado
------------------------------
{resposta}
"""

            st.download_button(
                label="📥 Baixar plano em .txt",
                data=plano_txt,
                file_name="plano_agroflorestal_germinai.txt",
                mime="text/plain",
            )

        except Exception as e:
            st.error(f"Erro ao gerar resposta: {e}")
