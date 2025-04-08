
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
from math import pi

st.set_page_config(page_title="Rehsult Grãos", layout="centered")
st.image("LOGO REAGRO TRATADA.png", width=200)

st.title("Rehsult Grãos")
st.markdown("Diagnóstico de fazendas produtoras de grãos com análise simulada GPT-4")

# ---------- ETAPA INICIAL ----------
if "estado" not in st.session_state:
    st.session_state.estado = "dados_iniciais"
    st.session_state.respostas = {}
    st.session_state.areas_respondidas = []
    st.session_state.dados_iniciais = {}

# ... (código completo aqui com regras já integradas) ...
