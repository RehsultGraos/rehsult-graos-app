
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="Rehsult Grãos - Diagnóstico", layout="centered")

if "inicio" not in st.session_state:
    st.session_state.inicio = False
if "respostas" not in st.session_state:
    st.session_state.respostas = {}
    st.session_state.pergunta_atual = None
    st.session_state.fim = False

if not st.session_state.inicio:
    st.image("LOGO REAGRO TRATADA.png", width=200)
    st.title("🌾 Rehsult Grãos - Diagnóstico de Fazenda")
    st.markdown("Este é um sistema de diagnóstico para fazendas produtoras de grãos. Escolha a área que deseja avaliar.")
    
    st.text_input("Nome da Fazenda", key="fazenda")
    st.text_input("Nome do Responsável", key="responsavel")
    st.number_input("Produtividade média de SOJA (kg/ha)", min_value=0, key="prod_soja")
    st.number_input("Produtividade média de MILHO (kg/ha)", min_value=0, key="prod_milho")
    st.session_state.area_escolhida = st.radio("Qual área deseja avaliar?", ["Fertilidade", "Plantas Daninhas"])
    
    if st.button("Iniciar Diagnóstico"):
        st.session_state.inicio = True
        aba_excel = "Fertilidade" if st.session_state.area_escolhida == "Fertilidade" else "Planta Daninha"
        df_inicio = pd.read_excel("Teste Chat.xlsx", sheet_name=aba_excel)
        df_inicio = df_inicio.dropna(subset=["Referência", "Pergunta", "Peso"])
        df_inicio["Referência"] = df_inicio["Referência"].astype(int)
        df_inicio = df_inicio.sort_values("Referência")
        st.session_state.pergunta_atual = int(df_inicio["Referência"].iloc[0])

if st.session_state.inicio and st.session_state.pergunta_atual:
    st.image("LOGO REAGRO TRATADA.png", width=150)

    area = st.session_state.area_escolhida
    aba_excel = "Fertilidade" if area == "Fertilidade" else "Planta Daninha"
    df = pd.read_excel("Teste Chat.xlsx", sheet_name=aba_excel)

    df["Peso"] = pd.to_numeric(df["Peso"], errors="coerce")
    df = df.dropna(subset=["Referência", "Pergunta", "Peso"])
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
                "Peso": dados["Peso"],
                "Resposta": resposta,
                "Certa": dados.get("Resposta", "")
            }

            if resposta == "Sim" and not pd.isna(dados["Sim"]):
                st.session_state.pergunta_atual = int(dados["Sim"])
            elif not pd.isna(dados["Não"]):
                st.session_state.pergunta_atual = int(dados["Não"])
            else:
                st.session_state.fim = True
    else:
        st.session_state.fim = True

if st.session_state.fim and st.session_state.inicio:
    st.markdown("## ✅ Diagnóstico Concluído")
    df_resultado = pd.DataFrame(st.session_state.respostas).T

    if df_resultado.empty:
        st.warning("Nenhuma pergunta foi respondida. Por favor, complete o diagnóstico.")
        st.stop()

    mapa = {"Sim": 1, "Não": 0, "Não sei": 0.5}
    df_resultado["Score"] = df_resultado["Resposta"].map(mapa) * df_resultado["Peso"]

    setores = df_resultado.groupby("Setor").agg({"Score": "sum", "Peso": "sum"})
    setores["Percentual"] = (setores["Score"] / setores["Peso"]) * 100
    nota_area = (df_resultado["Score"].sum() / df_resultado["Peso"].sum()) * 100
    st.markdown(f"### Pontuação na área de {st.session_state.area_escolhida}: **{nota_area:.1f}%**")

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
    ax.set_title(f"Desempenho - {st.session_state.area_escolhida}")
    st.pyplot(fig)

    pior_setores = setores.sort_values("Percentual").head(3)
    st.markdown("### Tópicos a Melhorar:")
    for setor, linha in pior_setores.iterrows():
        st.write(f"- {setor}: {linha['Percentual']:.1f}%")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "Relatório de Diagnóstico - Rehsult Grãos", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Fazenda: {st.session_state.get('fazenda', 'NÃO INFORMADO')}", ln=True)
    pdf.cell(200, 10, f"Responsável: {st.session_state.get('responsavel', 'NÃO INFORMADO')}", ln=True)
    pdf.cell(200, 10, f"Área Avaliada: {st.session_state.area_escolhida}", ln=True)
    pdf.cell(200, 10, f"Produtividade média SOJA: {st.session_state.get('prod_soja', 0)} kg/ha", ln=True)
    pdf.cell(200, 10, f"Produtividade média MILHO: {st.session_state.get('prod_milho', 0)} kg/ha", ln=True)
    pdf.cell(200, 10, f"Pontuação Geral da Área: {nota_area:.1f}%", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, "Desempenho por Setor:", ln=True)
    for setor, linha in setores.iterrows():
        pdf.cell(200, 10, f"- {setor}: {linha['Percentual']:.1f}%", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, "Tópicos a Melhorar:", ln=True)
    for setor, linha in pior_setores.iterrows():
        pdf.cell(200, 10, f"- {setor}: {linha['Percentual']:.1f}%", ln=True)

    pdf_buffer = BytesIO()
    pdf_buffer.write(pdf.output(dest='S').encode('latin1'))
    pdf_buffer.seek(0)

    st.download_button("📄 Baixar Relatório em PDF", data=pdf_buffer.getvalue(), file_name=f"relatorio_{area.lower().replace(' ', '_')}.pdf", mime="application/pdf")
