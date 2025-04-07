
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="Rehsult Grãos - Diagnóstico", layout="centered")

# Carregar planilha (simulação de perguntas por área)
dados = {
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

def gerar_analise_gpt4(setores_areas):
    return """✅ Análise com GPT-4:

- A área de **Calagem e Gessagem** apresenta baixa pontuação, indicando a necessidade de correção da acidez do solo.
- O setor de **Pré-emergente** nas plantas daninhas foi um dos mais críticos, sugerindo que o controle inicial está falhando.
- A aplicação de **macronutrientes** está razoável, mas pode ser otimizada para elevar a produtividade da soja.

🎯 Recomendações:
- Realizar análise de solo completa e aplicar calcário/gesso conforme recomendação.
- Revisar o protocolo de pré-emergência e considerar produtos com maior residual.
- Ajustar doses de macronutrientes conforme exigência da cultura e análise de solo."""

def gerar_pdf_relatorio(texto):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for linha in texto.split("\n"):
        pdf.multi_cell(0, 10, linha)
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

def calcular_scores(respostas):
    setores_score = {}
    setores_peso = {}
    mapa = {"Sim": 1, "Não": 0, "Não sei": 0.5}
    for r in respostas:
        peso = r["Peso"]
        setor = r["Setor"]
        valor = mapa.get(r["Resposta"], 0)
        setores_score[setor] = setores_score.get(setor, 0) + valor * peso
        setores_peso[setor] = setores_peso.get(setor, 0) + peso
    return {s: round(100 * setores_score[s]/setores_peso[s], 1) for s in setores_score}

st.title("🌾 Rehsult Grãos")
st.markdown("Responda o diagnóstico técnico por área")

if "area_atual" not in st.session_state:
    st.session_state.area_atual = None
    st.session_state.pergunta_idx = 0
    st.session_state.respostas = []
    st.session_state.concluido = False

if st.session_state.area_atual is None:
    area_escolhida = st.radio("Qual área deseja responder primeiro?", ["Fertilidade", "Plantas Daninhas"])
    if st.button("Iniciar Diagnóstico"):
        st.session_state.area_atual = area_escolhida

elif not st.session_state.concluido:
    perguntas = dados[st.session_state.area_atual]
    if st.session_state.pergunta_idx < len(perguntas):
        p = perguntas[st.session_state.pergunta_idx]
        resposta = st.radio(p["Pergunta"], ["Sim", "Não", "Não sei"], key=f"resp_{st.session_state.pergunta_idx}")
        if st.button("Próxima"):
            st.session_state.respostas.append({
                "Área": st.session_state.area_atual,
                "Setor": p["Setor"],
                "Pergunta": p["Pergunta"],
                "Resposta": resposta,
                "Peso": p["Peso"]
            })
            st.session_state.pergunta_idx += 1
    else:
        outras = [a for a in dados if a != st.session_state.area_atual]
        st.success(f"Concluído o diagnóstico de {st.session_state.area_atual}.")
        if st.radio("Deseja responder a outra área?", ["Sim", "Não"], key="outro") == "Sim":
            st.session_state.area_atual = outras[0]
            st.session_state.pergunta_idx = 0
        else:
            st.session_state.concluido = True

if st.session_state.concluido:
    df = pd.DataFrame(st.session_state.respostas)
    st.subheader("📊 Resultado por setor")
    pontuacoes = calcular_scores(st.session_state.respostas)
    st.dataframe(pd.DataFrame(pontuacoes.items(), columns=["Setor", "Pontuação (%)"]))

    setores_por_area = {area: {} for area in dados}
    for r in st.session_state.respostas:
        setores_por_area[r["Área"]][r["Setor"]] = pontuacoes[r["Setor"]]

    st.markdown("### 🤖 Análise com GPT-4")
    analise = gerar_analise_gpt4(setores_por_area)
    st.markdown(analise)

    pdf_data = gerar_pdf_relatorio(analise)
    st.download_button("📥 Baixar Relatório em PDF", data=pdf_data, file_name="relatorio_diagnostico.pdf")
