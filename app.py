
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF

def gerar_analise_simulada(setores_areas):
    return '''✅ Análise com GPT-4 (simulada):

- A área de **Calagem e Gessagem** apresenta baixa pontuação, indicando necessidade de correção de solo.
- O controle de **plantas daninhas** com pré-emergente está abaixo do ideal.
- A **adubação** está parcialmente alinhada com as recomendações técnicas.

🎯 Recomendações:
- Reavaliar a calagem com base nas análises de solo mais recentes.
- Considerar herbicidas mais eficazes para o início da cultura.
- Ajustar as doses de macronutrientes com base na produtividade esperada.'''

def gerar_pdf(texto):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for linha in texto.split("\n"):
        pdf.multi_cell(0, 10, linha)
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

st.set_page_config(page_title="Rehsult Grãos", layout="centered")

if "inicio" not in st.session_state:
    st.session_state.inicio = False
if "respostas" not in st.session_state:
    st.session_state.respostas = {"Fertilidade": {}, "Plantas Daninhas": {}}
    st.session_state.pergunta_atual = None
    st.session_state.area_atual = None
    st.session_state.fim_area = False
    st.session_state.finalizado = False
    st.session_state.decidir_proxima_area = False
if "areas_respondidas" not in st.session_state:
    st.session_state.areas_respondidas = []

# TELA INICIAL
if not st.session_state.inicio:
    st.image("LOGO REAGRO TRATADA.png", width=200)
    st.title("🌾 Rehsult Grãos - Diagnóstico de Fazenda")
    st.text_input("Nome da Fazenda", key="fazenda")
    st.text_input("Nome do Responsável", key="responsavel")
    st.number_input("Produtividade média de SOJA (kg/ha)", min_value=0, key="prod_soja")
    st.number_input("Produtividade média de MILHO (kg/ha)", min_value=0, key="prod_milho")
    st.session_state.area_atual = st.radio("Qual área deseja começar avaliando?", ["Fertilidade", "Plantas Daninhas"])
    if st.button("Iniciar Diagnóstico"):
        st.session_state.inicio = True
        aba = "Fertilidade" if st.session_state.area_atual == "Fertilidade" else "Planta Daninha"
        df_inicio = pd.read_excel("Teste Chat.xlsx", sheet_name=aba)
        df_inicio = df_inicio.dropna(subset=["Referência", "Pergunta", "Peso"])
        df_inicio["Referência"] = df_inicio["Referência"].astype(int)
        df_inicio = df_inicio.sort_values("Referência")
        st.session_state.pergunta_atual = int(df_inicio["Referência"].iloc[0])

# COLETA DE DADOS
if st.session_state.inicio and not st.session_state.finalizado and not st.session_state.decidir_proxima_area:
    st.image("LOGO REAGRO TRATADA.png", width=150)
    area = st.session_state.area_atual
    aba_excel = "Fertilidade" if area == "Fertilidade" else "Planta Daninha"
    df = pd.read_excel("Teste Chat.xlsx", sheet_name=aba_excel)
    df["Peso"] = pd.to_numeric(df["Peso"], errors="coerce")
    df = df.dropna(subset=["Referência", "Pergunta", "Peso"])
    df["Referência"] = df["Referência"].astype(int)
    df = df.sort_values("Referência")
    perguntas_dict = df.set_index("Referência").to_dict(orient="index")

    ref = st.session_state.pergunta_atual
    if ref in perguntas_dict:
        pergunta = perguntas_dict[ref]["Pergunta"]
        peso = perguntas_dict[ref]["Peso"]
        proxima_sim = perguntas_dict[ref]["Próxima (Sim)"]
        proxima_nao = perguntas_dict[ref]["Próxima (Não)"]
        gabarito = perguntas_dict[ref]["Gabarito"]
        setor = perguntas_dict[ref]["Setor"]

        resposta = st.radio(pergunta, ["Sim", "Não", "Não sei"], key=f"{area}_{ref}")
        if st.button("Responder"):
            st.session_state.respostas[area][ref] = {
                "Setor": setor,
                "Pergunta": pergunta,
                "Resposta": resposta,
                "Peso": peso,
                "Gabarito": gabarito
            }
            if (gabarito == "Sim" and resposta == "Sim") or (gabarito == "Não" and resposta == "Não"):
                st.session_state.pergunta_atual = int(proxima_sim) if not pd.isna(proxima_sim) else None
            else:
                st.session_state.pergunta_atual = int(proxima_nao) if not pd.isna(proxima_nao) else None

            if st.session_state.pergunta_atual is None:
                st.session_state.areas_respondidas.append(area)
                st.session_state.decidir_proxima_area = True

# MUDAR DE ÁREA OU FINALIZAR
if st.session_state.decidir_proxima_area:
    st.success(f"Área {st.session_state.area_atual} finalizada!")
    proxima = [a for a in ["Fertilidade", "Plantas Daninhas"] if a not in st.session_state.areas_respondidas]
    if proxima:
        if st.button(f"Deseja responder {proxima[0]}?"):
            st.session_state.area_atual = proxima[0]
            st.session_state.decidir_proxima_area = False
            aba = "Fertilidade" if proxima[0] == "Fertilidade" else "Planta Daninha"
            df_inicio = pd.read_excel("Teste Chat.xlsx", sheet_name=aba)
            df_inicio = df_inicio.dropna(subset=["Referência", "Pergunta", "Peso"])
            df_inicio["Referência"] = df_inicio["Referência"].astype(int)
            df_inicio = df_inicio.sort_values("Referência")
            st.session_state.pergunta_atual = int(df_inicio["Referência"].iloc[0])
    else:
        if st.button("Finalizar Diagnóstico"):
            st.session_state.finalizado = True

# RELATÓRIO FINAL
if st.session_state.finalizado:
    mapa = {"Sim": 1, "Não": 0, "Não sei": 0.5}
    setores_por_area = {}
    for area in st.session_state.areas_respondidas:
        df_area = pd.DataFrame(st.session_state.respostas[area]).T
        if not df_area.empty:
            df_area["Score"] = df_area["Resposta"].map(mapa) * df_area["Peso"]
            setor_pct = df_area.groupby("Setor").apply(lambda x: round((x["Score"].sum() / x["Peso"].sum()) * 100, 1))
            setores_por_area[area] = setor_pct.to_dict()

    st.subheader("📊 Pontuação por Setor")
    for area, setores in setores_por_area.items():
        st.markdown(f"**{area}**")
        df_setor = pd.DataFrame(list(setores.items()), columns=["Setor", "Pontuação (%)"])
        st.dataframe(df_setor)

    st.subheader("🤖 Análise com GPT-4 (simulada)")
    analise = gerar_analise_simulada(setores_por_area)
    st.markdown(analise)

    pdf_file = gerar_pdf(analise)
    st.download_button("📥 Baixar Relatório PDF", data=pdf_file, file_name="relatorio_diagnostico.pdf")
