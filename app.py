
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="Rehsult Grãos - Diagnóstico", layout="centered")

# Logo fixa em todas as telas
st.image("LOGO REAGRO TRATADA.png", width=200)

# Inicialização de sessão
st.session_state.setdefault("inicio", False)
st.session_state.setdefault("respostas", {"Fertilidade": {}, "Plantas Daninhas": {}})
st.session_state.setdefault("pergunta_atual", None)
st.session_state.setdefault("area_atual", None)
st.session_state.setdefault("area_finalizada", False)
st.session_state.setdefault("finalizado", False)
st.session_state.setdefault("areas_respondidas", [])
st.session_state.setdefault("aguardando_decisao", False)

# Tela inicial
if not st.session_state.inicio:
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
        st.session_state.area_finalizada = False
        st.session_state.aguardando_decisao = False

# Diagnóstico
elif st.session_state.inicio and not st.session_state.area_finalizada and not st.session_state.finalizado:
    area = st.session_state.area_atual
    aba_excel = "Fertilidade" if area == "Fertilidade" else "Planta Daninha"
    df = pd.read_excel("Teste Chat.xlsx", sheet_name=aba_excel)
    df["Peso"] = pd.to_numeric(df["Peso"], errors="coerce")
    df = df.dropna(subset=["Referência", "Pergunta", "Peso"])
    df["Referência"] = df["Referência"].astype(int)
    perguntas_dict = df.set_index("Referência").to_dict(orient="index")

    ref = st.session_state.pergunta_atual
    if ref in perguntas_dict:
        dados = perguntas_dict[ref]
        resposta = st.radio(dados["Pergunta"], ["Sim", "Não", "Não sei"], key=f"{area}_ref_{ref}")
        if st.button("Responder", key=f"{area}_btn_{ref}"):
            st.session_state.respostas[area][ref] = {
                "Setor": dados["Setor"],
                "Área": dados["Área"],
                "Pergunta": dados["Pergunta"],
                "Peso": dados["Peso"],
                "Resposta": resposta
            }
            if resposta == "Sim" and not pd.isna(dados["Sim"]):
                st.session_state.pergunta_atual = int(dados["Sim"])
            elif not pd.isna(dados["Não"]):
                st.session_state.pergunta_atual = int(dados["Não"])
            else:
                st.session_state.area_finalizada = True
                st.session_state.aguardando_decisao = True
                st.session_state.areas_respondidas.append(area)

# Após a última pergunta da área
elif st.session_state.aguardando_decisao and not st.session_state.finalizado:
    outras = {"Fertilidade": "Plantas Daninhas", "Plantas Daninhas": "Fertilidade"}
    proxima = outras[st.session_state.area_atual]
    st.markdown(f"### ✅ Você concluiu as perguntas sobre *{st.session_state.area_atual}*.")
    st.markdown(f"🔄 Deseja responder também sobre **{proxima}**?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"✅ Sim, responder {proxima}"):
            st.session_state.area_atual = proxima
            df_inicio = pd.read_excel("Teste Chat.xlsx", sheet_name="Fertilidade" if proxima == "Fertilidade" else "Planta Daninha")
            df_inicio = df_inicio.dropna(subset=["Referência", "Pergunta", "Peso"])
            df_inicio["Referência"] = df_inicio["Referência"].astype(int)
            df_inicio = df_inicio.sort_values("Referência")
            st.session_state.pergunta_atual = int(df_inicio["Referência"].iloc[0])
            st.session_state.area_finalizada = False
            st.session_state.aguardando_decisao = False
    with col2:
        if st.button("❌ Não, finalizar diagnóstico"):
            st.session_state.finalizado = True

# Relatório
if st.session_state.finalizado:
    st.markdown("## ✅ Diagnóstico Concluído")
    mapa = {"Sim": 1, "Não": 0, "Não sei": 0.5}
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "Relatório de Diagnóstico - Rehsult Grãos", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Fazenda: {st.session_state.get('fazenda', '-')}", ln=True)
    pdf.cell(200, 10, f"Responsável: {st.session_state.get('responsavel', '-')}", ln=True)
    pdf.cell(200, 10, f"Produtividade média SOJA: {st.session_state.get('prod_soja', 0)} kg/ha", ln=True)
    pdf.cell(200, 10, f"Produtividade média MILHO: {st.session_state.get('prod_milho', 0)} kg/ha", ln=True)

    for area in st.session_state.areas_respondidas:
        df_resultado = pd.DataFrame(st.session_state.respostas[area]).T
        if "Resposta" not in df_resultado.columns:
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
