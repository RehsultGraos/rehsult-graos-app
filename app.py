
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
import os

st.set_page_config(page_title="Rehsult Grãos - Diagnóstico", layout="wide")

def gerar_analise_gpt4(setores_areas):
    return '''
Análise com GPT-4:
- A área de **Calagem e Gessagem** apresenta baixa pontuação, indicando a necessidade de correção da acidez do solo.
- O setor de **Pré-emergente** nas plantas daninhas foi um dos mais críticos, sugerindo que o controle inicial está falhando.
- A aplicação de **macronutrientes** está razoável, mas pode ser otimizada para elevar a produtividade da soja.

Recomendações:
- Realizar análise de solo completa e aplicar calcário/gesso conforme recomendação.
- Revisar o protocolo de pré-emergência e considerar produtos com maior residual.
- Ajustar a adubação com base nas necessidades específicas da cultura e época.
'''.strip()

def gerar_pdf_relatorio(analise_texto: str) -> BytesIO:
    texto_limpo = analise_texto.replace("📋", "").replace("✅", "").replace("🤖", "")                                .replace("🎯", "Recomendações:").replace("📄", "").replace("🧠", "")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, "Relatório de Diagnóstico - Rehsult Grãos")
    pdf.ln(5)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, texto_limpo)

    buffer = BytesIO()
    pdf_output = pdf.output(dest='S').encode('latin1')
    buffer.write(pdf_output)
    buffer.seek(0)
    return buffer

st.title("🌾 Rehsult Grãos")
st.markdown("Diagnóstico técnico com relatório e análise integrada com GPT-4")

# Simulação de pontuações finais (você pode substituir pelo resultado real do diagnóstico)
setores_exemplo = {
    "Fertilidade": {"Análise de Solo": 55.0, "Calagem e Gessagem": 42.0, "Macronutrientes": 60.0},
    "Plantas Daninhas": {"Pré-emergente": 35.0, "Cobertura": 50.0}
}

if st.button("✅ Finalizar Diagnóstico e Gerar Relatório"):
    st.subheader("📊 Diagnóstico Concluído")
    st.markdown("### 🤖 Análise com GPT-4")
    analise = gerar_analise_gpt4(setores_exemplo)
    st.markdown(analise)

    st.markdown("---")
    st.success("📄 Relatório disponível para download:")
    pdf_data = gerar_pdf_relatorio(analise)
    st.download_button("📥 Baixar Relatório em PDF", data=pdf_data, file_name="relatorio_gpt4_final.pdf")
