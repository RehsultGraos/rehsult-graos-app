
import streamlit as st
import pandas as pd
from fpdf import FPDF

def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, "Análise com GPT-4 (simulada):")
    pdf.multi_cell(0, 10, "A análise mostra bom desempenho nos setores avaliados.")
    output_path = "/mnt/data/diagnostico_corrigido.pdf"
    pdf.output(output_path)
    return output_path

st.title("Rehsult Grãos")
st.markdown("Diagnóstico com GPT-4 (simulada)")

if st.button("Gerar PDF"):
    path = gerar_pdf()
    with open(path, "rb") as file:
        st.download_button("📄 Baixar PDF do Diagnóstico", file, file_name="diagnostico_corrigido.pdf")
