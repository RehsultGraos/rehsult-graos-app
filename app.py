
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="Rehsult Grãos - Diagnóstico", layout="centered")
st.title("🌾 Rehsult Grãos - Diagnóstico de Fazenda")
st.image("https://tecnocoffeeapi.rehagro.com.br/storage/imagens/rehagro.png", width=150)

@st.cache_data
def carregar_perguntas():
    df = pd.read_excel("Teste Chat.xlsx", sheet_name="Fertilidade")
    df = df.rename(columns={
        'Referência': 'ID',
        'Pergunta': 'Pergunta',
        'Sim': 'Proxima_Sim',
        'Não': 'Proxima_Nao',
        'Nota': 'Nota'
    })
    df = df[['Área', 'Setor', 'ID', 'Pergunta', 'Proxima_Sim', 'Proxima_Nao', 'Nota']]
    df = df.dropna(subset=['ID', 'Pergunta'])
    return df

df_perguntas = carregar_perguntas()

if 'fase' not in st.session_state:
    st.session_state.fase = 'inicio'
if 'respostas' not in st.session_state:
    st.session_state.respostas = {}
if 'pergunta_atual' not in st.session_state:
    st.session_state.pergunta_atual = 1

if st.session_state.fase == 'inicio':
    st.subheader("Bem-vindo ao Rehsult Grãos!")
    st.write("Este é um sistema de diagnóstico para fazendas produtoras de grãos.")
    st.session_state.fazenda = st.text_input("Nome da Fazenda")
    st.session_state.responsavel = st.text_input("Nome do Responsável")
    st.session_state.prod_soja = st.number_input("Produtividade da última safra de soja (sc/ha):", min_value=0)
    st.session_state.prod_milho = st.number_input("Produtividade da última safra de milho (sc/ha):", min_value=0)
    if st.button("Iniciar Diagnóstico"):
        st.session_state.fase = 'perguntas'
        st.rerun()

def classificar_produtividade(valor, cultura):
    if cultura == "soja":
        if valor < 65:
            return "Baixa"
        elif valor <= 75:
            return "Média"
        elif valor <= 90:
            return "Alta"
        return "Muito Alta"
    elif cultura == "milho":
        if valor < 170:
            return "Baixa"
        elif valor <= 190:
            return "Média"
        elif valor <= 205:
            return "Alta"
        return "Muito Alta"

if st.session_state.fase == 'perguntas':
    pergunta = df_perguntas[df_perguntas['ID'] == st.session_state.pergunta_atual]
    if not pergunta.empty:
        pergunta = pergunta.iloc[0]
        st.markdown(f"**{pergunta['Pergunta']}**")
        resposta = st.radio("Resposta:", ["Sim", "Não", "Não sei"], key=pergunta['ID'])
        if st.button("Responder"):
            st.session_state.respostas[pergunta['ID']] = resposta
            if resposta == "Sim" and not pd.isna(pergunta["Proxima_Sim"]):
                st.session_state.pergunta_atual = int(pergunta["Proxima_Sim"])
            elif resposta == "Não" and not pd.isna(pergunta["Proxima_Nao"]):
                st.session_state.pergunta_atual = int(pergunta["Proxima_Nao"])
            else:
                st.session_state.pergunta_atual += 1
            st.rerun()
    else:
        st.session_state.fase = 'resultado'
        st.rerun()

if st.session_state.fase == 'resultado':
    st.subheader("Resultado do Diagnóstico")

    respostas = st.session_state.respostas
    df_perguntas['Respondida'] = df_perguntas['ID'].apply(lambda x: x in respostas)
    df_perguntas['Valor'] = df_perguntas['ID'].apply(lambda x: respostas.get(x, ""))
    df_perguntas['Nota obtida'] = df_perguntas.apply(
        lambda row: row['Nota'] if row['Valor'] == 'Sim' else 0, axis=1
    )

    setores = df_perguntas.groupby('Setor').agg({'Nota obtida': 'sum', 'Nota': 'sum', 'Respondida': 'sum'})
    setores = setores[setores['Respondida'] > 0]
    setores['Pontuacao'] = (setores['Nota obtida'] / setores['Nota'] * 100).round(0)

    nota_geral = (df_perguntas['Nota obtida'].sum() / df_perguntas['Nota'].sum()) * 100
    nota_geral = round(nota_geral)

    st.markdown(f"**Pontuação Geral da Fazenda:** {nota_geral}/100")

    soja_txt = classificar_produtividade(st.session_state.prod_soja, "soja")
    milho_txt = classificar_produtividade(st.session_state.prod_milho, "milho")
    st.write(f"Produtividade da Soja: {st.session_state.prod_soja} sc/ha - {soja_txt}")
    st.write(f"Produtividade do Milho: {st.session_state.prod_milho} sc/ha - {milho_txt}")

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

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(190, 10, "Relatório de Diagnóstico - Rehsult Grãos", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Fazenda: {st.session_state.fazenda}", ln=True)
    pdf.cell(200, 10, f"Responsável: {st.session_state.responsavel}", ln=True)
    pdf.cell(200, 10, f"Pontuação Geral: {nota_geral}/100", ln=True)
    pdf.cell(200, 10, f"Soja: {st.session_state.prod_soja} sc/ha - {soja_txt}", ln=True)
    pdf.cell(200, 10, f"Milho: {st.session_state.prod_milho} sc/ha - {milho_txt}", ln=True)
    pdf.ln(5)
    for i, row in setores.iterrows():
        pdf.cell(200, 10, f"- {i}: {int(row['Pontuacao'])}/100", ln=True)
    pdf.ln(5)
    for i, row in setores.iterrows():
        if row['Pontuacao'] < 60:
            pdf.multi_cell(0, 10, f"- O setor {i} teve desempenho abaixo do esperado. Avaliar melhorias é recomendado.")

    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    buffer.seek(0)
    pdf.image(buffer, x=10, y=None, w=180)

    pdf_out = BytesIO()
    pdf.output(pdf_out)
    st.download_button("📄 Baixar Relatório em PDF", data=pdf_out.getvalue(), file_name="diagnostico_fertilidade.pdf", mime="application/pdf")
