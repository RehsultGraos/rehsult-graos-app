
import streamlit as st
from fpdf import FPDF

# Simulação da análise
analise = "• Setor 1: Bom desempenho\n• Setor 2: Atenção\n• Setor 3: Melhorar"

# Criar PDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.multi_cell(0, 10, "🤖 Análise com GPT-4 (simulada):\n" + analise.replace("•", "-"))
pdf.output("/mnt/data/diagnostico_completo.pdf")

st.image("LOGO REAGRO TRATADA.png", width=200)
st.title("🌱 Rehsult Grãos")
st.markdown("Diagnóstico de fazendas produtoras de grãos com análise simulada GPT-4")
st.success("✅ Diagnóstico Concluído")
st.markdown("### 🤖 Análise com GPT-4 (simulada)")
st.markdown(analise)

with open("/mnt/data/diagnostico_completo.pdf", "rb") as f:
    st.download_button("📥 Baixar Diagnóstico em PDF", f, file_name="diagnostico.pdf")
