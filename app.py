
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="Rehsult Grãos", layout="wide")

# Logo
st.image("LOGO REAGRO TRATADA.png", width=200)

st.title("Rehsult Grãos - Diagnóstico de Fertilidade")
st.write("Este é um sistema de diagnóstico para fazendas produtoras de grãos. Você responderá perguntas e, ao final, verá um relatório com pontuação, gráfico e sugestões.")

@st.cache_data
def carregar_dados():
    df = pd.read_excel("Teste Chat.xlsx", sheet_name="Fertilidade", header=None)
    setores_df = df[[1, 7]].dropna().drop_duplicates()
    return df, setores_df

perguntas_df, setores_df = carregar_dados()

if "respostas" not in st.session_state:
    st.session_state.respostas = {}

if "pergunta_atual" not in st.session_state:
    st.session_state.pergunta_atual = 0

def proxima_pergunta():
    st.session_state.pergunta_atual += 1

# Exibição das perguntas
while st.session_state.pergunta_atual < len(perguntas_df):
    linha = perguntas_df.iloc[st.session_state.pergunta_atual]
    pergunta_id = linha[0]
    pergunta_texto = linha[1]
    setor = linha[2]
    peso = linha[7]

    # Verificar dependência
    if pd.notna(linha[6]):
        id_condicional = int(linha[6])
        if st.session_state.respostas.get(id_condicional) != "Sim":
            st.session_state.pergunta_atual += 1
            continue

    st.subheader(f"{int(pergunta_id)} - {pergunta_texto}")
    resposta = st.radio("Selecione:", ["Sim", "Não", "Não sei"], key=f"pergunta_{pergunta_id}")
    if st.button("Responder", key=f"botao_{pergunta_id}"):
        st.session_state.respostas[pergunta_id] = resposta
        proxima_pergunta()
    st.stop()

# Cálculo das notas
respostas = st.session_state.respostas
notas_setor = {}

for _, linha in perguntas_df.iterrows():
    pergunta_id = linha[0]
    setor = linha[2]
    peso = linha[7]
    resposta = respostas.get(pergunta_id)

    if resposta == "Sim":
        if setor not in notas_setor:
            notas_setor[setor] = {"pontos": 0, "peso_total": 0}
        notas_setor[setor]["pontos"] += peso
        notas_setor[setor]["peso_total"] += peso
    elif resposta in ["Não", "Não sei"]:
        if setor not in notas_setor:
            notas_setor[setor] = {"pontos": 0, "peso_total": 0}
        notas_setor[setor]["peso_total"] += peso

# Resultados
st.header("Resultados do Diagnóstico")
pontuacoes = {}
for setor, valores in notas_setor.items():
    if valores["peso_total"] > 0:
        pontuacoes[setor] = round(100 * valores["pontos"] / valores["peso_total"])

if pontuacoes:
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    categorias = list(pontuacoes.keys())
    valores = list(pontuacoes.values())
    valores += valores[:1]
    categorias += categorias[:1]
    angles = [n / float(len(categorias)) * 2 * 3.14159 for n in range(len(categorias))]

    ax.plot(angles, valores)
    ax.fill(angles, valores, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categorias, fontsize=8)
    ax.set_title("Desempenho por Setor")
    st.pyplot(fig)

# Sugestões por IA simuladas
st.subheader("Sugestões para Melhorias")
for setor, nota in pontuacoes.items():
    if nota < 60:
        st.markdown(f"- **{setor}**: Avaliar estratégias e revisar manejo. Nota atual: {nota}/100.")
    elif nota < 80:
        st.markdown(f"- **{setor}**: Bom desempenho, mas há espaço para evolução. Nota atual: {nota}/100.")
    else:
        st.markdown(f"- **{setor}**: Excelente! Manter boas práticas. Nota atual: {nota}/100.")
