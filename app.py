import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="Rehsult Grãos - Diagnóstico", layout="centered")
st.title("🌾 Rehsult Grãos - Diagnóstico de Fazenda")

st.image("LOGO REAGRO TRATADA.png", width=200)

# Função para carregar os dados da planilha
@st.cache_data
def carregar_dados():
    df = pd.read_excel("Teste Chat.xlsx", sheet_name="fertilidade")
    df = df.dropna(subset=["Pergunta"])
    df["Peso"] = pd.to_numeric(df["Peso"], errors="coerce").fillna(1)
    return df

# Função para classificar produtividade
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
    if cultura == "milho":
        if valor < 170:
            return "Baixa"
        elif valor <= 190:
            return "Média"
        elif valor <= 205:
            return "Alta"
        else:
            return "Muito Alta"

df = carregar_dados()
if "etapa" not in st.session_state:
    st.session_state.etapa = "inicio"
if "respostas" not in st.session_state:
    st.session_state.respostas = {}
if "pergunta_atual" not in st.session_state:
    st.session_state.pergunta_atual = 0

# Tela inicial
if st.session_state.etapa == "inicio":
    st.subheader("Bem-vindo ao Rehsult Grãos!")
    st.write("Este é um sistema de diagnóstico para fazendas produtoras de grãos. Você responderá uma pergunta por vez, e ao final, verá um relatório com pontuação geral, gráfico de radar e recomendações.")
    st.session_state.fazenda = st.text_input("Nome da Fazenda")
    st.session_state.responsavel = st.text_input("Nome do Responsável")
    st.session_state.soja = st.number_input("Produtividade da última safra de **soja** (sc/ha)", min_value=0.0, step=1.0)
    st.session_state.milho = st.number_input("Produtividade da última safra de **milho** (sc/ha)", min_value=0.0, step=1.0)

    if st.button("Iniciar Diagnóstico") and st.session_state.fazenda and st.session_state.responsavel:
        st.session_state.etapa = "diagnostico"
        st.rerun()

# Etapa de perguntas
elif st.session_state.etapa == "diagnostico":
    respostas = st.session_state.respostas
    i = st.session_state.pergunta_atual
    while i < len(df):
        pergunta = df.iloc[i]
        pergunta_id = pergunta["ID"]
        texto = pergunta["Pergunta"]
        condicao = pergunta.get("Vinculo", "")
        mostrar = True
        if condicao and isinstance(condicao, str):
            partes = condicao.split("=")
            if len(partes) == 2:
                depende_id = int(partes[0].strip())
                valor_esperado = partes[1].strip()
                if respostas.get(depende_id) != valor_esperado:
                    mostrar = False
        if mostrar and pergunta_id not in respostas:
            st.write(f"**{texto}**")
            resposta = st.radio("Escolha:", ["Sim", "Não", "Não sei"], key=f"pergunta_{pergunta_id}")
            if st.button("Responder", key=f"botao_{pergunta_id}"):
                respostas[pergunta_id] = resposta
                st.session_state.pergunta_atual += 1
                st.rerun()
            break
        i += 1
    else:
        st.session_state.etapa = "resultado"
        st.rerun()

# Resultado
elif st.session_state.etapa == "resultado":
    respostas = st.session_state.respostas
    st.subheader("✅ Diagnóstico Concluído")

    resultados = []
    for _, row in df.iterrows():
        pid = row["ID"]
        peso = row["Peso"]
        setor = row["Setor"]
        resp = respostas.get(pid, "Não sei")
        nota = {"Sim": peso, "Não": 0, "Não sei": 0}.get(resp, 0)
        resultados.append({"Setor": setor, "Nota": nota, "Peso": peso})

    resultado_df = pd.DataFrame(resultados)
    setores = resultado_df.groupby("Setor").sum()
    setores["Percentual"] = (setores["Nota"] / setores["Peso"]) * 100
    setores = setores.reset_index()

    nota_geral = (resultado_df["Nota"].sum() / resultado_df["Peso"].sum()) * 100
    nota_geral_arredondada = round(nota_geral)

    st.metric("Pontuação Geral da Fazenda", f"{nota_geral_arredondada}/100")

    # Classificações
    soja_txt = classificar_produtividade(st.session_state.soja, "soja")
    milho_txt = classificar_produtividade(st.session_state.milho, "milho")
    st.write(f"**Produtividade Soja:** {st.session_state.soja} sc/ha - {soja_txt}")
    st.write(f"**Produtividade Milho:** {st.session_state.milho} sc/ha - {milho_txt}")

    # Radar chart
    st.subheader("📊 Radar por Setor")
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'projection': 'radar'})
    categorias = setores["Setor"].tolist()
    valores = setores["Percentual"].tolist()
    angles = np.linspace(0, 2 * np.pi, len(categorias), endpoint=False).tolist()
    valores += valores[:1]
    angles += angles[:1]
    ax.plot(angles, valores)
    ax.fill(angles, valores, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categorias)
    ax.set_yticklabels([])
    st.pyplot(fig)

    # Geração do PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "Relatório de Diagnóstico - Rehsult Grãos", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Fazenda: {st.session_state.fazenda}", ln=True)
    pdf.cell(200, 10, f"Responsável: {st.session_state.responsavel}", ln=True)
    pdf.cell(200, 10, f"Pontuação Geral: {nota_geral_arredondada}/100", ln=True)
    pdf.cell(200, 10, f"Produtividade Soja: {st.session_state.soja} sc/ha - {soja_txt}", ln=True)
    pdf.cell(200, 10, f"Produtividade Milho: {st.session_state.milho} sc/ha - {milho_txt}", ln=True)
    pdf.ln(10)
    for _, linha in setores.iterrows():
        pdf.cell(200, 10, f"- {linha['Setor']}: {round(linha['Percentual'])}/100", ln=True)
    pdf_buffer = BytesIO()
    pdf.output(pdf_buffer, dest='F')
    pdf_buffer.seek(0)
    st.download_button("📄 Baixar Relatório em PDF", data=pdf_buffer, file_name="diagnostico_rehsult.pdf", mime="application/pdf")
