
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
import os

st.set_page_config(page_title="Rehsult Grãos", layout="centered")
st.image("LOGO REAGRO TRATADA.png", width=200)
st.title("🌱 Rehsult Grãos")
st.markdown("Diagnóstico de fazendas produtoras de grãos com análise simulada GPT-4")

@st.cache_data
def carregar_planilha():
    xls = pd.ExcelFile("Teste Chat.xlsx")
    perguntas_dict = {}
    for aba in xls.sheet_names:
        df = xls.parse(aba)
        df.fillna("", inplace=True)
        perguntas_dict[aba] = df
    return perguntas_dict

dados = carregar_planilha()

if "estado" not in st.session_state:
    st.session_state.estado = "inicio"
    st.session_state.area_atual = None
    st.session_state.pergunta_id = None
    st.session_state.respostas = {}
    st.session_state.areas_respondidas = []
    st.session_state.pular = set()

if st.session_state.estado == "inicio":
    st.session_state.nome = st.text_input("📋 Nome da Fazenda")
    st.session_state.soja = st.number_input("🌾 Produtividade média de Soja (sc/ha)", 0.0)
    st.session_state.milho = st.number_input("🌽 Produtividade média de Milho (sc/ha)", 0.0)
    if st.button("Iniciar Diagnóstico"):
        st.session_state.estado = "selecionar_area"
        st.rerun()

elif st.session_state.estado == "selecionar_area":
    st.subheader("Escolha a área para começar:")
    opcoes = [a for a in dados if a not in st.session_state.areas_respondidas]
    area = st.radio("Áreas disponíveis:", opcoes)
    if st.button("👉 Iniciar perguntas"):
        st.session_state.area_atual = area
        st.session_state.pergunta_id = 1
        st.session_state.estado = "perguntando"
        st.rerun()

elif st.session_state.estado == "perguntando":
    area = st.session_state.area_atual
    df = dados[area]
    df = df.fillna("")
    respostas = st.session_state.respostas.setdefault(area, {})

    while True:
        linha = df[df["ID"] == st.session_state.pergunta_id]
        if linha.empty:
            st.session_state.areas_respondidas.append(area)
            st.session_state.estado = "selecionar_area"
            st.rerun()
        linha = linha.iloc[0]

        if linha["Depende de"]:
            pergunta_dep = int(linha["Depende de"])
            if st.session_state.respostas.get(area, {}).get(pergunta_dep, {}).get("resposta") != "Sim":
                st.session_state.pular.add(st.session_state.pergunta_id)
                st.session_state.pergunta_id += 1
                continue

        if st.session_state.pergunta_id in st.session_state.pular:
            st.session_state.pergunta_id += 1
            continue

        st.markdown(f"**{linha['Pergunta']}**")
        resposta = st.radio("Selecione:", ["Sim", "Não", "Não sei"], key=f"pergunta_{linha['ID']}")
        if st.button("Responder", key=f"botao_{linha['ID']}"):
            respostas[linha["ID"]] = {
                "resposta": resposta,
                "peso": linha["PESO"],
                "setor": linha["Setor"],
                "correta": linha["Certa"],
            }
            prox = linha["Próxima (Sim)"] if resposta == "Sim" else linha["Próxima (Não)"]
            if prox:
                st.session_state.pergunta_id = int(prox)
            else:
                st.session_state.areas_respondidas.append(area)
                st.session_state.estado = "selecionar_area"
            st.rerun()
        break

elif len(st.session_state.areas_respondidas) == len(dados):
    st.success("✅ Diagnóstico Concluído")

    def calcular_resultado():
        resultado = {}
        for area, respostas in st.session_state.respostas.items():
            setores = {}
            for id_, info in respostas.items():
                peso = float(info["peso"]) if str(info["peso"]).replace(".", "", 1).isdigit() else 0
                certa = info["correta"].strip().lower()
                resp = info["resposta"].strip().lower()
                setor = info["setor"]

                score = 0
                if resp == "não sei":
                    score = peso * 0.5
                elif resp == certa:
                    score = peso

                setores[setor] = setores.get(setor, 0) + score
            resultado[area] = setores
        return resultado

    def gerar_grafico_radar(setores, area):
        categorias = list(setores.keys())
        valores = list(setores.values())
        categorias.append(categorias[0])
        valores.append(valores[0])
        angulos = np.linspace(0, 2 * np.pi, len(categorias), endpoint=False).tolist()
        angulos += angulos[:1]
        fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
        ax.plot(angulos, valores, marker='o')
        ax.fill(angulos, valores, alpha=0.3)
        ax.set_yticklabels([])
        ax.set_xticks(angulos[:-1])
        ax.set_xticklabels(categorias)
        ax.set_title(f"📊 Radar - {area}")
        st.pyplot(fig)

    def gerar_pdf(analise, setores_areas, output="/mnt/data/diagnostico_rehsult.pdf"):
        os.makedirs("/mnt/data", exist_ok=True)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Diagnóstico - Fazenda: {st.session_state.nome}", ln=True)
        pdf.cell(0, 10, f"Soja: {st.session_state.soja} sc/ha | Milho: {st.session_state.milho} sc/ha", ln=True)
        pdf.ln(5)
        for area, setores in setores_areas.items():
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, f"{area}:", ln=True)
            pdf.set_font("Arial", '', 11)
            for setor, valor in setores.items():
                pdf.cell(0, 10, f"  - {setor}: {valor:.1f} pts", ln=True)
            pdf.ln(2)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Análise Simulada GPT-4:", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 10, analise)
        pdf.output(output)
        return output

    resultado = calcular_resultado()
    for area, setores in resultado.items():
        st.subheader(f"📊 Resultados - {area}")
        media = np.mean(list(setores.values()))
        st.markdown(f"**Pontuação Geral:** {media:.1f} pontos")
        gerar_grafico_radar(setores, area)

    analise = "✅ Análise Simulada:
"
    for area, setores in resultado.items():
        for setor, valor in setores.items():
            if valor < 30:
                analise += f"- O setor {setor} em {area} está com baixa pontuação.
"
            elif valor < 70:
                analise += f"- O setor {setor} em {area} está razoável.
"
            else:
                analise += f"- O setor {setor} em {area} está com bom desempenho.
"
    analise += "
🎯 Recomendações:
- Revisar práticas nos setores com baixa pontuação."

    st.markdown("### 🤖 Análise Simulada")
    st.markdown(analise)

    pdf_file = gerar_pdf(analise, resultado)
    with open(pdf_file, "rb") as f:
        st.download_button("📄 Baixar Diagnóstico em PDF", f, file_name="diagnostico_rehsult.pdf")
