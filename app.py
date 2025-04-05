import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="Rehsult Grãos - Diagnóstico", layout="centered")
st.title("🌾 Rehsult Grãos - Diagnóstico de Fazenda")
st.image("LOGO REAGRO TRATADA.png", width=150)

@st.cache_data
def carregar_dados():
    df = pd.read_excel("Teste Chat.xlsx", sheet_name=None)
    perguntas_df = df['Fertilidade']
    setores_df = perguntas_df[['Setor', 'Peso']].dropna().drop_duplicates()
    return perguntas_df, setores_df

perguntas_df, setores_df = carregar_dados()

if 'respostas' not in st.session_state:
    st.session_state.respostas = {}
if 'indice_pergunta' not in st.session_state:
    st.session_state.indice_pergunta = 0

if 'fazenda' not in st.session_state:
    st.session_state.fazenda = ''
if 'responsavel' not in st.session_state:
    st.session_state.responsavel = ''

if st.session_state.indice_pergunta == 0:
    st.session_state.fazenda = st.text_input("Nome da Fazenda")
    st.session_state.responsavel = st.text_input("Nome do Responsável")
    if st.button("Iniciar Diagnóstico"):
        st.session_state.indice_pergunta += 1
    st.stop()

perguntas_validas = perguntas_df.dropna(subset=['Pergunta']).reset_index(drop=True)

if st.session_state.indice_pergunta <= len(perguntas_validas):
    linha = perguntas_validas.iloc[st.session_state.indice_pergunta - 1]
    pergunta = linha['Pergunta']
    chave = f"pergunta_{st.session_state.indice_pergunta}"
    resposta = st.radio(pergunta, ["Sim", "Não", "Não sei"], key=chave)
    if st.button("Responder"):
        st.session_state.respostas[linha['ID']] = resposta
        st.session_state.indice_pergunta += 1
        st.experimental_rerun()
else:
    st.success("Diagnóstico finalizado!")

    notas = []
    for _, linha in perguntas_validas.iterrows():
        resposta = st.session_state.respostas.get(linha['ID'])
        peso = linha['Peso']
        if resposta == "Sim":
            nota = peso
        elif resposta == "Não":
            nota = 0
        else:
            nota = 0
        notas.append((linha['Setor'], nota))

    df_resultado = pd.DataFrame(notas, columns=["Setor", "Nota"])
    df_agrupado = df_resultado.groupby("Setor").agg({'Nota': 'sum'}).reset_index()
    setores_com_peso = setores_df.set_index('Setor')['Peso']
    df_agrupado["Peso Total"] = df_agrupado["Setor"].map(setores_com_peso)
    df_agrupado["Percentual"] = (df_agrupado["Nota"] / df_agrupado["Peso Total"]) * 100

    st.subheader("📊 Resultado por Setor")
    st.dataframe(df_agrupado)

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    categorias = df_agrupado["Setor"]
    valores = df_agrupado["Percentual"]
    valores = np.append(valores, valores[0])
    angulos = np.linspace(0, 2 * np.pi, len(categorias), endpoint=False)
    angulos = np.append(angulos, angulos[0])
    ax.plot(angulos, valores, 'green', linewidth=2)
    ax.fill(angulos, valores, 'green', alpha=0.25)
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(categorias)
    ax.set_yticklabels([])
    ax.set_title("Desempenho por Setor")
    st.pyplot(fig)

    # Gerar PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "Relatório de Diagnóstico - Rehsult Grãos", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Fazenda: {st.session_state.fazenda}", ln=True)
    pdf.cell(200, 10, f"Responsável: {st.session_state.responsavel}", ln=True)
    pdf.ln(10)
    nota_geral = df_agrupado['Percentual'].mean()
    pdf.cell(200, 10, f"Pontuação Geral da Fazenda: {nota_geral:.0f}/100", ln=True)
    pdf.ln(10)
    for _, linha in df_agrupado.iterrows():
        pdf.cell(200, 10, f"- {linha['Setor']}: {linha['Percentual']:.0f}/100", ln=True)

    pdf_buffer = BytesIO()
    pdf.output(pdf_buffer, 'F')
    st.download_button("📄 Baixar Relatório em PDF", data=pdf_buffer.getvalue(), file_name="relatorio_rehsult.pdf")