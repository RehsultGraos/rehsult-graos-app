
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import pi

# Função para gerar gráfico radar com verificação de dados
def gerar_grafico_radar(setores, area):
    setores = {k: v for k, v in setores.items() if pd.notnull(v)}
    if len(setores) < 3:
        st.warning(f"Não há dados suficientes para gerar o gráfico de {area}.")
        return

    categorias = list(setores.keys())
    valores = list(setores.values())
    valores += valores[:1]
    N = len(categorias)

    angulos = [n / float(N) * 2 * pi for n in range(N)]
    angulos += angulos[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)

    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(categorias)
    ax.set_rlabel_position(0)
    ax.plot(angulos, valores, marker='o')
    ax.fill(angulos, valores, alpha=0.3)

    st.pyplot(fig)

# Exemplo de uso
st.title("🌱 Rehsult Grãos")
st.markdown("Versão com GPT-4 (simulada) integrada ao diagnóstico")

setores_exemplo = {
    "Pré-emergente": 40,
    "Cobertura": 70,
    "Pós-emergente": 90,
    "Setor Vazio": None
}

st.markdown("### 📊 Resultados - Plantas Daninhas")
gerar_grafico_radar(setores_exemplo, "Plantas Daninhas")
