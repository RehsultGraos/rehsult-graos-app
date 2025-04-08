
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF

# Carrega os dados
df = pd.read_excel("Teste Chat.xlsx")

# Inicialização do estado
if "pergunta_id" not in st.session_state:
    st.session_state.pergunta_id = df.iloc[0]["Referência"]
    st.session_state.respostas = {}
    st.session_state.encerrar = False

# Função para verificar dependência
def verificar_vinculo(linha):
    if pd.notna(linha["Vínculo"]):
        ref_dependente = int(linha["Vínculo"])
        resposta_dependente = st.session_state.respostas.get(ref_dependente, (None,))[1]
        return resposta_dependente == "Sim"
    return True

# Layout
st.image("LOGO REAGRO TRATADA.png", width=150)
st.title("🌱 Rehsult Grãos")
st.caption("Diagnóstico de fazendas produtoras de grãos com análise simulada GPT-4")

if not st.session_state.encerrar:
    linha = df[df["Referência"] == st.session_state.pergunta_id].iloc[0]

    if not verificar_vinculo(linha):
        st.session_state.pergunta_id = int(linha["Sim"]) if pd.notna(linha["Sim"]) else None
        st.rerun()

    st.subheader(f"**{linha['Setor']}**")
    st.write(f"📌 {linha['Pergunta']}")
    resposta = st.radio("Escolha sua resposta:", ["Sim", "Não", "Não sei"])

    if st.button("Responder"):
        area = linha["Área"]
        st.session_state.respostas.setdefault(area, []).append(
            (linha["Referência"], resposta, linha["Peso"], linha["Setor"], linha["Resposta"])
        )
        proxima = linha["Sim"] if resposta == "Sim" else linha["Não"]
        st.session_state.pergunta_id = int(proxima) if pd.notna(proxima) else None
        if st.session_state.pergunta_id is None:
            st.session_state.encerrar = True
        st.rerun()
else:
    st.success("✅ Diagnóstico parcial concluído.")
    setores_areas = {}

    for respostas in st.session_state.respostas.values():
        for ref, resposta, peso, setor, correta in respostas:
            if setor not in setores_areas:
                setores_areas[setor] = 0
            if str(resposta).strip().lower() == str(correta).strip().lower():
                setores_areas[setor] += peso

    total = sum(setores_areas.values())
    st.write("### 📊 Resultados por Setor")
    for setor, score in setores_areas.items():
        st.write(f"- **{setor}**: {score:.1f} pontos")

    # Análise simulada
    analise = ""
    for setor, score in setores_areas.items():
        if score < 2:
            analise += f"O setor {setor} apresenta baixa pontuação.
"
        elif score < 4:
            analise += f"O setor {setor} está razoável, pode melhorar.
"
        else:
            analise += f"O setor {setor} está com bom desempenho.
"

    st.subheader("🤖 Análise com GPT-4 (simulada)")
    st.text(analise)

    # PDF
    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 12)
            self.cell(0, 10, "Relatório do Diagnóstico - Rehsult Grãos", ln=True, align="C")

    def gerar_pdf(analise, setores):
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, "Análise com GPT-4 (simulada):\n" + analise)
        for setor, score in setores.items():
            pdf.cell(0, 10, f"{setor}: {score:.1f} pontos", ln=True)
        output_path = "/mnt/data/diagnostico_completo_corrigido.pdf"
        pdf.output(output_path)
        return output_path

    if st.button("📥 Baixar Relatório PDF"):
        path = gerar_pdf(analise, setores_areas)
        with open(path, "rb") as f:
            st.download_button("📄 Download PDF", f, file_name="diagnostico_resultado.pdf")
