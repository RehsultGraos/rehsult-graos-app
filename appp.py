
# Protótipo do backend do Rehsult Grãos
# App web com Streamlit simulando a experiência de respostas e relatório

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.backends.backend_pdf import PdfPages

st.set_page_config(page_title="Rehsult Grãos - Diagnóstico", layout="centered")
st.title("🌾 Rehsult Grãos - Diagnóstico de Fazenda")

# Logo
st.image("https://tecnocoffeeapi.rehagro.com.br/storage/imagens/rehagro.png", width=200)

st.markdown("""
**Bem-vindo ao Rehsult Grãos!**

Este é um sistema de diagnóstico para fazendas produtoras de grãos. Ao responder este questionário, você receberá um relatório com sua pontuação geral, análise por setor técnico e recomendações de melhoria.
""")

# Dados iniciais
fazenda = st.text_input("Nome da Fazenda")
responsavel = st.text_input("Nome do Responsável")

start = st.button("Iniciar Diagnóstico")

if start:
    df_fert = pd.read_excel("Teste Chat.xlsx", sheet_name="Fertilidade")
    df_planta = pd.read_excel("Teste Chat.xlsx", sheet_name="Planta Daninha")
    df = pd.concat([df_fert, df_planta], ignore_index=True)
    df = df[["Setor", "Pergunta", "Nota"]].dropna()
    df["Nota"] = pd.to_numeric(df["Nota"], errors="coerce")

    respostas = []
    for i, row in df.iterrows():
        resposta = st.radio(row["Pergunta"], ["Sim", "Não", "Não sei"], key=i)
        respostas.append(resposta)

    if st.button("Finalizar e Gerar Relatório"):
        df["Resposta"] = respostas
        mapa = {"Sim": 1, "Não": 0, "Não sei": 0.5}
        df["Score"] = df["Resposta"].map(mapa) * df["Nota"]

        setores = df.groupby("Setor").agg({"Score": "sum", "Nota": "sum"})
        setores["Percentual"] = (setores["Score"] / setores["Nota"]) * 100

        # Pontuação Geral
        nota_geral = (df["Score"].sum() / df["Nota"].sum()) * 100
        st.markdown(f"## Pontuação Geral: **{nota_geral:.1f}%**")

        # Gráfico Radar
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

        # Pontos a melhorar
        st.markdown("## Tópicos a Melhorar:")
        pior_setores = setores.sort_values("Percentual").head(3)
        for setor, linha in pior_setores.iterrows():
            st.write(f"- {setor}: {linha['Percentual']:.1f}%")

        st.success("Diagnóstico finalizado com sucesso!")
