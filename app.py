
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF

# Função para gerar PDF corrigida
def gerar_pdf(analise, setores):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("DejaVu", '', "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", size=12)
    pdf.multi_cell(0, 10, "Análise com GPT-4 (simulada):\n")
    pdf.multi_cell(0, 10, analise)
    output_path = "/mnt/data/diagnostico_completo_corrigido.pdf"
    pdf.output(output_path)
    return output_path

# Carregamento da planilha
df = pd.read_excel("Teste Chat.xlsx")

# Inicializa o estado da aplicação
if "pergunta_id" not in st.session_state:
    st.session_state.pergunta_id = df.iloc[0]["Referência"]
    st.session_state.respostas = {}
    st.session_state.area_atual = df.iloc[0]["Área"]
    st.session_state.encerrar = False

# Interface
st.image("LOGO REAGRO TRATADA.png", width=150)
st.title("Rehsult Grãos")
st.caption("Diagnóstico de fazendas produtoras de grãos com análise simulada GPT-4")

if not st.session_state.encerrar:
    linha = df[df["Referência"] == st.session_state.pergunta_id]

    if not linha.empty:
        linha = linha.iloc[0]

        # Verifica dependência (vínculo)
        if pd.notna(linha["Vínculo"]):
            resposta_vinculo = st.session_state.respostas.get(linha["Vínculo"], [None])[1]
            if resposta_vinculo != "Sim":
                st.session_state.pergunta_id = linha["Sim"]
                st.rerun()

        st.subheader(f"{linha['Setor']} - {linha['Pergunta']}")
        resposta = st.radio("Selecione a resposta:", ["Sim", "Não", "Não sei"])

        if st.button("Responder"):
            area = linha["Área"]
            st.session_state.respostas.setdefault(area, []).append(
                (linha["Referência"], resposta, linha["Peso"], linha["Setor"], linha["Resposta"])
            )
            proxima = linha["Sim"] if resposta == "Sim" else linha["Não"]
            if pd.isna(proxima):
                st.session_state.encerrar = True
            else:
                st.session_state.pergunta_id = proxima
            st.rerun()
else:
    st.success("Diagnóstico parcial concluído.")
    respostas_df = pd.DataFrame(
        [(area, *r) for area, lista in st.session_state.respostas.items() for r in lista],
        columns=["Área", "Referência", "Resposta", "Peso", "Setor", "Resposta_Correta"]
    )
    respostas_df["Score"] = respostas_df.apply(
        lambda x: x["Peso"] if str(x["Resposta"]).strip() == str(x["Resposta_Correta"]).strip() else 0, axis=1
    )

    setores = respostas_df.groupby("Setor")["Score"].sum().to_dict()
    total = respostas_df["Score"].sum()

    st.write("\n\n### Resultados por Setor")
    for setor, score in setores.items():
        st.write(f"- **{setor}**: {score:.1f} pontos")

    # Análise simulada
    analise = ""
    for setor, score in setores.items():
        if score < 2:
            analise += f"O setor {setor} apresenta baixa pontuação.\n"
        elif score < 4:
            analise += f"O setor {setor} está razoável, pode melhorar.\n"
        else:
            analise += f"O setor {setor} está com bom desempenho.\n"

    st.subheader("Análise com GPT-4 (simulada)")
    st.write(analise)

    # Gerar PDF
    if st.button("Baixar Relatório PDF"):
        path = gerar_pdf(analise, setores)
        with open(path, "rb") as f:
            st.download_button("Download PDF", f, file_name="diagnostico_resultado.pdf")
