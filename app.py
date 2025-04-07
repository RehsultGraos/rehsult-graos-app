
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="Rehsult Grãos - Diagnóstico", layout="centered")

# Iniciar variáveis de controle
if "inicio" not in st.session_state:
    st.session_state.inicio = False
if "respostas" not in st.session_state:
    st.session_state.respostas = {}
    st.session_state.pergunta_atual = 1
    st.session_state.fim = False

# Cabeçalho e entrada de dados só se ainda não começou
if not st.session_state.inicio:
    st.image("LOGO REAGRO TRATADA.png", width=200)
    st.title("🌾 Rehsult Grãos - Diagnóstico de Fazenda")
    st.markdown("""
    **Bem-vindo ao Rehsult Grãos!**

    Este é um sistema de diagnóstico para fazendas produtoras de grãos. Você responderá uma pergunta por vez, e ao final, verá um relatório com pontuação geral, gráfico de radar e recomendações.
    """)
    st.text_input("Nome da Fazenda", key="fazenda")
    st.text_input("Nome do Responsável", key="responsavel")
    if st.button("Iniciar Diagnóstico"):
        st.session_state.inicio = True

# Diagnóstico após clique
if st.session_state.inicio:
    st.image("LOGO REAGRO TRATADA.png", width=150)

    df_fert = pd.read_excel("Teste Chat.xlsx", sheet_name="Fertilidade")
    df_planta = pd.read_excel("Teste Chat.xlsx", sheet_name="Planta Daninha")
    df = pd.concat([df_fert, df_planta], ignore_index=True)
    df["Nota"] = pd.to_numeric(df["Nota"], errors="coerce")
    df = df.dropna(subset=["Referência", "Pergunta", "Nota"])
    df["Referência"] = df["Referência"].astype(int)
    perguntas_dict = df.set_index("Referência").to_dict(orient="index")

    ref = st.session_state.pergunta_atual
    if not st.session_state.fim and ref in perguntas_dict:
        dados = perguntas_dict[ref]
        resposta = st.radio(dados["Pergunta"], ["Sim", "Não", "Não sei"], key=f"ref_{ref}")
        if st.button("Responder", key=f"btn_{ref}"):
            st.session_state.respostas[ref] = {
                "Setor": dados["Setor"],
                "Área": dados["Área"],
                "Pergunta": dados["Pergunta"],
                "Nota": dados["Nota"],
                "Resposta": resposta
            }
            if resposta == "Sim" and not pd.isna(dados["Sim"]):
                st.session_state.pergunta_atual = int(dados["Sim"])
            elif not pd.isna(dados["Não"]):
                st.session_state.pergunta_atual = int(dados["Não"])
            else:
                st.session_state.fim = True
    else:
        st.session_state.fim = True

# Finalização do diagnóstico
if st.session_state.fim and st.session_state.inicio:
    st.markdown("## ✅ Diagnóstico Concluído")
    df_resultado = pd.DataFrame(st.session_state.respostas).T
    mapa = {"Sim": 1, "Não": 0, "Não sei": 0.5}
    df_resultado["Score"] = df_resultado["Resposta"].map(mapa) * df_resultado["Nota"]

    setores = df_resultado.groupby("Setor").agg({"Score": "sum", "Nota": "sum"})
    setores["Percentual"] = (setores["Score"] / setores["Nota"]) * 100
    nota_geral = (df_resultado["Score"].sum() / df_resultado["Nota"].sum()) * 100
    st.markdown(f"### Pontuação Geral da Fazenda: **{nota_geral:.1f}%**")

    labels = setores.index.tolist()
    valores = setores["Percentual"].tolist()
    valores += valores[:1]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))
    ax.plot(angles, valores, color='green')
    ax.fill(angles, valores, color='green', alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_title("Desempenho por Setor")
    st.pyplot(fig)

    st.markdown("### Tópicos a Melhorar:")
    pior_setores = setores.sort_values("Percentual").head(3)
    for setor, linha in pior_setores.iterrows():
        st.write(f"- {setor}: {linha['Percentual']:.1f}%")

    # PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.image("LOGO REAGRO TRATADA.png", x=70, y=10, w=70)
    pdf.set_xy(10, 40)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "Relatório de Diagnóstico - Rehsult Grãos", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.ln(5)
    fazenda = st.session_state.get("fazenda", "NÃO INFORMADO")
    pdf.cell(200, 10, f"Fazenda: {fazenda}", ln=True)
    responsavel = st.session_state.get("responsavel", "NÃO INFORMADO")
    pdf.cell(200, 10, f"Responsável: {responsavel}", ln=True)
    pdf.cell(200, 10, f"Pontuação Geral: {nota_geral:.1f}%", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Desempenho por Setor:", ln=True)
    pdf.set_font("Arial", "", 12)
    for setor, linha in setores.iterrows():
        pdf.cell(200, 10, f"- {setor}: {linha['Percentual']:.1f}%", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Tópicos a Melhorar:", ln=True)
    pdf.set_font("Arial", "", 12)
    for setor, linha in pior_setores.iterrows():
        pdf.cell(200, 10, f"- {setor}: {linha['Percentual']:.1f}%", ln=True)

    pdf_buffer = BytesIO()
    pdf.output(pdf_buffer)
    st.download_button("📄 Baixar Relatório em PDF", data=pdf_buffer.getvalue(), file_name="relatorio_rehsult_graos.pdf", mime="application/pdf")
