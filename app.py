
import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Rehsult Grãos - Diagnóstico", layout="centered")

# Logo
st.image("LOGO REAGRO TRATADA.png", width=200)

# Carregamento dos dados
@st.cache_data
def carregar_dados():
    df = pd.read_excel("Teste Chat.xlsx", sheet_name="Fertilidade")
    setores_df = df[['Setor', 'Peso']].dropna().drop_duplicates()
    return df, setores_df

perguntas_df, setores_df = carregar_dados()

# Inicialização do estado da sessão
if "pagina" not in st.session_state:
    st.session_state.pagina = 0
    st.session_state.respostas = {}
    st.session_state.fazenda = ""
    st.session_state.responsavel = ""

# Página inicial
if st.session_state.pagina == 0:
    st.title("Bem-vindo ao Rehsult Grãos!")
    st.markdown("Este é um sistema de diagnóstico para fazendas produtoras de grãos. Você responderá uma pergunta por vez e, ao final, verá um relatório com pontuação geral, gráfico de radar e recomendações.")
    st.session_state.fazenda = st.text_input("Nome da Fazenda")
    st.session_state.responsavel = st.text_input("Nome do Responsável")
    if st.button("Iniciar Diagnóstico"):
        st.session_state.pagina += 1
        st.rerun()

# Lógica das perguntas
elif st.session_state.pagina <= len(perguntas_df):
    linha = perguntas_df.iloc[st.session_state.pagina - 1]
    
    # Verifica se há dependência e se a resposta foi "Sim"
    if pd.notna(linha["G"]):
        pergunta_dependente = int(linha["G"])
        resposta_anterior = st.session_state.respostas.get(pergunta_dependente, None)
        if resposta_anterior != "Sim":
            st.session_state.pagina += 1
            st.rerun()

    st.subheader(f"Pergunta {int(linha['ID'])}")
    resposta = st.radio(linha["Pergunta"], ["Sim", "Não", "Não sei"])
    if st.button("Responder"):
        st.session_state.respostas[int(linha["ID"])] = resposta
        st.session_state.pagina += 1
        st.rerun()

# Página de resultados
else:
    st.header("✅ Diagnóstico Concluído")

    # Cálculo das notas
    notas_setores = []
    for setor in setores_df["Setor"].unique():
        perguntas_setor = perguntas_df[perguntas_df["Setor"] == setor]
        total_peso = perguntas_setor["Peso"].sum()
        nota = 0
        for _, linha in perguntas_setor.iterrows():
            resposta = st.session_state.respostas.get(int(linha["ID"]))
            if resposta == "Sim":
                nota += linha["Peso"]
        nota_final = (nota / total_peso) * 100 if total_peso > 0 else 0
        notas_setores.append({"Setor": setor, "Pontuacao": round(nota_final)})

    df_notas = pd.DataFrame(notas_setores)

    nota_geral = round(df_notas["Pontuacao"].mean())

    st.metric("Pontuação Geral da Fazenda", f"{nota_geral}/100")
    st.dataframe(df_notas)

    # Radar chart
    categorias = df_notas["Setor"]
    valores = df_notas["Pontuacao"]

    num_vars = len(categorias)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    valores += valores[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angles, valores, color='green', alpha=0.25)
    ax.plot(angles, valores, color='green', linewidth=2)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categorias, fontsize=8)
    st.pyplot(fig)

    # Geração de sugestões por IA
    sugestoes = []
    for _, linha in perguntas_df.iterrows():
        resposta = st.session_state.respostas.get(int(linha["ID"]))
        if resposta == "Não":
            sugestoes.append(f"- {linha['Pergunta']}")

    if sugestoes:
        st.markdown("### Sugestões de Melhoria (geradas por IA)")
        for item in sugestoes:
            st.markdown(item)

    # Geração de PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Relatório de Diagnóstico - Rehsult Grãos", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Fazenda: {st.session_state.fazenda}", ln=True)
    pdf.cell(200, 10, f"Responsável: {st.session_state.responsavel}", ln=True)
    pdf.cell(200, 10, f"Pontuação Geral: {nota_geral}/100", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Pontuação por Setor:", ln=True)
    pdf.set_font("Arial", "", 12)
    for _, linha in df_notas.iterrows():
        pdf.cell(200, 10, f"- {linha['Setor']}: {linha['Pontuacao']}/100", ln=True)
    if sugestoes:
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 10, "Sugestões de Melhoria:", ln=True)
        pdf.set_font("Arial", "", 12)
        for item in sugestoes:
            pdf.multi_cell(0, 10, item)

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    st.download_button("📄 Baixar PDF", data=buffer, file_name="diagnostico.pdf")
