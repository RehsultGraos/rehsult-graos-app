
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
import base64

st.set_page_config(page_title="Rehsult Grãos", layout="centered")

st.image("LOGO REAGRO TRATADA.png", width=180)

st.title("🌾 Rehsult Grãos")
st.markdown("Versão com GPT-4 (simulada) integrada ao diagnóstico")

@st.cache_data
def carregar_planilha():
    return pd.read_excel("Teste Chat.xlsx", sheet_name=None)

def gerar_grafico_radar(setores_dict, titulo):
    categorias = list(setores_dict.keys())
    valores = list(setores_dict.values())
    valores += valores[:1]
    categorias += categorias[:1]

    angles = np.linspace(0, 2 * np.pi, len(categorias), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.fill(angles, valores, alpha=0.25)
    ax.plot(angles, valores, linewidth=2)

    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categorias)
    ax.set_title(titulo, y=1.1)
    st.pyplot(fig)

def gerar_analise_simulada(setores_areas):
    pontos = []
    recomendacoes = []

    for area, setores in setores_areas.items():
        for setor, pct in setores.items():
            if pct < 50:
                pontos.append(f"A área de **{setor}** apresenta baixa pontuação, indicando necessidade de atenção.")
                recomendacoes.append(f"- Rever o manejo de **{setor}** na área de **{area}**.")
            elif pct < 75:
                pontos.append(f"O setor de **{setor}** está razoável, mas pode ser otimizado.")
                recomendacoes.append(f"- Avaliar oportunidades de melhoria em **{setor}**.")

    analise = "### ✅ Análise com GPT-4 (simulada):\n"
    analise += "\n".join([f"- {p}" for p in pontos]) + "\n\n"
    analise += "### 🎯 Recomendações:\n"
    analise += "\n".join(recomendacoes)

    return analise

dados = carregar_planilha()
perguntas_dict = {}
setores = {}

for aba, df in dados.items():
    for _, row in df.iterrows():
        perguntas_dict[row["ID"]] = row.to_dict()
        setores[row["ID"]] = aba

if "respostas" not in st.session_state:
    st.session_state.respostas = {}
if "pagina" not in st.session_state:
    st.session_state.pagina = "inicio"
if "area_atual" not in st.session_state:
    st.session_state.area_atual = ""
if "respondidas" not in st.session_state:
    st.session_state.respondidas = []
if "areas_respondidas" not in st.session_state:
    st.session_state.areas_respondidas = []

def responder(pergunta_id, resposta):
    st.session_state.respostas[pergunta_id] = resposta
    st.session_state.respondidas.append(pergunta_id)
    proxima = perguntas_dict[pergunta_id][f"Próxima ({resposta})"]
    if pd.isna(proxima):
        st.session_state.pagina = "outra_area"
    else:
        st.session_state.pagina = proxima

if st.session_state.pagina == "inicio":
    st.subheader("Qual área deseja avaliar?")
    area = st.radio("Escolha uma área:", list(dados.keys()))
    if st.button("Iniciar Diagnóstico"):
        st.session_state.area_atual = area
        primeira = dados[area].iloc[0]["ID"]
        st.session_state.pagina = primeira
        st.session_state.areas_respondidas.append(area)

elif st.session_state.pagina in perguntas_dict:
    pergunta = perguntas_dict[st.session_state.pagina]
    st.subheader(pergunta["Pergunta"])
    col1, col2, col3 = st.columns(3)
    if col1.button("✅ Sim"):
        responder(pergunta["ID"], "Sim")
    if col2.button("❌ Não"):
        responder(pergunta["ID"], "Não")
    if col3.button("🤔 Não sei"):
        responder(pergunta["ID"], "Não sei")

elif st.session_state.pagina == "outra_area":
    areas_disponiveis = [a for a in dados.keys() if a not in st.session_state.areas_respondidas]
    if areas_disponiveis:
        nova_area = areas_disponiveis[0]
        st.subheader(f"Deseja responder também sobre {nova_area}?")
        col1, col2 = st.columns(2)
        if col1.button("✅ Sim"):
            st.session_state.area_atual = nova_area
            primeira = dados[nova_area].iloc[0]["ID"]
            st.session_state.pagina = primeira
            st.session_state.areas_respondidas.append(nova_area)
            st.rerun()
        if col2.button("❌ Não"):
            st.session_state.pagina = "relatorio"
            st.rerun()
    else:
        st.session_state.pagina = "relatorio"
        st.rerun()

elif st.session_state.pagina == "relatorio":
    st.success("✅ Diagnóstico Concluído")

    respostas_df = pd.DataFrame([
        {"ID": k, "Resposta": v, "Área": setores[k]}
        for k, v in st.session_state.respostas.items()
    ])
    respostas_df = respostas_df.merge(
        pd.concat(dados.values()), on="ID"
    )

    setores_por_area = {}
    for area in st.session_state.areas_respondidas:
        df_area = respostas_df[respostas_df["Área"] == area]
        mapa = {"Sim": 1, "Não": 0, "Não sei": 0.5}
        df_area["Score"] = df_area["Resposta"].map(mapa) * df_area["Peso"]
        setores_score = df_area.groupby("Setor")["Score"].sum()
        setores_peso = df_area.groupby("Setor")["Peso"].sum()
        setores_pct = (setores_score / setores_peso * 100).to_dict()
        setores_por_area[area] = setores_pct

        st.subheader(f"📊 Resultados - {area}")
        st.markdown(f"**Pontuação Geral:** {sum(df_area['Score']) / sum(df_area['Peso']) * 100:.1f}%")
        gerar_grafico_radar(setores_pct, f"Radar - {area}")

    # 🔍 Análise simulada (com GPT-4 falso)
    st.subheader("🤖 Análise com GPT-4 (simulada)")
    analise = gerar_analise_simulada(setores_por_area)
    st.markdown(analise)
