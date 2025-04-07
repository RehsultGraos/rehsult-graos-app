import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="Rehsult Grãos", layout="wide")

st.title("🌱 Rehsult Grãos")
st.markdown("Versão com GPT-4 (simulada) integrada ao diagnóstico")

# ---------------------- Funções --------------------------

def gerar_grafico_radar(dados_por_setor, area):
    setores = list(dados_por_setor.keys())
    valores = list(dados_por_setor.values())

    if len(setores) != len(valores) or len(setores) == 0:
        st.error(f"Erro ao gerar gráfico de {area}: dados incompletos.")
        return None

    setores += [setores[0]]
    valores += [valores[0]]

    angles = np.linspace(0, 2 * np.pi, len(setores), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(setores, fontsize=9)
    ax.plot(angles, valores, marker='o')
    ax.fill(angles, valores, alpha=0.25)
    ax.set_title(f"Radar - {area}", y=1.1)
    st.pyplot(fig)

def gerar_pdf(setores_areas, analise_ia):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for area, setores in setores_areas.items():
        pdf.set_font("Arial", style="B", size=14)
        pdf.cell(200, 10, txt=f"Área: {area}", ln=True)
        pdf.set_font("Arial", size=12)
        for setor, pct in setores.items():
            pdf.cell(200, 10, txt=f"{setor}: {pct:.1f}%", ln=True)
        pdf.ln(5)

    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(200, 10, txt="Análise GPT-4 (Simulada):", ln=True)
    pdf.set_font("Arial", size=12)
    for linha in analise_ia.split("\n"):
        pdf.multi_cell(0, 10, linha)
    
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

def gerar_analise_simulada(setores_areas):
    texto = "✅ Análise Simulada:\n\n"
    for area, setores in setores_areas.items():
        for setor, pct in setores.items():
            if pct < 60:
                texto += f"• O setor **{setor}** na área de **{area}** está abaixo do ideal. Avaliar estratégias de melhoria.\n"
            elif pct < 80:
                texto += f"• O setor **{setor}** na área de **{area}** tem desempenho razoável. Há espaço para ajustes.\n"
            else:
                texto += f"• O setor **{setor}** na área de **{area}** apresenta bom desempenho.\n"
    texto += "\n🎯 Recomendações:\n- Avaliar os setores com menor pontuação.\n- Consultar especialistas conforme necessário.\n"
    return texto

# ---------------------- Início do App --------------------------

df = pd.read_excel("Teste Chat.xlsx", sheet_name=None)
areas_disponiveis = list(df.keys())

if "estado" not in st.session_state:
    st.session_state.estado = "inicio"
    st.session_state.respostas = {}
    st.session_state.areas_respondidas = []

if st.session_state.estado == "inicio":
    st.subheader("Qual área deseja começar?")
    area_escolhida = st.radio("", areas_disponiveis)
    if st.button("Iniciar Diagnóstico"):
        st.session_state.estado = "perguntando"
        st.session_state.area_atual = area_escolhida
        st.session_state.pergunta_idx = 0

elif st.session_state.estado == "perguntando":
    area = st.session_state.area_atual
    perguntas = df[area].dropna(subset=["Pergunta"])
    pergunta = perguntas.iloc[st.session_state.pergunta_idx]

    st.markdown(f"**{pergunta['Pergunta']}**")
    resposta = st.radio("Selecione uma opção:", ["Sim", "Não", "Não sei"], key=f"resposta_{st.session_state.pergunta_idx}")

    if st.button("Próxima"):
        st.session_state.respostas.setdefault(area, [])
        st.session_state.respostas[area].append((pergunta["Setor"], resposta, pergunta["Peso"]))

        if st.session_state.pergunta_idx + 1 < len(perguntas):
            st.session_state.pergunta_idx += 1
        else:
            st.session_state.areas_respondidas.append(area)
            if len(st.session_state.areas_respondidas) < len(areas_disponiveis):
                outras = [a for a in areas_disponiveis if a not in st.session_state.areas_respondidas]
                st.session_state.estado = "perguntar_outra"
                st.session_state.proxima_area = outras[0]
            else:
                st.session_state.estado = "resultado"

elif st.session_state.estado == "perguntar_outra":
    st.subheader(f"Deseja responder também sobre {st.session_state.proxima_area}?")
    col1, col2 = st.columns(2)
    if col1.button("✅ Sim"):
        st.session_state.area_atual = st.session_state.proxima_area
        st.session_state.pergunta_idx = 0
        st.session_state.estado = "perguntando"
    elif col2.button("❌ Não"):
        st.session_state.estado = "resultado"

elif st.session_state.estado == "resultado":
    st.header("✅ Diagnóstico Concluído")
    setores_por_area = {}
    for area, respostas in st.session_state.respostas.items():
        setor_scores = {}
        setor_pesos = {}
        for setor, resposta, peso in respostas:
            nota = {"Sim": 1, "Não": 0, "Não sei": 0.5}.get(resposta, 0)
            setor_scores[setor] = setor_scores.get(setor, 0) + nota * peso
            setor_pesos[setor] = setor_pesos.get(setor, 0) + peso
        setores_por_area[area] = {s: (setor_scores[s]/setor_pesos[s])*100 for s in setor_scores}

    for area, setores in setores_por_area.items():
        st.subheader(f"📊 Resultados - {area}")
        st.markdown(f"**Pontuação Geral:** {np.mean(list(setores.values())):.1f}%")
        gerar_grafico_radar(setores, area)

    st.subheader("🤖 Análise com GPT-4 (simulada)")
    analise = gerar_analise_simulada(setores_por_area)
    st.markdown(analise)

    pdf = gerar_pdf(setores_por_area, analise)
    st.download_button("📥 Baixar PDF do Diagnóstico", data=pdf, file_name="diagnostico.pdf")