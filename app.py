
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
from math import pi

st.set_page_config(page_title="Rehsult Grãos", layout="centered")
st.image("LOGO REAGRO TRATADA.png", width=200)

st.title("Rehsult Grãos")
st.markdown("Diagnóstico de fazendas produtoras de grãos com análise simulada GPT-4")

if "estado" not in st.session_state:
    st.session_state.estado = "dados_iniciais"
    st.session_state.respostas = {}
    st.session_state.areas_respondidas = []
    st.session_state.dados_iniciais = {}
    st.session_state.pergunta_id = None
    st.session_state.area_atual = None

# ---------- ETAPA INICIAL ----------
if st.session_state.estado == "dados_iniciais":
    with st.form("dados_form"):
        nome = st.text_input("👤 Nome do responsável")
        fazenda = st.text_input("🏡 Nome da fazenda")
        soja = st.number_input("🌱 Produtividade de soja (sc/ha)", 0.0)
        milho = st.number_input("🌽 Produtividade de milho (sc/ha)", 0.0)
        submitted = st.form_submit_button("Iniciar")
    if submitted:
        st.session_state.dados_iniciais = {
            "nome": nome,
            "fazenda": fazenda,
            "soja": soja,
            "milho": milho
        }
        st.session_state.estado = "escolher_area"

# ---------- ESCOLHER ÁREA ----------
if st.session_state.estado == "escolher_area":
    st.markdown("### Qual área deseja começar?")
    opcao = st.radio("Área:", ["Fertilidade", "Planta Daninha"])
    if st.button("Iniciar diagnóstico"):
        st.session_state.area_atual = opcao
        st.session_state.pergunta_id = 1
        st.session_state.estado = "perguntando"

# ---------- PERGUNTAS ----------
if st.session_state.estado == "perguntando":
    df = pd.read_excel("Teste Chat.xlsx", sheet_name=st.session_state.area_atual)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={"Referência": "ID", "Vínculo": "Depende de", "Resposta": "Correta"})

    while True:
        linha = df[df["ID"] == st.session_state.pergunta_id]
        if linha.empty:
            st.session_state.areas_respondidas.append(st.session_state.area_atual)
            st.session_state.estado = "resultado_parcial"
            st.rerun()

        row = linha.iloc[0]

        if pd.notna(row["Depende de"]):
            ref = int(row["Depende de"])
            if st.session_state.respostas.get(ref, {}).get("resposta") != "Sim":
                st.session_state.pergunta_id = int(row["Sim"]) if pd.notna(row["Sim"]) else None
                st.rerun()

        st.markdown(f"**{row['Pergunta']}**")
        resposta = st.radio("Escolha uma opção:", ["Sim", "Não", "Não sei"], key=f"pergunta_{row['ID']}")
        if st.button("Responder", key=f"responder_{row['ID']}"):
            correta = row["Correta"]
            ganho = 0
            if isinstance(correta, str) and "==" in correta:
                ref_id, esperado = correta.split("==")
                ref_id = int(ref_id.strip())
                esperado = esperado.strip()
                if st.session_state.respostas.get(ref_id, {}).get("resposta") == esperado:
                    ganho = row["Peso"]
            elif resposta == correta:
                ganho = row["Peso"]
            elif resposta == "Não sei":
                ganho = row["Peso"] * 0.5

            st.session_state.respostas[row["ID"]] = {
                "resposta": resposta,
                "peso": row["Peso"],
                "setor": row["Setor"],
                "area": row["Área"],
                "ganho": ganho
            }

            prox = row["Sim"] if resposta == "Sim" else row["Não"]
            st.session_state.pergunta_id = int(prox) if pd.notna(prox) else None
            st.rerun()
        break

# ---------- RESULTADO ----------
if st.session_state.estado == "resultado_parcial":
    st.success("✅ Diagnóstico parcial concluído.")
    if len(st.session_state.areas_respondidas) == 1:
        if st.session_state.areas_respondidas[0] == "Fertilidade":
            proxima = "Planta Daninha"
        else:
            proxima = "Fertilidade"
        if st.button(f"Deseja responder {proxima}?"):
            st.session_state.area_atual = proxima
            st.session_state.pergunta_id = 1
            st.session_state.estado = "perguntando"
            st.rerun()
        if st.button("Finalizar diagnóstico"):
            st.session_state.estado = "final"
            st.rerun()

# ---------- RELATÓRIO FINAL ----------
if st.session_state.estado == "final":
    st.subheader("📊 Resultado Final")
    df_result = pd.DataFrame(st.session_state.respostas).T
    setores_areas = {}
    for area in df_result["area"].unique():
        setores = df_result[df_result["area"] == area].groupby("setor")["ganho"].sum()
        pesos = df_result[df_result["area"] == area].groupby("setor")["peso"].sum()
        resultado = (setores / pesos * 100).fillna(0)
        setores_areas[area] = resultado.to_dict()

    for area, setores in setores_areas.items():
        st.markdown(f"### 🔍 {area}")
        for setor, score in setores.items():
            st.write(f"- **{setor}**: {score:.1f}%")

    st.balloons()
