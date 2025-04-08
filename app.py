
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
from math import pi

st.set_page_config(page_title="Rehsult Grãos", layout="wide")
st.title("🌱 Rehsult Grãos")
st.markdown("Versão com GPT-4 (simulada) integrada ao diagnóstico")

# ------------------ Funções ------------------

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
    ax.set_title(f"Radar - {area}")
    st.pyplot(fig)

def gerar_analise_simulada(setores_areas):
    texto = "🤖 **Análise com GPT-4 (simulada)**\n\n"
    for area, setores in setores_areas.items():
        for setor, nota in setores.items():
            if nota < 50:
                texto += f"- O setor **{setor}** em **{area}** apresenta baixa pontuação. Avaliar ações corretivas.\n"
            elif nota < 75:
                texto += f"- O setor **{setor}** em **{area}** está mediano. Há espaço para ajustes.\n"
            else:
                texto += f"- O setor **{setor}** em **{area}** apresenta bom desempenho.\n"
    texto += "\n🎯 **Recomendações:**\n- Revisar práticas nos setores com desempenho fraco.\n- Otimizar os setores intermediários.\n"
    return texto

def gerar_pdf(analise, setores_areas):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for area, setores in setores_areas.items():
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, f"Área: {area}", ln=True)
        pdf.set_font("Arial", size=12)
        for setor, val in setores.items():
            pdf.cell(200, 10, f"{setor}: {val:.1f}%", ln=True)
        pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "Análise GPT-4 (simulada)", ln=True)
    pdf.set_font("Arial", size=12)
    for linha in analise.split("\n"):
        pdf.multi_cell(0, 10, linha)

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# ------------------ Dados simulados ------------------

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

# ------------------ Relatório ------------------

for area, setores in setores_por_area.items():
    st.markdown(f"### 📊 Resultados - {area}")
    st.markdown(f"**Pontuação Geral:** {np.mean(list(setores.values())):.1f}%")
    gerar_grafico_radar(setores, area)

st.markdown("---")
analise = gerar_analise_simulada(setores_por_area)
st.markdown(analise)

pdf_buffer = gerar_pdf(analise, setores_por_area)
st.download_button("📄 Baixar Relatório em PDF", data=pdf_buffer, file_name="relatorio_rehsult.pdf")
