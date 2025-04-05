
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="Rehsult Grãos - Diagnóstico", layout="centered")
st.title("🌾 Rehsult Grãos - Diagnóstico de Fazenda")
st.image("logo_rehagro.png", width=150)

@st.cache_data
def carregar_dados():
    df = pd.read_excel("Teste Chat.xlsx", sheet_name=None)
    fertilidade_df = df['Fertilidade']
    daninhas_df = df['Planta Daninha']
    fertilidade_df['Área'] = 'Fertilidade'
    daninhas_df['Área'] = 'Planta Daninha'
    perguntas_df = pd.concat([fertilidade_df, daninhas_df], ignore_index=True)
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
    st.session_state.soja = st.number_input("Produtividade da última safra de soja (sc/ha)", min_value=0.0, step=1.0)
    st.session_state.milho = st.number_input("Produtividade da última safra de milho (sc/ha)", min_value=0.0, step=1.0)
    if st.button("Iniciar Diagnóstico"):
        st.session_state.etapa = 'perguntas'
        st.session_state.indice = 0
        st.rerun()

if st.session_state.etapa == 'perguntas':
    perguntas_validas = perguntas_df.dropna(subset=['Pergunta'])
    indice = st.session_state.indice

    if indice < len(perguntas_validas):
        pergunta = perguntas_validas.iloc[indice]
        st.write(f"**{pergunta['Pergunta']}**")
        resposta = st.radio("Resposta:", ['Sim', 'Não', 'Não sei'], key=f"resposta_{indice}")
        if st.button("Responder", key=f"botao_{indice}"):
            st.session_state.respostas[pergunta['ID']] = resposta
            st.session_state.indice += 1
            st.rerun()
    else:
        st.session_state.etapa = 'resultado'
        st.rerun()

if st.session_state.etapa == 'resultado':
    respostas = st.session_state.respostas
    perguntas_df['Respondida'] = perguntas_df['ID'].apply(lambda x: x in respostas)
    perguntas_df['Valor'] = perguntas_df['ID'].apply(lambda x: respostas.get(x, ''))
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

    def classificar_produtividade(valor, cultura):
        if cultura == "soja":
            if valor < 65:
                return "Baixa"
            elif valor <= 75:
                return "Média"
            elif valor <= 90:
                return "Alta"
            else:
                return "Muito Alta"
        elif cultura == "milho":
            if valor < 170:
                return "Baixa"
            elif valor <= 190:
                return "Média"
            elif valor <= 205:
                return "Alta"
            else:
                return "Muito Alta"

    soja_txt = classificar_produtividade(st.session_state.soja, "soja")
    milho_txt = classificar_produtividade(st.session_state.milho, "milho")
    st.write(f"Produtividade da Soja: {st.session_state.soja} sc/ha - {soja_txt}")
    st.write(f"Produtividade do Milho: {st.session_state.milho} sc/ha - {milho_txt}")

    # Radar
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    categorias = setores.index.tolist()
    valores = setores['Pontuacao'].tolist()
    categorias += [categorias[0]]
    valores += [valores[0]]
    angulos = np.linspace(0, 2 * np.pi, len(categorias))
    ax.plot(angulos, valores)
    ax.fill(angulos, valores, alpha=0.25)
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(categorias, fontsize=8)
    ax.set_title("Desempenho por Setor")
    st.pyplot(fig)

    st.markdown("### Sugestões por IA")
    for i, row in setores.iterrows():
        if row['Pontuacao'] < 60:
            st.markdown(f"- O setor **{i}** teve desempenho abaixo do esperado. Avalie as práticas adotadas e oportunidades de melhoria.")
