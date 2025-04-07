
import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="Rehsult Grãos", layout="centered")
st.title("🌾 Rehsult Grãos")
st.markdown("Bem-vindo ao sistema de diagnóstico de fazendas produtoras de grãos.")

# ------------------------ CONFIGURAÇÃO DO FLUXO ------------------------

if "etapa" not in st.session_state:
    st.session_state.etapa = "inicio"
    st.session_state.area_atual = None
    st.session_state.pergunta_idx = 0
    st.session_state.respostas = []
    st.session_state.areas_respondidas = set()

# ------------------------ DADOS DAS PERGUNTAS ------------------------

dados_perguntas = {
    "Fertilidade": [
        {"Setor": "Análise de Solo", "Pergunta": "A fazenda realiza análise de solo regularmente?", "Peso": 1},
        {"Setor": "Calagem e Gessagem", "Pergunta": "Existe planejamento para calagem e gessagem?", "Peso": 2},
        {"Setor": "Macronutrientes", "Pergunta": "A adubação de macronutrientes segue recomendação técnica?", "Peso": 1.5},
    ],
    "Plantas Daninhas": [
        {"Setor": "Pré-emergente", "Pergunta": "É utilizado pré-emergente no início da cultura?", "Peso": 2},
        {"Setor": "Cobertura", "Pergunta": "A fazenda realiza boa cobertura do solo?", "Peso": 1.5},
    ]
}

mapa_valores = {"Sim": 1, "Não": 0, "Não sei": 0.5}

# ------------------------ FUNÇÕES AUXILIARES ------------------------

def gerar_analise_simulada(pontuacoes_por_area):
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

def calcular_pontuacoes(respostas):
    score = {}
    pesos = {}
    for r in respostas:
        setor = r["Setor"]
        valor = mapa_valores.get(r["Resposta"], 0)
        peso = r["Peso"]
        score[setor] = score.get(setor, 0) + valor * peso
        pesos[setor] = pesos.get(setor, 0) + peso
    return {setor: round(100 * score[setor] / pesos[setor], 1) for setor in score}

def organizar_por_area(respostas, pontuacoes):
    resultado = {}
    for r in respostas:
        area = r["Área"]
        setor = r["Setor"]
        if area not in resultado:
            resultado[area] = {}
        resultado[area][setor] = pontuacoes[setor]
    return resultado

# ------------------------ FLUXO DE EXECUÇÃO ------------------------

if st.session_state.etapa == "inicio":
    st.markdown("Selecione por qual área deseja iniciar o diagnóstico:")
    area = st.selectbox("Área inicial", list(dados_perguntas.keys()))
    if st.button("Iniciar Diagnóstico"):
        st.session_state.area_atual = area
        st.session_state.etapa = "perguntas"
        st.session_state.pergunta_idx = 0

elif st.session_state.etapa == "perguntas":
    area = st.session_state.area_atual
    idx = st.session_state.pergunta_idx
    perguntas = dados_perguntas[area]
    pergunta_atual = perguntas[idx]
    st.subheader(f"{area} - {pergunta_atual['Setor']}")
    resposta = st.radio(pergunta_atual["Pergunta"], ["Sim", "Não", "Não sei"], key=f"{area}_{idx}")
    if st.button("Próxima"):
        st.session_state.respostas.append({
            "Área": area,
            "Setor": pergunta_atual["Setor"],
            "Pergunta": pergunta_atual["Pergunta"],
            "Resposta": resposta,
            "Peso": pergunta_atual["Peso"]
        })
        st.session_state.pergunta_idx += 1
        if st.session_state.pergunta_idx >= len(perguntas):
            st.session_state.areas_respondidas.add(area)
            st.session_state.etapa = "outra_area"

elif st.session_state.etapa == "outra_area":
    outras = [a for a in dados_perguntas.keys() if a not in st.session_state.areas_respondidas]
    if outras:
        st.markdown("Deseja responder outra área?")
        if st.button("Sim"):
            st.session_state.area_atual = outras[0]
            st.session_state.pergunta_idx = 0
            st.session_state.etapa = "perguntas"
        elif st.button("Não"):
            st.session_state.etapa = "final"
    else:
        st.session_state.etapa = "final"

elif st.session_state.etapa == "final":
    st.success("✅ Diagnóstico finalizado!")
    df = pd.DataFrame(st.session_state.respostas)
    st.dataframe(df[["Área", "Setor", "Resposta", "Peso"]])

    pontuacoes = calcular_pontuacoes(st.session_state.respostas)
    setores_por_area = organizar_por_area(st.session_state.respostas, pontuacoes)

    st.subheader("📊 Pontuação por Setor")
    st.write(pd.DataFrame(pontuacoes.items(), columns=["Setor", "Pontuação (%)"]))

    st.subheader("🤖 Análise com GPT-4")
    analise = gerar_analise_simulada(setores_por_area)
    st.markdown(analise)

    pdf_file = gerar_pdf(analise)
    st.download_button("📥 Baixar Relatório PDF", data=pdf_file, file_name="relatorio_diagnostico.pdf")
