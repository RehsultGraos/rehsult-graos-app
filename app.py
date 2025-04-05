import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="Rehsult Grãos - Diagnóstico", layout="centered")
st.image("logo_rehagro.png", width=200)
st.title("Rehsult Grãos - Diagnóstico de Fazenda")

@st.cache_data
def carregar_dados():
    df = pd.read_excel("Teste Chat.xlsx", sheet_name=None)
    perguntas_df = df['Perguntas']
    setores_df = perguntas_df[['Setor', 'Peso']].dropna().drop_duplicates()
    return perguntas_df, setores_df

perguntas_df, setores_df = carregar_dados()

if 'etapa' not in st.session_state:
    st.session_state.etapa = 'inicio'
if 'respostas' not in st.session_state:
    st.session_state.respostas = {}

if st.session_state.etapa == 'inicio':
    st.session_state.fazenda = st.text_input("Nome da Fazenda")
    st.session_state.responsavel = st.text_input("Nome do Responsável")
    st.session_state.soja = st.number_input("Produtividade de soja (sc/ha) na safra passada", min_value=0)
    st.session_state.milho = st.number_input("Produtividade de milho (sc/ha) na safra passada", min_value=0)
    if st.button("Iniciar Diagnóstico"):
        st.session_state.etapa = 'perguntas'
        st.session_state.indice = 0
        st.rerun()

elif st.session_state.etapa == 'perguntas':
    indice = st.session_state.indice
    perguntas_validas = perguntas_df.dropna(subset=['Pergunta'])

    if indice < len(perguntas_validas):
        pergunta = perguntas_validas.iloc[indice]
        texto = pergunta['Pergunta']
        codigo = pergunta['Código']
        resposta = st.radio(texto, ['Sim', 'Não', 'Não sei'])
        if st.button("Responder"):
            st.session_state.respostas[codigo] = resposta
            st.session_state.indice += 1
            st.rerun()
    else:
        st.session_state.etapa = 'resultado'
        st.rerun()

elif st.session_state.etapa == 'resultado':
    st.header("Resultado do Diagnóstico")

    respostas = st.session_state.respostas
    setores = setores_df['Setor'].unique()
    resultados = []

    for setor in setores:
        perguntas_setor = perguntas_df[perguntas_df['Setor'] == setor]
        total_peso = perguntas_setor['Peso'].sum()
        pontos = 0
        peso_respondido = 0

        for _, linha in perguntas_setor.iterrows():
            codigo = linha['Código']
            peso = linha['Peso']
            nota = linha['Nota']
            resposta = respostas.get(codigo)

            if pd.notna(nota) and resposta == 'Sim':
                pontos += nota * peso / 100
                peso_respondido += peso
            elif resposta in ['Não', 'Não sei']:
                peso_respondido += peso

        if peso_respondido > 0:
            percentual = round((pontos / peso_respondido) * 100)
            resultados.append({"Setor": setor, "Pontuacao": percentual})

    resultados_df = pd.DataFrame(resultados)
    nota_geral = round(resultados_df['Pontuacao'].mean())

    # Radar
    categorias = resultados_df['Setor'].tolist()
    valores = resultados_df['Pontuacao'].tolist()
    categorias.append(categorias[0])
    valores.append(valores[0])

    angles = np.linspace(0, 2 * np.pi, len(categorias), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.plot(angles, valores, 'o-', linewidth=2)
    ax.fill(angles, valores, alpha=0.25)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categorias)
    st.pyplot(fig)

    # IA - Sugestão
    sugestoes = []
    for _, linha in resultados_df.iterrows():
        if linha['Pontuacao'] < 50:
            sugestoes.append(f"O setor {linha['Setor']} apresenta baixa pontuação e pode ser melhorado.")

    # Produtividade
    def classificar_prod(cultura, valor):
        if cultura == "Soja":
            if valor < 65:
                return "Baixa"
            elif valor <= 75:
                return "Média"
            elif valor <= 90:
                return "Alta"
            else:
                return "Muito Alta"
        if cultura == "Milho":
            if valor < 170:
                return "Baixa"
            elif valor <= 190:
                return "Média"
            elif valor <= 205:
                return "Alta"
            else:
                return "Muito Alta"

    prod_soja = classificar_prod("Soja", st.session_state.soja)
    prod_milho = classificar_prod("Milho", st.session_state.milho)

    # PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "Relatório de Diagnóstico - Rehsult Grãos", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Fazenda: {st.session_state.fazenda}", ln=True)
    pdf.cell(200, 10, f"Responsável: {st.session_state.responsavel}", ln=True)
    pdf.cell(200, 10, f"Pontuação Geral da Fazenda: {nota_geral}/100", ln=True)
    pdf.cell(200, 10, f"Produtividade soja: {st.session_state.soja} sc/ha - {prod_soja}", ln=True)
    pdf.cell(200, 10, f"Produtividade milho: {st.session_state.milho} sc/ha - {prod_milho}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(190, 10, "Resultados por Setor:", ln=True)
    pdf.set_font("Arial", "", 12)
    for _, linha in resultados_df.iterrows():
        pdf.cell(200, 10, f"- {linha['Setor']}: {linha['Pontuacao']}/100", ln=True)

    if sugestoes:
        pdf.ln(10)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(190, 10, "Sugestões de melhoria:", ln=True)
        pdf.set_font("Arial", "", 12)
        for sugestao in sugestoes:
            pdf.cell(200, 10, f"- {sugestao}", ln=True)

    buffer = BytesIO()
    pdf.output(buffer, dest='F')
    buffer.seek(0)

    st.download_button("📄 Baixar Relatório em PDF", data=buffer, file_name="diagnostico.pdf", mime="application/pdf")
