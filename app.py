
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
import base64

# Função para gerar análise simulada
def gerar_analise_simulada(setores_areas):
    analise = "### 🤖 Análise com GPT-4 (simulada)\n\n"
    analise += "✅ **Análise Simulada:**\n\n"
    for area, setores in setores_areas.items():
        for setor, pct in setores.items():
            if pct < 50:
                analise += f"- O setor de **{setor}** na área de **{area}** está com baixa pontuação.\n"
            elif pct < 75:
                analise += f"- O setor de **{setor}** na área de **{area}** está com desempenho razoável.\n"
            else:
                analise += f"- O setor de **{setor}** na área de **{area}** está com bom desempenho.\n"
    analise += "\n🎯 **Recomendações:**\n"
    analise += "- Reavaliar os setores com baixa pontuação para identificar causas.\n"
    analise += "- Buscar otimizações nos setores com desempenho razoável.\n"
    analise += "- Manter as boas práticas nos setores com bom desempenho.\n"
    return analise

# Função para gerar PDF
def gerar_pdf(buffer, setores_areas, analise_simulada):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="📊 Diagnóstico Rehsult Grãos", ln=True)

    for area, setores in setores_areas.items():
        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(200, 10, txt=f"Área: {area}", ln=True)
        pdf.set_font("Arial", size=12)
        for setor, valor in setores.items():
            pdf.cell(200, 10, txt=f"{setor}: {valor:.1f}%", ln=True)

    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(200, 10, txt="Análise Simulada", ln=True)
    pdf.set_font("Arial", size=12)
    for linha in analise_simulada.split("\n"):
        pdf.multi_cell(0, 10, linha)

    pdf.output(buffer)
    buffer.seek(0)

# Início da aplicação
st.set_page_config(page_title="Rehsult Grãos", layout="centered")
st.image("LOGO REAGRO TRATADA.png", width=150)
st.title("🌾 Rehsult Grãos")
st.markdown("Versão com GPT-4 (simulada) integrada ao diagnóstico")

# Carregamento de dados
file = "Teste Chat.xlsx"
excel = pd.ExcelFile(file)
abas = {"Fertilidade": "Fertilidade", "Plantas Daninhas": "Planta Daninha"}

respostas = {}
pontuacoes = {}
setores_areas = {}

for nome_area, aba in abas.items():
    df = pd.read_excel(excel, sheet_name=aba)
    mapa = {"Sim": 1, "Não": 0, "Não sei": 0.5}
    df["Resposta"] = df["Resposta"].fillna("Não sei")
    df["Score"] = df["Resposta"].map(mapa) * df["Peso"]
    score_total = df["Score"].sum() / df["Peso"].sum() * 100
    pontuacoes[nome_area] = score_total

    setores = df["Setor"].unique()
    setores_pontuacao = {}
    for setor in setores:
        df_setor = df[df["Setor"] == setor]
        score = df_setor["Score"].sum() / df_setor["Peso"].sum() * 100
        setores_pontuacao[setor] = score
    setores_areas[nome_area] = setores_pontuacao

# Mostrar pontuações e gráfico
for area, setores in setores_areas.items():
    st.markdown(f"### 📊 Resultados - {area}")
    st.write(f"**Pontuação Geral:** {pontuacoes[area]:.1f}%")
    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw={'projection': 'polar'})
    categorias = list(setores.keys())
    valores = list(setores.values())
    categorias += [categorias[0]]
    valores += [valores[0]]
    angles = np.linspace(0, 2 * np.pi, len(categorias), endpoint=False).tolist()
    angles += angles[:1]
    ax.plot(angles, valores, marker='o')
    ax.fill(angles, valores, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categorias)
    ax.set_yticklabels([])
    st.pyplot(fig)

# Gerar análise simulada
analise = gerar_analise_simulada(setores_areas)
st.markdown(analise)

# Gerar botão de download do PDF
buffer = BytesIO()
gerar_pdf(buffer, setores_areas, analise)
b64_pdf = base64.b64encode(buffer.read()).decode('utf-8')
href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="diagnostico.pdf">📥 Baixar Relatório em PDF</a>'
st.markdown(href, unsafe_allow_html=True)
