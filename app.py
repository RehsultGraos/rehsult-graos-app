
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
from math import pi

st.set_page_config(page_title="Rehsult Grãos", layout="centered")
st.title("🌱 Rehsult Grãos")
st.markdown("Diagnóstico de fazendas produtoras de grãos com análise simulada GPT-4")

# Carregar planilha
df = pd.read_excel("Teste Chat.xlsx", sheet_name=None)
abas = list(df.keys())

# Inicializar estado
if "estado" not in st.session_state:
    st.session_state.estado = "inicio"
    st.session_state.respostas = {}
    st.session_state.areas_respondidas = []

# Funções
def gerar_grafico_radar(setores, area):
    setores = {k: v for k, v in setores.items() if pd.notnull(v)}
    if len(setores) < 3:
        st.warning(f"Não há dados suficientes para gerar o gráfico de {area}.")
        return

    categorias = list(setores.keys())
    valores = list(setores.values())
    valores += valores[:1]
    N = len(categorias)

    angulos = [n / float(N) * 2 * pi for n in range(N)]
    angulos += angulos[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(categorias)
    ax.set_rlabel_position(0)
    ax.plot(angulos, valores, marker='o')
    ax.fill(angulos, valores, alpha=0.3)
    ax.set_title(f"Radar - {area}")
    st.pyplot(fig)

def gerar_analise_simulada(setores_areas):
    texto = "🤖 **Análise com GPT-4 (simulada)**\n\n"
    for area, setores in setores_areas.items():
        for setor, nota in setores.items():
            if nota < 50:
                texto += f"- O setor **{setor}** em **{area}** apresenta baixa pontuação. Avaliar ações corretivas.\n"
            elif nota < 75:
                texto += f"- O setor **{setor}** em **{area}** está mediano. Há espaço para ajustes.\n"
            else:
                texto += f"- O setor **{setor}** em **{area}** apresenta bom desempenho.\n"
    texto += "\n🎯 **Recomendações:**\n- Revisar práticas nos setores com desempenho fraco.\n- Otimizar os setores intermediários.\n"
    return texto

def gerar_pdf(analise, setores_areas):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for area, setores in setores_areas.items():
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, f"Área: {area}", ln=True)
        pdf.set_font("Arial", size=12)
        for setor, val in setores.items():
            pdf.cell(200, 10, f"{setor}: {val:.1f}%", ln=True)
        pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "Análise GPT-4 (simulada)", ln=True)
    pdf.set_font("Arial", size=12)
    for linha in analise.split("\n"):
        pdf.multi_cell(0, 10, linha)

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    buffer = BytesIO(pdf_bytes)
    return buffer

# Etapas do app
if st.session_state.estado == "inicio":
    st.subheader("Qual área deseja começar?")
    area_escolhida = st.radio("", [a for a in abas if a not in st.session_state.areas_respondidas])
    if st.button("Iniciar Diagnóstico"):
        st.session_state.area_atual = area_escolhida
        st.session_state.pergunta_idx = 0
        st.session_state.estado = "perguntas"

elif st.session_state.estado == "perguntas":
    area = st.session_state.area_atual
    perguntas = df[area].dropna(subset=["Pergunta"]).reset_index(drop=True)
    linha = perguntas.iloc[st.session_state.pergunta_idx]
    st.markdown(f"**{linha['Pergunta']}**")
    resposta = st.radio("Selecione:", ["Sim", "Não", "Não sei"], key=f"resp_{st.session_state.pergunta_idx}")
    if st.button("Responder"):
        st.session_state.respostas.setdefault(area, []).append((linha["Setor"], resposta, linha["Peso"]))
        if st.session_state.pergunta_idx + 1 < len(perguntas):
            st.session_state.pergunta_idx += 1
        else:
            st.session_state.areas_respondidas.append(area)
            outras = [a for a in abas if a not in st.session_state.areas_respondidas]
            if outras:
                st.session_state.proxima_area = outras[0]
                st.session_state.estado = "perguntar_outra"
            else:
                st.session_state.estado = "relatorio"

elif st.session_state.estado == "perguntar_outra":
    area = st.session_state.proxima_area
    st.subheader(f"Deseja responder também sobre **{area}**?")
    col1, col2 = st.columns(2)
    if col1.button("✅ Sim"):
        st.session_state.area_atual = area
        st.session_state.pergunta_idx = 0
        st.session_state.estado = "perguntas"
    elif col2.button("❌ Não"):
        st.session_state.estado = "relatorio"

elif st.session_state.estado == "relatorio":
    st.success("✅ Diagnóstico Concluído")
    setores_areas = {}
    for area, respostas in st.session_state.respostas.items():
        nota_area = {}
        pesos_area = {}
        for setor, resp, peso in respostas:
            mult = {"Sim": 1, "Não": 0, "Não sei": 0.5}.get(resp, 0)
            nota_area[setor] = nota_area.get(setor, 0) + mult * peso
            pesos_area[setor] = pesos_area.get(setor, 0) + peso
        setores_areas[area] = {s: (nota_area[s] / pesos_area[s]) * 100 for s in nota_area}

    for area, setores in setores_areas.items():
        st.markdown(f"### 📊 Resultados - {area}")
        st.markdown(f"**Pontuação Geral:** {np.mean(list(setores.values())):.1f}%")
        gerar_grafico_radar(setores, area)

    st.markdown("---")
    analise = gerar_analise_simulada(setores_areas)
    st.markdown(analise)
    pdf = gerar_pdf(analise, setores_areas)
    st.download_button("📄 Baixar PDF do Diagnóstico", data=pdf, file_name="relatorio_rehsult.pdf")
