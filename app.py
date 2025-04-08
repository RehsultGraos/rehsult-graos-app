import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
from PIL import Image

# Logo
st.image("LOGO REAGRO TRATADA.png", width=150)
st.markdown("# 🌱 Rehsult Grãos")
st.markdown("Diagnóstico de fazendas produtoras de grãos com análise simulada GPT-4")

# Entradas iniciais
with st.form("info_fazenda"):
    col1, col2 = st.columns(2)
    nome_resp = col1.text_input("👨‍🌾 Nome do responsável pela fazenda")
    nome_fazenda = col2.text_input("🏡 Nome da fazenda")
    prod_esperada = st.text_input("🌾 Produtividade média esperada (sc/ha)")
    submitted = st.form_submit_button("Iniciar Diagnóstico")
    if submitted:
        st.session_state.respostas = {}
        st.session_state.pergunta_id = 1
        st.experimental_rerun()

# Exemplo de pergunta
if "pergunta_id" in st.session_state:
    df = pd.read_excel("Teste Chat.xlsx")
    linha = df[df["Referência"] == st.session_state.pergunta_id].iloc[0]
    st.markdown(f"### {linha['Pergunta']}")
    col1, col2, col3 = st.columns(3)
    if col1.button("✅ Sim"):
        st.session_state.respostas[linha["Referência"]] = "Sim"
        st.session_state.pergunta_id = linha["Próxima (Sim)"]
        st.experimental_rerun()
    if col2.button("❌ Não"):
        st.session_state.respostas[linha["Referência"]] = "Não"
        st.session_state.pergunta_id = linha["Próxima (Não)"]
        st.experimental_rerun()
    if col3.button("🤔 Não sei"):
        st.session_state.respostas[linha["Referência"]] = "Não sei"
        st.session_state.pergunta_id = linha["Próxima (Não)"]
        st.experimental_rerun()
