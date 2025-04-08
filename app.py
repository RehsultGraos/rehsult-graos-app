
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

# Carrega a planilha e limpa nomes de colunas
df = pd.read_excel("Teste Chat.xlsx")
df.columns = df.columns.str.strip()  # Remove espaços extras

# Inicialização de estados
if "pergunta_id" not in st.session_state:
    st.session_state.pergunta_id = df.iloc[0]["Referência"]
    st.session_state.respostas = {}
    st.session_state.encerrar = False

# Função para gerar PDF
def gerar_pdf(analise, setores):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("DejaVu", '', "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", size=12)
    pdf.multi_cell(0, 10, "Análise com GPT-4 (simulada):\n")
    pdf.multi_cell(0, 10, analise)
    output_path = "/mnt/data/diagnostico_corrigido.pdf"
    pdf.output(output_path)
    return output_path

st.image("LOGO REAGRO TRATADA.png", width=150)
st.title("Rehsult Grãos")
st.caption("Diagnóstico de fazendas produtoras de grãos com análise simulada GPT-4")

if not st.session_state.encerrar:
    linha_df = df[df["Referência"] == st.session_state.pergunta_id]
    if not linha_df.empty:
        linha = linha_df.iloc[0]

        # Verifica vínculo condicional
        if "Vínculo" in linha and pd.notna(linha["Vínculo"]):
            ref_dependente = int(linha["Vínculo"])
            resposta_dependente = st.session_state.respostas.get(ref_dependente, {}).get("Resposta")
            if resposta_dependente != "Sim":
                st.session_state.pergunta_id = int(linha["Sim"])
                st.rerun()

        st.subheader(f"{linha['Setor']} - {linha['Pergunta']}")
        resposta = st.radio("Selecione a resposta:", ["Sim", "Não", "Não sei"])

        if st.button("Responder"):
            area = linha["Área"]
            st.session_state.respostas.setdefault(area, []).append((
                linha["Referência"],
                resposta,
                linha["Peso"],
                linha["Setor"],
                linha["Resposta"]
            ))
            proxima = linha["Sim"] if resposta == "Sim" else linha["Não"]
            if pd.isna(proxima):
                st.session_state.encerrar = True
            else:
                st.session_state.pergunta_id = int(proxima)
            st.rerun()
else:
    st.success("Diagnóstico parcial concluído.")

    resultados = []
    for area, respostas in st.session_state.respostas.items():
        for ref, resposta, peso, setor, correta in respostas:
            score = peso if str(resposta).strip() == str(correta).strip() else 0
            resultados.append({"Área": area, "Setor": setor, "Score": score})

    df_resultado = pd.DataFrame(resultados)
    setores = df_resultado.groupby("Setor")["Score"].sum().to_dict()

    st.write("### Resultados por Setor")
    for setor, score in setores.items():
        st.write(f"- **{setor}**: {score:.1f} pontos")

    # Análise Simulada
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

    # PDF
    if st.button("Baixar Relatório PDF"):
        path = gerar_pdf(analise, setores)
        with open(path, "rb") as f:
            st.download_button("Download PDF", f, file_name="diagnostico_resultado.pdf")
