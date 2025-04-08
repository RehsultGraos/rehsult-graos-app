
import streamlit as st
import pandas as pd
from fpdf import FPDF

# Função para gerar PDF sem emojis
def gerar_pdf(analise, setores_areas):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(0, 10, "Analise com GPT-4 (simulada)", ln=True)
    pdf.multi_cell(0, 10, analise.replace("🤖", "").replace("✅", "").replace("🎯", "").replace("🌱", "").strip())

    for area, setores in setores_areas.items():
        pdf.ln(5)
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(0, 10, f"{area}", ln=True)
        pdf.set_font("Arial", size=12)
        for setor, score in setores.items():
            pdf.cell(0, 10, f"{setor}: {score:.1f}%", ln=True)

    pdf_output_path = "/mnt/data/diagnostico_completo.pdf"
    pdf.output(pdf_output_path)
    return pdf_output_path

# Simulação dos dados (exemplo)
st.image("LOGO REAGRO TRATADA.png", width=200)
st.title("🌱 Rehsult Grãos")
st.markdown("Diagnóstico de fazendas produtoras de grãos com análise simulada GPT-4")

if st.button("Gerar Diagnóstico"):
    setores_areas = {
        "Fertilidade": {
            "Calagem e Gessagem": 60.0,
            "Macronutrientes": 80.0
        },
        "Plantas Daninhas": {
            "Pré-emergente": 40.0,
            "Cobertura": 70.0
        }
    }

    analise = '''
🤖 **Análise com GPT-4 (simulada)**

✅ **Análise Simulada:**

- A área de **Calagem e Gessagem** apresenta pontuação intermediária, indicando atenção.
- A área de **Macronutrientes** está com bom desempenho.
- O setor **Pré-emergente** apresenta baixo desempenho, exige correções.
- O setor **Cobertura** está com desempenho razoável.

🎯 **Recomendações**:

- Corrigir acidez do solo e aplicar nutrientes conforme análise.
- Reavaliar o controle inicial de plantas daninhas.
'''

    st.markdown(analise, unsafe_allow_html=True)
    pdf_path = gerar_pdf(analise, setores_areas)
    with open(pdf_path, "rb") as f:
        st.download_button("📥 Baixar PDF do Diagnóstico", f, file_name="diagnostico_completo.pdf")
