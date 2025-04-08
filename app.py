
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
import os

st.set_page_config(page_title="🌱 Rehsult Grãos", layout="centered")

# Função para gerar PDF
def gerar_pdf(analise, setores_areas):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Diagnóstico Rehsult Grãos", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, "Análise com GPT-4 (simulada):")
    pdf.ln(5)
    pdf.set_font("Arial", "", 11)
    for linha in analise.split("\n"):
        pdf.multi_cell(0, 10, linha)
    pdf.ln(10)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Pontuação por Setor:", ln=True)
    pdf.set_font("Arial", "", 11)
    for area, setores in setores_areas.items():
        pdf.cell(0, 10, f"Área: {area}", ln=True)
        for setor, score in setores.items():
            pdf.cell(0, 10, f"  - {setor}: {score:.1f}%", ln=True)
        pdf.ln(5)

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# Função de análise simulada
def gerar_analise_simulada(setores_areas):
    analise = "✅ Análise Simulada:\n"
    recomendacoes = "\n🎯 Recomendações:\n"
    for area, setores in setores_areas.items():
        for setor, score in setores.items():
            if score < 50:
                analise += f"- O setor {setor} em {area} apresenta baixa pontuação, indicando atenção.\n"
                recomendacoes += f"- Reavaliar práticas no setor {setor} em {area}.\n"
            elif score < 75:
                analise += f"- O setor {setor} em {area} está razoável, mas pode melhorar.\n"
                recomendacoes += f"- Buscar otimização no setor {setor} em {area}.\n"
            else:
                analise += f"- O setor {setor} em {area} apresenta bom desempenho.\n"
    return analise + recomendacoes

# Logo Rehagro
st.image("LOGO REAGRO TRATADA.png", width=180)

st.title("🌱 Rehsult Grãos")
st.markdown("Diagnóstico de fazendas produtoras de grãos com análise simulada GPT-4")

# Perguntas iniciais
with st.form("dados_iniciais"):
    col1, col2 = st.columns(2)
    nome = col1.text_input("👨‍🌾 Nome do responsável pela fazenda")
    fazenda = col2.text_input("🏡 Nome da fazenda")
    produtividade = st.text_input("🌾 Produtividade média esperada (sc/ha)")
    submitted = st.form_submit_button("Iniciar Diagnóstico")
    if submitted:
        st.session_state.nome = nome
        st.session_state.fazenda = fazenda
        st.session_state.produtividade = produtividade
        st.session_state.start = True
        st.experimental_rerun()

if "start" not in st.session_state:
    st.stop()

# Leitura da planilha
df = pd.read_excel("Teste Chat.xlsx")
df.columns = df.columns.str.strip()
df = df.rename(columns={"Referência": "ID"})

# Inicializar respostas
if "respostas" not in st.session_state:
    st.session_state.respostas = {}
if "pergunta_id" not in st.session_state:
    st.session_state.pergunta_id = 1

# Execução do questionário
while st.session_state.pergunta_id is not None:
    linha = df[df["ID"] == st.session_state.pergunta_id]
    if linha.empty:
        break
    row = linha.iloc[0]
    depende = row.get("Depende de")
    if pd.notna(depende) and int(depende) not in st.session_state.respostas:
        st.session_state.pergunta_id += 1
        continue
    resposta = st.radio(row["Pergunta"], ["Sim", "Não", "Não sei"], key=f"pergunta_{row['ID']}")
    if st.button("Próxima", key=f"next_{row['ID']}"):
        st.session_state.respostas[row["ID"]] = {
            "Resposta": resposta,
            "Setor": row["Setor"],
            "Peso": row["Peso"],
            "Area": row["Área"]
        }
        correta = str(row["Resposta certa"]).strip().lower()
        if isinstance(correta, str) and "se" in correta:
            st.session_state.pergunta_id += 1
        elif resposta.lower() == correta:
            st.session_state.pergunta_id = row["Próxima (Sim)"]
        else:
            st.session_state.pergunta_id = row["Próxima (Não)"]
        st.experimental_rerun()

# Resultado final
st.success("✅ Diagnóstico Concluído")

df_resultados = pd.DataFrame(st.session_state.respostas).T
df_resultados["Score"] = df_resultados.apply(
    lambda row: row["Peso"] if str(row["Resposta"]).lower() == str(row["Resposta"]).lower() else 0, axis=1
)

setores_areas = {}
for area in df_resultados["Area"].unique():
    dados_area = df_resultados[df_resultados["Area"] == area]
    setores = dados_area.groupby("Setor")["Score"].sum()
    pesos = dados_area.groupby("Setor")["Peso"].sum()
    setores_areas[area] = (setores / pesos * 100).fillna(0).to_dict()

st.markdown("### 📊 Resultados")
for area, setores in setores_areas.items():
    st.markdown(f"#### 🔍 {area}")
    for setor, score in setores.items():
        st.markdown(f"- **{setor}**: {score:.1f}%")

# Análise simulada
analise = gerar_analise_simulada(setores_areas)
st.markdown("### 🤖 Análise com GPT-4 (simulada)")
st.markdown(analise)

# PDF final
pdf_buffer = gerar_pdf(analise, setores_areas)
st.download_button("📄 Baixar PDF", data=pdf_buffer, file_name="diagnostico_rehsult.pdf")
