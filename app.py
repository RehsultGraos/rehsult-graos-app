
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="Rehsult Grãos", layout="centered")

def gerar_grafico_radar(setores, area):
    categorias = list(setores.keys())
    valores = list(setores.values())

    # Corrigir para radar
    categorias += categorias[:1]
    valores += valores[:1]

    angles = np.linspace(0, 2 * np.pi, len(categorias), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angles, valores, marker='o')
    ax.fill(angles, valores, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categorias)
    ax.set_title(f"Radar - {area}")
    st.pyplot(fig)

def gerar_pdf(analise):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, analise)
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

def gerar_analise_simulada(setores_areas):
    texto = "🤖 Análise com GPT-4 (simulada)

✅ Análise Simulada:
"
    for area, setores in setores_areas.items():
        for setor, valor in setores.items():
            if valor < 50:
                texto += f"- O setor de **{setor}** em **{area}** está com baixa pontuação. Sugere-se revisão das práticas adotadas.
"
            elif valor < 70:
                texto += f"- O setor de **{setor}** em **{area}** apresenta pontuação mediana. Pode haver oportunidades de melhoria.
"
            else:
                texto += f"- O setor de **{setor}** em **{area}** está indo bem. Manter as práticas atuais.
"
    return texto

# Layout
st.title("🌱 Rehsult Grãos")
st.markdown("Versão com GPT-4 (simulada) integrada ao diagnóstico")

# Simulação das notas por setor (exemplo)
setores_por_area = {
    "Planta Daninha": {
        "Pré-emergente": 45,
        "Cobertura": 65,
        "Pós-emergente": 80
    },
    "Fertilidade": {
        "Calagem e Gessagem": 40,
        "Macronutrientes": 72,
        "Micronutrientes": 88
    }
}

# Escolha da área para iniciar
if "area_atual" not in st.session_state:
    st.session_state.area_atual = None

if st.session_state.area_atual is None:
    st.subheader("Qual área deseja começar?")
    area_escolhida = st.radio("", ["Planta Daninha", "Fertilidade"])
    if st.button("Iniciar Diagnóstico"):
        st.session_state.area_atual = area_escolhida
        st.experimental_rerun()

# Apresenta gráfico e análise simulada
else:
    area = st.session_state.area_atual
    setores = setores_por_area.get(area, {})

    st.markdown(f"### ✅ Diagnóstico Concluído")
    st.markdown(f"### 📊 Resultados - {area}")
    media = np.mean(list(setores.values()))
    st.markdown(f"**Pontuação Geral:** {media:.1f}%")
    gerar_grafico_radar(setores, area)

    # Perguntar se deseja responder outra área
    outras_areas = [a for a in setores_por_area if a != area]
    if outras_areas:
        st.markdown("### Deseja responder também sobre " + outras_areas[0] + "?")
        col1, col2 = st.columns(2)
        if col1.button("✅ Sim"):
            st.session_state.area_atual = outras_areas[0]
            st.experimental_rerun()
        elif col2.button("❌ Não"):
            st.session_state.area_atual = "finalizar"
            st.experimental_rerun()
    else:
        st.session_state.area_atual = "finalizar"
        st.experimental_rerun()

# Tela final
if st.session_state.area_atual == "finalizar":
    st.markdown("## 🤖 Análise com GPT-4 (simulada)")
    analise = gerar_analise_simulada(setores_por_area)
    st.write(analise)

    buffer = gerar_pdf(analise)
    st.download_button("📥 Baixar PDF da Análise", data=buffer, file_name="analise_rehsult.pdf")
