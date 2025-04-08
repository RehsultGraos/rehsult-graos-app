
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="Rehsult Grãos", layout="wide")

def gerar_grafico_radar(setores, titulo):
    categorias = list(setores.keys())
    valores = list(setores.values())

    categorias += [categorias[0]]
    valores += [valores[0]]

    angulos = np.linspace(0, 2 * np.pi, len(categorias), endpoint=False).tolist()
    angulos += [angulos[0]]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.plot(angulos, valores, marker='o')
    ax.fill(angulos, valores, alpha=0.3)
    ax.set_yticklabels([])
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(categorias)
    ax.set_title(f"Radar - {titulo}")
    st.pyplot(fig)

def gerar_analise_simulada(setores_areas):
    analise = """✅ **Análise Simulada:**

"""
    for area, setores in setores_areas.items():
        for setor, nota in setores.items():
            if nota < 50:
                analise += f"- A área de **{setor}** em **{area}** apresenta baixa pontuação, indicando atenção.\n"
            elif nota < 75:
                analise += f"- A área de **{setor}** em **{area}** está razoável, mas pode melhorar.\n"
            else:
                analise += f"- A área de **{setor}** em **{area}** está com boa pontuação.\n"
    analise += "\n🎯 **Recomendações:**\n- Revisar práticas nos setores com pontuação baixa.\n- Consultar especialistas para ações corretivas.\n"
    return analise

# Interface
st.title("🌱 Rehsult Grãos")
st.markdown("Versão com GPT-4 (simulada) integrada ao diagnóstico")

# Simulação de dados
setores_por_area = {
    "Plantas Daninhas": {
        "Pré-emergente": 35.0,
        "Cobertura": 65.0,
        "Pós-emergente": 85.0
    },
    "Fertilidade": {
        "Análise de Solo": 45.0,
        "Calagem e Gessagem": 55.0,
        "Macronutrientes": 78.0
    }
}

# Gerar análise simulada
st.subheader("🤖 Análise com GPT-4 (simulada)")
analise = gerar_analise_simulada(setores_por_area)
st.markdown(analise)

# Exibir gráficos
for area, setores in setores_por_area.items():
    st.markdown(f"### 📊 Resultados - {area}")
    st.markdown(f"**Pontuação Geral:** {np.mean(list(setores.values())):.1f}%")
    gerar_grafico_radar(setores, area)
