
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
import unicodedata

st.set_page_config(page_title="🌱 Rehsult Grãos", layout="centered")

# Logo e título
st.image("LOGO REAGRO TRATADA.png", width=180)
st.title("🌱 Rehsult Grãos")
st.markdown("Diagnóstico de fazendas produtoras de grãos com análise simulada **GPT-4**")

# Função para gerar gráfico radar
def gerar_grafico_radar(setores, area):
    categorias = list(setores.keys())
    valores = list(setores.values())
    categorias += [categorias[0]]
    valores += [valores[0]]

    angulos = [n / float(len(categorias)) * 2 * 3.14159 for n in range(len(categorias))]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.plot(angulos, valores, marker='o')
    ax.fill(angulos, valores, alpha=0.25)
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(categorias)
    ax.set_title(f"📊 Radar - {area}", y=1.1)
    st.pyplot(fig)

# Função para gerar PDF
def gerar_pdf(analise, setores_areas):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "🌱 Diagnóstico Rehsult Grãos", ln=True, align="C")

    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "✅ Diagnóstico Concluído", ln=True)

    pdf.set_font("Arial", "", 12)
    for area, setores in setores_areas.items():
        pdf.cell(200, 10, f"📊 Resultados - {area}", ln=True)
        media = sum(setores.values()) / len(setores)
        pdf.cell(200, 10, f"Pontuação Geral: {media:.1f}%", ln=True)
        for setor, valor in setores.items():
            pdf.cell(200, 10, f"- {setor}: {valor:.1f}%", ln=True)

    pdf.multi_cell(0, 10, f"🤖 Análise com GPT-4 (simulada):
{unicodedata.normalize('NFKD', analise).encode('latin-1', 'ignore').decode('latin-1')}")

    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    return BytesIO(pdf_bytes)

# Função para gerar análise simulada
def gerar_analise_simulada(setores_areas):
    analise = "✅ **Análise Simulada:**\n\n"
    recomendacoes = []

    for area, setores in setores_areas.items():
        for setor, valor in setores.items():
            if valor < 50:
                analise += f"- A área de **{setor}** em **{area}** apresenta baixa pontuação, indicando atenção.\n"
                recomendacoes.append(f"Revisar práticas na área de {setor} ({area}).")
            elif 50 <= valor < 80:
                analise += f"- A área de **{setor}** em **{area}** está razoável, mas pode melhorar.\n"
                recomendacoes.append(f"Aprimorar técnicas em {setor} ({area}).")
            else:
                analise += f"- A área de **{setor}** em **{area}** está com boa pontuação.\n"

    if recomendacoes:
        analise += "\n🎯 **Recomendações:**\n"
        for rec in recomendacoes:
            analise += f"- {rec}\n"

    return analise

# Simulando setores
setores_exemplo = {
    "Plantas Daninhas": {
        "Pré emergente": 65,
        "Manejo integrado": 85,
        "Dessecação": 70,
        "Capina": 95
    },
    "Fertilidade": {
        "Análise de Solo": 50,
        "Calagem e Gessagem": 60,
        "Macronutrientes": 85
    }
}

st.markdown("## ✅ Diagnóstico Concluído")

for area, setores in setores_exemplo.items():
    st.markdown(f"### 📊 Resultados - {area}")
    media = sum(setores.values()) / len(setores)
    st.markdown(f"**Pontuação Geral:** {media:.1f}%")
    gerar_grafico_radar(setores, area)

# Gerar análise simulada
analise = gerar_analise_simulada(setores_exemplo)
st.markdown("### 🤖 Análise com GPT-4 (simulada)")
st.markdown(analise)

# PDF download
pdf_buffer = gerar_pdf(analise, setores_exemplo)
st.download_button("📄 Baixar Relatório em PDF", data=pdf_buffer, file_name="relatorio_rehsult.pdf")
