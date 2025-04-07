
def gerar_analise_simulada(setores_areas):
    return '''✅ Análise com GPT-4 (simulada):

- A área de **Calagem e Gessagem** apresenta baixa pontuação, indicando necessidade de correção de solo.
- O controle de **plantas daninhas** com pré-emergente está abaixo do ideal.
- A **adubação** está parcialmente alinhada com as recomendações técnicas.

🎯 Recomendações:
- Reavaliar a calagem com base nas análises de solo mais recentes.
- Considerar herbicidas mais eficazes para o início da cultura.
- Ajustar as doses de macronutrientes com base na produtividade esperada.'''



import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="Rehsult Grãos - Diagnóstico", layout="centered")

# Inicialização
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

# Tela de entrada
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

# Diagnóstico
if st.session_state.inicio and not st.session_state.finalizado and not st.session_state.decidir_proxima_area:
    st.image("LOGO REAGRO TRATADA.png", width=150)
    area = st.session_state.area_atual
    aba_excel = "Fertilidade" if area == "Fertilidade" else "Planta Daninha"
    df = pd.read_excel("Teste Chat.xlsx", sheet_name=aba_excel)
    df["Peso"] = pd.to_numeric(df["Peso"], errors="coerce")
    df = df.dropna(subset=["Referência", "Pergunta", "Peso"])
    df["Referência"] = df["Referência"].astype(int)
    perguntas_dict = df.set_index("Referência").to_dict(orient="index")

    ref = st.session_state.pergunta_atual
    if not st.session_state.fim_area and ref in perguntas_dict:
        dados = perguntas_dict[ref]
        resposta = st.radio(dados["Pergunta"], ["Sim", "Não", "Não sei"], key=f"{area}_ref_{ref}")
        if st.button("Responder", key=f"{area}_btn_{ref}"):
            st.session_state.respostas[area][ref] = {
                "Setor": dados["Setor"],
                "Área": dados["Área"],
                "Pergunta": dados["Pergunta"],
                "Peso": dados["Peso"],
                "Resposta": resposta,
                "Certa": dados.get("Resposta", "")
            }
            if resposta == "Sim" and not pd.isna(dados["Sim"]):
                st.session_state.pergunta_atual = int(dados["Sim"])
            elif not pd.isna(dados["Não"]):
                st.session_state.pergunta_atual = int(dados["Não"])
            else:
                st.session_state.fim_area = True
                st.session_state.decidir_proxima_area = True
    else:
        st.session_state.fim_area = True
        st.session_state.decidir_proxima_area = True

# Transição entre áreas
if st.session_state.decidir_proxima_area and not st.session_state.finalizado:
    if st.session_state.area_atual not in st.session_state.areas_respondidas:
        st.session_state.areas_respondidas.append(st.session_state.area_atual)

    outras = {"Fertilidade": "Plantas Daninhas", "Plantas Daninhas": "Fertilidade"}
    proxima = outras[st.session_state.area_atual]

    if proxima not in st.session_state.areas_respondidas:
        st.markdown(f"### Deseja responder também sobre **{proxima}**?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Sim"):
                st.session_state.area_atual = proxima
                aba = "Fertilidade" if proxima == "Fertilidade" else "Planta Daninha"
                df_inicio = pd.read_excel("Teste Chat.xlsx", sheet_name=aba)
                df_inicio = df_inicio.dropna(subset=["Referência", "Pergunta", "Peso"])
                df_inicio["Referência"] = df_inicio["Referência"].astype(int)
                df_inicio = df_inicio.sort_values("Referência")
                st.session_state.pergunta_atual = int(df_inicio["Referência"].iloc[0])
                st.session_state.fim_area = False
                st.session_state.decidir_proxima_area = False
        with col2:
            if st.button("❌ Não"):
                st.session_state.finalizado = True
                st.session_state.decidir_proxima_area = False
    else:
        st.session_state.finalizado = True
        st.session_state.decidir_proxima_area = False

# Relatório Final
st.subheader("🤖 Análise com GPT-4 (simulada)")
setores_por_area = {}
    mapa = {'Sim': 1, 'Não': 0, 'Não sei': 0.5}
for area in st.session_state.areas_respondidas:
        df_area = pd.DataFrame(st.session_state.respostas[area]).T
        if not df_area.empty:
            df_area["Score"] = df_area["Resposta"].map(mapa) * df_area["Peso"]
            setor_pct = df_area.groupby("Setor").apply(lambda x: round((x["Score"].sum() / x["Peso"].sum()) * 100, 1))
            setores_por_area[area] = setor_pct.to_dict()
    analise = gerar_analise_simulada(setores_por_area)
    st.markdown(analise)
    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "Análise Final com GPT-4 (simulada):", ln=True)
    pdf.set_font("Arial", "", 12)
    for linha in analise.split("\n"):
        pdf.multi_cell(0, 10, linha)
    


if st.session_state.finalizado:
    st.markdown("## ✅ Diagnóstico Concluído")
    mapa = {"Sim": 1, "Não": 0, "Não sei": 0.5}
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "Relatório de Diagnóstico - Rehsult Grãos", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Fazenda: {st.session_state.get('fazenda', 'NÃO INFORMADO')}", ln=True)
    pdf.cell(200, 10, f"Responsável: {st.session_state.get('responsavel', 'NÃO INFORMADO')}", ln=True)
    pdf.cell(200, 10, f"Produtividade média SOJA: {st.session_state.get('prod_soja', 0)} kg/ha", ln=True)
    pdf.cell(200, 10, f"Produtividade média MILHO: {st.session_state.get('prod_milho', 0)} kg/ha", ln=True)

    for area in set(st.session_state.areas_respondidas):
        df_resultado = pd.DataFrame(st.session_state.respostas[area]).T
        if df_resultado.empty:
            continue
        df_resultado["Score"] = df_resultado["Resposta"].map(mapa) * df_resultado["Peso"]
        setores = df_resultado.groupby("Setor").agg({"Score": "sum", "Peso": "sum"})
        setores["Percentual"] = (setores["Score"] / setores["Peso"]) * 100
        nota_area = (df_resultado["Score"].sum() / df_resultado["Peso"].sum()) * 100

        st.markdown(f"### 📊 Resultados - {area}")
        st.markdown(f"**Pontuação Geral:** {nota_area:.1f}%")

        labels = setores.index.tolist()
        valores = setores["Percentual"].tolist()
        valores += valores[:1]
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        angles += angles[:1]
        fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))
        ax.plot(angles, valores, color='green')
        ax.fill(angles, valores, color='green', alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels)
        ax.set_title(f"Radar - {area}")
        st.pyplot(fig)

        st.markdown("**Tópicos a Melhorar:**")
        pior_setores = setores.sort_values("Percentual").head(3)
        for setor, linha in pior_setores.iterrows():
            st.write(f"- {setor}: {linha['Percentual']:.1f}%")

        pdf.ln(10)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(200, 10, f"Área Avaliada: {area}", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.cell(200, 10, f"Pontuação Geral: {nota_area:.1f}%", ln=True)
        for setor, linha in setores.iterrows():
            pdf.cell(200, 10, f"- {setor}: {linha['Percentual']:.1f}%", ln=True)

    pdf_buffer = BytesIO()
    pdf_buffer.write(pdf.output(dest='S').encode('latin1'))
    pdf_buffer.seek(0)
    st.download_button("📄 Baixar Relatório em PDF", data=pdf_buffer.getvalue(), file_name="relatorio_diagnostico_completo.pdf", mime="application/pdf")

    