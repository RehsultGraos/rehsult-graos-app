
import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF
from io import BytesIO
from math import pi
import matplotlib.pyplot as plt

st.set_page_config(page_title="Rehsult Grãos", layout="centered")
st.image("LOGO REAGRO TRATADA.png", width=200)
st.title("Rehsult Grãos")
st.markdown("Diagnóstico de fazendas produtoras de grãos com análise simulada GPT-4")

if "estado" not in st.session_state:
    st.session_state.estado = "dados_iniciais"
    st.session_state.respostas = {}
    st.session_state.areas_respondidas = []
    st.session_state.dados_iniciais = {}

def obter_condicional(ref, valor_esperado, respostas):
    return any(r[0] == ref and r[1] == valor_esperado for r in respostas)

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
    ax.plot(angulos, valores, marker='o')
    ax.fill(angulos, valores, alpha=0.3)
    ax.set_title(f"Radar - {area}")
    st.pyplot(fig)

def gerar_analise_simulada(setores_areas):
    texto = "Analise GPT-4 (simulada):\n\n"
    for area, setores in setores_areas.items():
        for setor, nota in setores.items():
            if nota < 50:
                texto += f"- O setor {setor} em {area} apresenta baixa pontuação.\n"
            elif nota < 75:
                texto += f"- O setor {setor} em {area} está mediano.\n"
            else:
                texto += f"- O setor {setor} em {area} apresenta bom desempenho.\n"
    return texto

def gerar_pdf(analise, setores_areas, dados_iniciais):
    def limpar(txt): return str(txt).encode("latin-1", "replace").decode("latin-1")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, limpar(f"Fazenda: {dados_iniciais.get('nome', '')}"), ln=True)
    pdf.cell(200, 10, limpar(f"Soja: {dados_iniciais.get('soja', '')} sc/ha"), ln=True)
    pdf.cell(200, 10, limpar(f"Milho: {dados_iniciais.get('milho', '')} sc/ha"), ln=True)
    pdf.ln(5)
    for area, setores in setores_areas.items():
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, limpar(f"Área: {area}"), ln=True)
        pdf.set_font("Arial", size=12)
        for setor, val in setores.items():
            pdf.cell(200, 10, limpar(f"{setor}: {val:.1f}%"), ln=True)
        pdf.ln(4)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, limpar("Análise GPT-4 (simulada)"), ln=True)
    pdf.set_font("Arial", size=12)
    for linha in analise.split("\n"):
        pdf.multi_cell(0, 10, limpar(linha))
    return BytesIO(pdf.output(dest="S").encode("latin1"))

df = pd.read_excel("Teste Chat.xlsx", sheet_name=None)
abas = list(df.keys())

if st.session_state.estado == "dados_iniciais":
    st.subheader("Dados Iniciais")
    nome = st.text_input("Nome da Fazenda")
    soja = st.number_input("Produtividade de Soja", 0.0, format="%.1f")
    milho = st.number_input("Produtividade de Milho", 0.0, format="%.1f")
    if st.button("Iniciar"):
        st.session_state.dados_iniciais = {"nome": nome, "soja": soja, "milho": milho}
        st.session_state.estado = "inicio"
        st.rerun()

elif st.session_state.estado == "inicio":
    st.subheader("Qual área deseja iniciar?")
    area_escolhida = st.radio("", [a for a in abas if a not in st.session_state.areas_respondidas])
    if st.button("Iniciar Diagnóstico"):
        st.session_state.area_atual = area_escolhida
        st.session_state.pergunta_id = None
        st.session_state.estado = "perguntas"

elif st.session_state.estado == "perguntas":
    area = st.session_state.area_atual
    perguntas = df[area].dropna(subset=["Pergunta"]).reset_index(drop=True)
    if st.session_state.pergunta_id is None:
        st.session_state.pergunta_id = perguntas.iloc[0]["Referência"]

    linha = perguntas[perguntas["Referência"] == st.session_state.pergunta_id].iloc[0]

    # Regra da coluna G (Exibir se Sim de)
    if pd.notna(linha.get("Exibir se Sim de")):
        ref_dep = linha["Exibir se Sim de"]
        resposta_anterior = next((r[1] for r in st.session_state.respostas.get(area, []) if r[0] == ref_dep), None)
        if resposta_anterior != "Sim":
            st.session_state.pergunta_id = linha["Próxima (Não)"]
            st.rerun()

    st.markdown(f"**{linha['Pergunta']}**")
    resposta = st.radio("Escolha:", ["Sim", "Não", "Não sei"], key=f"r{linha['Referência']}")

    if st.button("Responder"):
        st.session_state.respostas.setdefault(area, []).append((linha["Referência"], resposta, linha["Peso"], linha["Setor"], linha["Resposta"]))
        proxima = linha["Próxima (Sim)"] if resposta == "Sim" else linha["Próxima (Não)"]
        if pd.isna(proxima):
            st.session_state.areas_respondidas.append(area)
            outras = [a for a in abas if a not in st.session_state.areas_respondidas]
            st.session_state.estado = "inicio" if outras else "relatorio"
        else:
            st.session_state.pergunta_id = proxima
        st.rerun()

elif st.session_state.estado == "relatorio":
    st.success("Diagnóstico Concluído")
    setores_areas = {}
    for area, respostas in st.session_state.respostas.items():
        nota_area = {}
        pesos_area = {}
        for ref, resp, peso, setor, correta in respostas:
            if pd.isna(peso): continue
            if "se" in str(correta):
                cond_ref = correta.split("se")[1].strip().split(" ")[0]
                esperado = correta.split(" ")[-1]
                cond_ok = obter_condicional(cond_ref, esperado, respostas)
                acerto = 1 if resp == "Sim" and cond_ok else 0
            else:
                acerto = 1 if resp == correta else 0.5 if resp == "Não sei" else 0
            nota_area[setor] = nota_area.get(setor, 0) + acerto * peso
            pesos_area[setor] = pesos_area.get(setor, 0) + peso
        setores_areas[area] = {s: (nota_area[s] / pesos_area[s]) * 100 for s in nota_area}
        st.markdown(f"### Resultados - {area}")
        st.markdown(f"**Pontuação Geral:** {np.mean(list(setores_areas[area].values())):.1f}%")
        gerar_grafico_radar(setores_areas[area], area)

    st.markdown("---")
    analise = gerar_analise_simulada(setores_areas)
    st.markdown(analise)
    pdf = gerar_pdf(analise, setores_areas, st.session_state.dados_iniciais)
    st.download_button("Baixar PDF", data=pdf, file_name="relatorio_rehsult.pdf")
