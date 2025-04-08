
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font("DejaVu", "", 12)
        self.cell(0, 10, "Relatório do Diagnóstico - Rehsult Grãos", ln=True, align="C")

def limpar(texto):
    try:
        return texto.encode('latin-1', 'ignore').decode('latin-1').strip()
    except:
        return "Erro ao processar texto para PDF."

def gerar_pdf(analise, setores, dados_iniciais):
    pdf = PDF()
    pdf.add_page()
    pdf.add_font("DejaVu", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", "", 12)

    pdf.cell(0, 10, f"Fazenda: {dados_iniciais.get('Fazenda', '-')}", ln=True)
    pdf.cell(0, 10, f"Produtividade Soja: {dados_iniciais.get('Produtividade Soja', '-')}", ln=True)
    pdf.cell(0, 10, f"Produtividade Milho: {dados_iniciais.get('Produtividade Milho', '-')}", ln=True)

    pdf.ln(10)
    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 10, "Análise com GPT-4 (Simulada):", ln=True)
    pdf.set_font("DejaVu", "", 12)

    for linha in analise.split("\n"):
        pdf.multi_cell(0, 10, limpar(linha))

    pdf.ln(5)
    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 10, "Pontuação por Setor:", ln=True)
    pdf.set_font("DejaVu", "", 12)
    for setor, score in setores.items():
        pdf.cell(0, 10, f"{setor}: {score:.1f} pontos", ln=True)

    output_path = "/mnt/data/diagnostico_corrigido_final.pdf"
    pdf.output(output_path)
    return output_path
