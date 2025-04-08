import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="Rehsult Grãos", layout="wide")
st.title("🌱 Rehsult Grãos")
st.markdown("Diagnóstico de fazendas produtoras de grãos com análise simulada GPT-4")

# Dados simulados para perguntas iniciais
if "fazenda" not in st.session_state:
    st.session_state.fazenda = ""
    st.session_state.produtividade_soja = 0
    st.session_state.produtividade_milho = 0
    st.session_state.coletado_dados = False

if not st.session_state.coletado_dados:
    st.subheader("Informações iniciais da fazenda")
    st.session_state.fazenda = st.text_input("Nome da Fazenda")
    st.session_state.produtividade_soja = st.number_input("Produtividade de Soja (sc/ha)", 0.0, 100.0)
    st.session_state.produtividade_milho = st.number_input("Produtividade de Milho (sc/ha)", 0.0, 100.0)
    if st.button("Iniciar Diagnóstico"):
        st.session_state.coletado_dados = True
        st.rerun()
    st.stop()

# Dados simulados de pontuação por setor
setores_areas = {
    "Planta Daninha": {
        "Manejo integrado": 95,
        "Pré emergente": 90,
        "Dessecação": 85,
        "Capina": 92,
    },
    "Fertilidade": {
        "Análise de Solo": 70,
        "Calagem e Gessagem": 78,
        "Macronutrientes": 88
    }
}

# Geração do gráfico radar
def gerar_grafico_radar(setores, area):
    categorias = list(setores.keys())
    valores = list(setores.values())
    valores += valores[:1]  # fecha o gráfico

    angulos = np.linspace(0, 2 * np.pi, len(categorias), endpoint=False).tolist()
    angulos += angulos[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angulos, valores, marker='o')
    ax.fill(angulos, valores, alpha=0.25)
    ax.set_thetagrids(np.degrees(angulos[:-1]), categorias)
    ax.set_title(f"Radar - {area}")
    st.pyplot(fig)

# Geração da análise simulada
def gerar_analise_simulada(setores_dict):
    analise = "🤖 **Análise com GPT-4 (simulada)**\n"
    analise += "\n✅ **Análise Simulada:**\n"
    for area, setores in setores_dict.items():
        for setor, score in setores.items():
            if score < 60:
                analise += f"- O setor **{setor}** em **{area}** apresenta baixa pontuação, indicando atenção.\n"
            elif score < 80:
                analise += f"- O setor **{setor}** em **{area}** está razoável, mas pode melhorar.\n"
            else:
                analise += f"- O setor **{setor}** em **{area}** está com boa pontuação.\n"
    analise += "\n🎯 **Recomendações:**\n"
    analise += "- Revisar práticas nos setores com desempenho fraco.\n"
    analise += "- Otimizar os setores intermediários."
    return analise

# Geração do PDF
def gerar_pdf(analise, setores_areas):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    try:
        pdf.multi_cell(0, 10, analise.encode('latin1').decode('latin1'))
    except UnicodeEncodeError:
        texto_tratado = analise.encode('latin1', 'replace').decode('latin1')
        pdf.multi_cell(0, 10, texto_tratado)

    for area, setores in setores_areas.items():
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"{area}", ln=True)
        pdf.set_font("Arial", size=12)
        for setor, score in setores.items():
            linha = f"{setor}: {score:.1f}%"
            try:
                pdf.cell(0, 10, linha.encode('latin1').decode('latin1'), ln=True)
            except UnicodeEncodeError:
                linha_tratada = linha.encode('latin1', 'replace').decode('latin1')
                pdf.cell(0, 10, linha_tratada, ln=True)

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return BytesIO(pdf_bytes)

# Resultado
st.subheader("\n✅ Diagnóstico Concluído")
for area, setores in setores_areas.items():
    st.markdown(f"\n### \ud83d\udcca Resultados - {area}")
    media = np.mean(list(setores.values()))
    st.markdown(f"**Pontuação Geral:** {media:.1f}%")
    gerar_grafico_radar(setores, area)

# Análise
analise = gerar_analise_simulada(setores_areas)
st.markdown("\n" + analise)

# PDF download
pdf_buffer = gerar_pdf(analise, setores_areas)
st.download_button("📄 Baixar Relatório em PDF", data=pdf_buffer, file_name="relatorio_diagnostico.pdf")
