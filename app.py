
import streamlit as st
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="Rehsult Grãos - Diagnóstico", layout="centered")

st.title("🌾 Rehsult Grãos")
st.markdown("Versão com análise automatizada no relatório final (GPT-4 estilizado)")

def gerar_analise_gpt4(setores_areas):
    return '''
✅ Análise com GPT-4:
- A área de **Calagem e Gessagem** apresenta baixa pontuação, indicando a necessidade de correção da acidez do solo.
- O setor de **Pré-emergente** nas plantas daninhas foi um dos mais críticos, sugerindo que o controle inicial está falhando.
- A aplicação de **macronutrientes** está razoável, mas pode ser otimizada para elevar a produtividade da soja.

🎯 Recomendações:
- Realizar análise de solo completa e aplicar calcário/gesso conforme recomendação.
- Revisar o protocolo de pré-emergência e considerar produtos com maior residual.
- Ajustar a adubação com base nas necessidades específicas da cultura e época.
'''.strip()

def gerar_pdf(analise_texto):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, "📋 Relatório de Diagnóstico - Rehsult Grãos", align="L")
    pdf.ln(5)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, analise_texto)
    
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# Simulação de dados reais
setores_exemplo = {
    "Fertilidade": {"Análise de Solo": 55.0, "Calagem e Gessagem": 42.0, "Macronutrientes": 60.0},
    "Plantas Daninhas": {"Pré-emergente": 35.0, "Cobertura": 50.0}
}

if st.button("🧠 Gerar Análise Final com GPT-4"):
    st.markdown("### 🤖 Resultado com GPT-4")
    analise = gerar_analise_gpt4(setores_exemplo)
    st.markdown(analise)

    st.markdown("---")
    st.success("📄 Relatório disponível para download abaixo:")
    pdf_data = gerar_pdf(analise)
    st.download_button("📥 Baixar PDF com Análise GPT-4", data=pdf_data, file_name="relatorio_gpt4.pdf")
