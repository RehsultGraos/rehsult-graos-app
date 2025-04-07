
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="Rehsult Grãos - Diagnóstico", layout="centered")

# Inicialização das variáveis de sessão
if "inicio" not in st.session_state:
    st.session_state.inicio = False
if "respostas" not in st.session_state:
    st.session_state.respostas = {}
    st.session_state.pergunta_atual = 1
    st.session_state.fim = False

# Entrada inicial
if not st.session_state.inicio:
    st.image("LOGO REAGRO TRATADA.png", width=200)
    st.title("🌾 Rehsult Grãos - Diagnóstico de Fazenda")
    st.markdown("Este é um sistema de diagnóstico para fazendas produtoras de grãos. Responda uma pergunta por vez e receba seu relatório completo.")
    
    st.text_input("Nome da Fazenda", key="fazenda")
    st.text_input("Nome do Responsável", key="responsavel")
    st.number_input("Produtividade média de SOJA (kg/ha)", min_value=0, key="prod_soja")
    st.number_input("Produtividade média de MILHO (kg/ha)", min_value=0, key="prod_milho")
    
    if st.button("Iniciar Diagnóstico"):
        st.session_state.inicio = True

# Diagnóstico
if st.session_state.inicio:
    st.image("LOGO REAGRO TRATADA.png", width=150)

    df_fert = pd.read_excel("Teste Chat.xlsx", sheet_name="Fertilidade")
    df_planta = pd.read_excel("Teste Chat.xlsx", sheet_name="Planta Daninha")
    df = pd.concat([df_fert, df_planta], ignore_index=True)
    df["Peso"] = pd.to_numeric(df["Peso"], errors="coerce")
    df = df.dropna(subset=["Referência", "Pergunta", "Peso"])
    df["Referência"] = df["Referência"].astype(int)
    perguntas_dict = df.set_index("Referência").to_dict(orient="index")

    ref = st.session_state.pergunta_atual
    if not st.session_state.fim and ref in perguntas_dict:
        dados = perguntas_dict[ref]
        resposta = st.radio(dados["Pergunta"], ["Sim", "Não", "Não sei"], key=f"ref_{ref}")
        if st.button("Responder", key=f"btn_{ref}"):
            st.session_state.respostas[ref] = {
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
                st.session_state.fim = True
    else:
        st.session_state.fim = True

# Final do diagnóstico
if st.session_state.fim and st.session_state.inicio:
    st.markdown("## ✅ Diagnóstico Concluído")
    df_resultado = pd.DataFrame(st.session_state.respostas).T

    # Regras específicas: se resposta da 35 for 'Não', 36, 40 e 41 devem ser tratadas
    resposta_35 = st.session_state.respostas.get(35, {}).get("Resposta")
    ignorar_40_41 = resposta_35 == "Não"
    
    def aplicar_peso(row):
        if row.name in [40, 41] and ignorar_40_41:
            return 0
        if row.name == 36 and resposta_35 == "Não":
            return 0
        return row["Peso"]

    df_resultado["Peso Ajustado"] = df_resultado.apply(aplicar_peso, axis=1)

    mapa = {"Sim": 1, "Não": 0, "Não sei": 0.5}
    df_resultado["Score"] = df_resultado["Resposta"].map(mapa) * df_resultado["Peso Ajustado"]

    setores = df_resultado.groupby("Setor").agg({"Score": "sum", "Peso Ajustado": "sum"})
    setores["Percentual"] = (setores["Score"] / setores["Peso Ajustado"]) * 100
    nota_geral = (df_resultado["Score"].sum() / df_resultado["Peso Ajustado"].sum()) * 100
    st.markdown(f"### Pontuação Geral da Fazenda: **{nota_geral:.1f}%**")

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
    ax.set_title("Desempenho por Setor")
    st.pyplot(fig)

    pior_setores = setores.sort_values("Percentual").head(3)
    st.markdown("### Tópicos a Melhorar:")
    for setor, linha in pior_setores.iterrows():
        st.write(f"- {setor}: {linha['Percentual']:.1f}%")

    # PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "Relatório de Diagnóstico - Rehsult Grãos", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Fazenda: {st.session_state.get('fazenda', 'NÃO INFORMADO')}", ln=True)
    pdf.cell(200, 10, f"Responsável: {st.session_state.get('responsavel', 'NÃO INFORMADO')}", ln=True)
    pdf.cell(200, 10, f"Produtividade média SOJA: {st.session_state.get('prod_soja', 0)} kg/ha", ln=True)
    pdf.cell(200, 10, f"Produtividade média MILHO: {st.session_state.get('prod_milho', 0)} kg/ha", ln=True)
    pdf.cell(200, 10, f"Pontuação Geral: {nota_geral:.1f}%", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, "Desempenho por Setor:", ln=True)
    for setor, linha in setores.iterrows():
        pdf.cell(200, 10, f"- {setor}: {linha['Percentual']:.1f}%", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, "Tópicos a Melhorar:", ln=True)
    for setor, linha in pior_setores.iterrows():
        pdf.cell(200, 10, f"- {setor}: {linha['Percentual']:.1f}%", ln=True)

    pdf_buffer = BytesIO()
    pdf_buffer.write(pdf.output(dest='S').encode('latin1'))
    pdf_buffer.seek(0)

    st.download_button("📄 Baixar Relatório em PDF", data=pdf_buffer.getvalue(), file_name="relatorio_rehsult_graos.pdf", mime="application/pdf")
