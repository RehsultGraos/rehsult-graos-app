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
    fertilidade_df = df['Fertilidade']
    fertilidade_df['Área'] = 'Fertilidade'
    perguntas_df = fertilidade_df.copy()
    setores_df = perguntas_df.iloc[:, [1, 7]].copy()
    setores_df.columns = ['Setor', 'Peso']
    setores_df = setores_df.dropna().drop_duplicates()
    return perguntas_df, setores_df

perguntas_df, setores_df = carregar_dados()

if 'etapa' not in st.session_state:
    st.session_state.etapa = 'inicio'
if 'respostas' not in st.session_state:
    st.session_state.respostas = {}

if st.session_state.etapa == 'inicio':
    st.session_state.fazenda = st.text_input("Nome da Fazenda")
    st.session_state.responsavel = st.text_input("Nome do Responsável")
    if st.button("Iniciar Diagnóstico"):
        st.session_state.etapa = 'perguntas'
        st.session_state.indice = 0
        st.rerun()

if st.session_state.etapa == 'perguntas':
    perguntas_validas = perguntas_df.dropna(subset=['Pergunta'])
    indice = st.session_state.indice

    if indice < len(perguntas_validas):
        linha = perguntas_validas.iloc[indice]
        pergunta = linha['Pergunta']
        resposta = st.radio(f"{pergunta}", ['Sim', 'Não', 'Não sei'], key=f"resposta_{indice}")
        if st.button("Responder", key=f"botao_{indice}"):
            st.session_state.respostas[indice] = resposta
            st.session_state.indice += 1
            st.rerun()
    else:
        st.session_state.etapa = 'resultado'
        st.rerun()

if st.session_state.etapa == 'resultado':
    respostas = st.session_state.respostas
    perguntas_df['Respondida'] = perguntas_df.index.to_series().apply(lambda x: x in respostas)
    perguntas_df['Valor'] = perguntas_df.index.to_series().apply(lambda x: respostas.get(x, ''))
    perguntas_df['Nota obtida'] = perguntas_df.apply(
        lambda row: row['Nota'] if row['Valor'] == 'Sim' else 0, axis=1
    )

    setores = perguntas_df.groupby('Setor').agg({'Nota obtida': 'sum', 'Nota': 'sum', 'Respondida': 'sum'})
    setores = setores[setores['Respondida'] > 0]
    setores['Pontuacao'] = (setores['Nota obtida'] / setores['Nota'] * 100).round(0)

    nota_geral = (perguntas_df['Nota obtida'].sum() / perguntas_df['Nota'].sum()) * 100
    nota_geral = round(nota_geral)

    st.subheader("Resultado do Diagnóstico")
    st.markdown(f"**Pontuação Geral da Fazenda:** {nota_geral}/100")

    # Radar
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    categorias = setores.index.tolist()
    valores = setores['Pontuacao'].tolist()
    categorias_plot = categorias + [categorias[0]]
    valores = valores + [valores[0]]
    angulos = np.linspace(0, 2 * np.pi, len(categorias_plot))
    ax.plot(angulos, valores)
    ax.fill(angulos, valores, alpha=0.25)
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(categorias, fontsize=8)
    ax.set_title("Desempenho por Setor")
    st.pyplot(fig)

    # Sugestões por IA simples com base em setores abaixo de 60
    st.markdown("### Sugestões por IA")
    for i, row in setores.iterrows():
        if row['Pontuacao'] < 60:
            st.markdown(f"- O setor **{i}** teve pontuação de {int(row['Pontuacao'])}/100. Avalie práticas, dados e processos para identificar os principais gargalos.")