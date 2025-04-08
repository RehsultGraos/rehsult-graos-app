
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="Rehsult Grãos", layout="centered")

# Função para gerar gráfico radar
def gerar_grafico_radar(setores, area):
    categorias = list(setores.keys())
    valores = list(setores.values())
    N = len(categorias)

    valores += valores[:1]
    angulos = [n / float(N) * 2 * np.pi for n in range(N)]
    angulos += angulos[:1]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    plt.xticks(angulos[:-1], categorias)
    ax.plot(angulos, valores, marker='o')
    ax.fill(angulos, valores, alpha=0.25)
    st.pyplot(fig)

# Função para gerar PDF
def gerar_pdf(analise, setores_areas):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.multi_cell(0, 10, txt="Rehsult Grãos - Diagnóstico com GPT-4 (simulado)", align='C')
    pdf.ln()

    for area, setores in setores_areas.items():
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"Resultados - {area}", ln=True)
        pdf.set_font("Arial", size=12)
        for setor, valor in setores.items():
            pdf.cell(0, 10, f"{setor}: {valor:.1f}%", ln=True)
        pdf.ln()

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Análise Simulada:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, analise)

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# Função simulada para gerar análise com IA
def gerar_analise_simulada(setores_areas):
    analise = "✅ **Análise Simulada:**\n"
    recomendacoes = []

    for area, setores in setores_areas.items():
        for setor, score in setores.items():
            if score < 50:
                analise += f"- A área de **{setor}** em **{area}** apresenta baixa pontuação, indicando atenção.\n"
                recomendacoes.append(f"Melhorar práticas em {setor} ({area}).")
            elif score < 75:
                analise += f"- A área de **{setor}** em **{area}** está razoável, mas pode melhorar.\n"
                recomendacoes.append(f"Revisar estratégias em {setor} ({area}).")
            else:
                analise += f"- A área de **{setor}** em **{area}** está com boa pontuação.\n"

    analise += "\n🎯 **Recomendações:**\n"
    for r in recomendacoes:
        analise += f"- {r}\n"

    return analise

# Simulação dos dados finais
setores_areas = {
    "Plantas Daninhas": {
        "Pré-emergente": 45,
        "Cobertura": 70,
        "Pós-emergente": 85
    },
    "Fertilidade": {
        "Análise de Solo": 48,
        "Calagem e Gessagem": 60,
        "Macronutrientes": 80
    }
}

st.title("🌱 Rehsult Grãos")
st.markdown("Diagnóstico de fazendas produtoras de grãos com análise simulada GPT-4")

if "mostrar_resultado" not in st.session_state:
    st.session_state.mostrar_resultado = False

if not st.session_state.mostrar_resultado:
    if st.button("Iniciar Diagnóstico"):
        st.session_state.mostrar_resultado = True
        st.rerun()
else:
    st.success("✅ Diagnóstico Concluído")
    for area, setores in setores_areas.items():
        st.markdown(f"### 📊 Resultados - {area}")
        media = np.mean(list(setores.values()))
        st.markdown(f"**Pontuação Geral:** {media:.1f}%")
        gerar_grafico_radar(setores, area)

    analise = gerar_analise_simulada(setores_areas)
    st.markdown("### 🤖 Análise com GPT-4 (simulada)")
    st.markdown(analise)

    pdf_buffer = gerar_pdf(analise, setores_areas)
    st.download_button(
        label="📥 Baixar Relatório em PDF",
        data=pdf_buffer,
        file_name="diagnostico_rehsult_graos.pdf",
        mime="application/pdf"
    )
