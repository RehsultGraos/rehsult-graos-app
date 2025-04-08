
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

st.set_page_config(page_title="Rehsult Grãos", layout="centered")

# Função para gerar PDF
def gerar_pdf(analise, setores_areas):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Diagnóstico Rehsult Grãos", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt="Análise com GPT-4 (simulada):", ln=True)
    pdf.multi_cell(0, 10, analise)
    pdf.ln(10)

    for area, setores in setores_areas.items():
        pdf.cell(200, 10, txt=f"{area}:", ln=True)
        for setor, score in setores.items():
            pdf.cell(200, 10, txt=f"- {setor}: {score:.1f}%", ln=True)
        pdf.ln(5)

    output_path = "/mnt/data/app_final_rehsultgraos.py"
    pdf.output("/mnt/data/diagnostico_completo_corrigido.pdf")
    return output_path

# Interface para simular conclusão do diagnóstico
st.title("🌱 Rehsult Grãos")
st.subheader("Diagnóstico de fazendas produtoras de grãos com análise simulada GPT-4")

if st.button("Simular Diagnóstico"):
    analise = (
        "A área de Pré-emergente em Plantas Daninhas apresenta baixa pontuação, indicando atenção.
"
        "A área de Cobertura em Plantas Daninhas está razoável, mas pode melhorar.
"
        "A área de Pós-emergente em Plantas Daninhas está com boa pontuação.
"
        "A área de Análise de Solo em Fertilidade apresenta baixa pontuação, indicando atenção.
"
        "A área de Calagem e Gessagem em Fertilidade está razoável, mas pode melhorar.
"
        "A área de Macronutrientes em Fertilidade está com boa pontuação.

"
        "🎯 Recomendações:

"
        "- Realizar análise de solo completa e aplicar calcário/gesso conforme recomendação.
"
        "- Revisar o protocolo de pré-emergência e considerar produtos com maior residual.
"
        "- Otimizar aplicação de cobertura para alcançar maior eficiência.
"
        "- Manter o bom trabalho nos setores que estão com pontuação alta."
    )

    setores_areas = {
        "Plantas Daninhas": {
            "Pré-emergente": 35.0,
            "Cobertura": 60.0,
            "Pós-emergente": 80.0
        },
        "Fertilidade": {
            "Análise de Solo": 40.0,
            "Calagem e Gessagem": 60.0,
            "Macronutrientes": 85.0
        }
    }

    pdf_path = gerar_pdf(analise, setores_areas)
    st.success("✅ Diagnóstico concluído com sucesso.")
    st.download_button(label="📄 Baixar Relatório PDF", data=open("/mnt/data/diagnostico_completo_corrigido.pdf", "rb"), file_name="diagnostico_completo.pdf")

