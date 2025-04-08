
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="Rehsult Grãos", layout="centered")

# Funções de apoio
def gerar_grafico_radar(setores, titulo):
    categorias = list(setores.keys())
    valores = list(setores.values())
    categorias += [categorias[0]]
    valores += [valores[0]]

    angulos = np.linspace(0, 2 * np.pi, len(categorias), endpoint=False).tolist()
    angulos += angulos[:1]

    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    ax.plot(angulos, valores, marker='o')
    ax.fill(angulos, valores, alpha=0.25)
    ax.set_yticklabels([])
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(categorias)
    ax.set_title(f"Radar - {titulo}")
    st.pyplot(fig)

def gerar_analise_simulada(setores_areas):
    texto = "🤖 **Análise com GPT-4 (simulada)**\n\n"
    texto += "✅ **Análise Simulada:**\n\n"
    recomendacoes = []
    for area, setores in setores_areas.items():
        for setor, score in setores.items():
            if score < 40:
                texto += f"- A área de **{setor}** em **{area}** apresenta baixa pontuação, indicando atenção.\n"
                recomendacoes.append(f"Rever práticas em {setor.lower()} ({area.lower()}).")
            elif score < 70:
                texto += f"- A área de **{setor}** em **{area}** está razoável, mas pode melhorar.\n"
                recomendacoes.append(f"Aprimorar estratégias em {setor.lower()} ({area.lower()}).")
            else:
                texto += f"- A área de **{setor}** em **{area}** está com boa pontuação.\n"

    if recomendacoes:
        texto += "\n🎯 **Recomendações:**\n\n"
        for rec in set(recomendacoes):
            texto += f"- {rec}\n"
    return texto

def gerar_pdf(analise, setores_areas):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Diagnóstico Rehsult Grãos", ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, analise)

    for area, setores in setores_areas.items():
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"{area}", ln=True)
        pdf.set_font("Arial", "", 12)
        for setor, score in setores.items():
            pdf.cell(0, 10, f"{setor}: {score:.1f}%", ln=True)

    buffer = BytesIO()
    pdf_bytes = pdf.output(dest='S').encode("latin-1", "replace")
    buffer.write(pdf_bytes)
    buffer.seek(0)
    return buffer

# Inicialização de estado
if 'etapa' not in st.session_state:
    st.session_state.etapa = 'inicio'
    st.session_state.nome = ''
    st.session_state.produtividade_soja = ''
    st.session_state.produtividade_milho = ''
    st.session_state.area_atual = ''
    st.session_state.perguntas_respondidas = []
    st.session_state.respostas = {}

# Etapas do app
if st.session_state.etapa == 'inicio':
    st.title("🌱 Rehsult Grãos")
    st.markdown("Diagnóstico de fazendas produtoras de grãos com análise simulada GPT-4")
    st.session_state.nome = st.text_input("Qual seu nome?")
    st.session_state.produtividade_soja = st.text_input("Produtividade esperada de Soja (sc/ha)?")
    st.session_state.produtividade_milho = st.text_input("Produtividade esperada de Milho (sc/ha)?")
    st.session_state.area_atual = st.radio("Qual área deseja começar?", ["Planta Daninha", "Fertilidade"])
    if st.button("Iniciar Diagnóstico"):
        st.session_state.etapa = 'perguntas'

elif st.session_state.etapa == 'perguntas':
    df = pd.read_excel("Teste Chat.xlsx", sheet_name=None)
    area = st.session_state.area_atual
    perguntas = df[area]
    proxima = None
    mapa = {'Sim': 1, 'Não': 0, 'Não sei': 0.5}

    for _, row in perguntas.iterrows():
        if row['ID'] in st.session_state.perguntas_respondidas:
            continue
        st.write(row["Pergunta"])
        resposta = st.radio("", ["Sim", "Não", "Não sei"], key=row["ID"])
        if st.button("Responder", key="responder_" + str(row["ID"])):
            st.session_state.perguntas_respondidas.append(row["ID"])
            st.session_state.respostas[row["ID"]] = {"Resposta": resposta, "Setor": row["Setor"], "Peso": row["Peso"]}
            proxima = row["Próxima (Sim)"] if resposta == "Sim" else row["Próxima (Não)"]
            break

    if len(st.session_state.perguntas_respondidas) == len(perguntas):
        st.session_state.etapa = 'pergunta_extra'

elif st.session_state.etapa == 'pergunta_extra':
    outra = "Fertilidade" if st.session_state.area_atual == "Planta Daninha" else "Planta Daninha"
    st.write(f"Deseja responder também sobre {outra}?")
    col1, col2 = st.columns(2)
    if col1.button("✅ Sim"):
        st.session_state.area_atual = outra
        st.session_state.etapa = 'perguntas'
    if col2.button("❌ Não"):
        st.session_state.etapa = 'resultado'

elif st.session_state.etapa == 'resultado':
    respostas = pd.DataFrame.from_dict(st.session_state.respostas, orient='index')
    respostas["Score"] = respostas["Resposta"].map({'Sim': 1, 'Não': 0, 'Não sei': 0.5}) * respostas["Peso"]
    setores = respostas.groupby("Setor")["Score"].mean().to_dict()
    area_label = st.session_state.area_atual

    st.markdown("## ✅ Diagnóstico Concluído")
    st.markdown(f"### 📊 Resultados - {area_label}")
    st.markdown(f"**Pontuação Geral:** {round(np.mean(list(setores.values()))*100, 1)}%")
    gerar_grafico_radar(setores, area_label)

    setores_areas = {area_label: {k: v*100 for k, v in setores.items()}}
    analise = gerar_analise_simulada(setores_areas)
    st.markdown(analise)

    pdf = gerar_pdf(analise.replace("\n", "\n"), setores_areas)
    st.download_button("📄 Baixar PDF", pdf, file_name="diagnostico_rehsult.pdf", mime="application/pdf")
