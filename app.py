
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
import os

def gerar_analise_gpt4(setores_areas):
    prompt = "Você é um especialista em agronomia. Com base na pontuação percentual por setor abaixo, gere uma análise de pontos de atenção e sugestões de melhoria:\n"
    for area, setores in setores_areas.items():
        prompt += f"Área: {area}\n"
        for setor, pct in setores.items():
            prompt += f"- {setor}: {pct:.1f}%\n"
        prompt += "\n"
    prompt += "Baseado nesses dados, identifique os setores com menor pontuação e escreva uma análise explicando o que esses resultados indicam e o que pode ser feito para melhorar."

    # Simulação de resposta para teste sem API
    return (
        "✅ Análise Simulada:

"
        "- A área de **Calagem e Gessagem** apresenta baixa pontuação, indicando a necessidade de correção da acidez do solo.
"
        "- O setor de **Pré-emergente** nas plantas daninhas foi um dos mais críticos, sugerindo que o controle inicial está falhando.
"
        "- A aplicação de **macronutrientes** está razoável, mas pode ser otimizada para elevar a produtividade da soja.

"
        "🎯 Recomendações:
"
        "- Realizar análise de solo completa e aplicar calcário/gesso conforme recomendação.
"
        "- Revisar o protocolo de pré-emergência e considerar produtos com maior residual.
"
        "- Ajustar doses de macronutrientes conforme exigência da cultura e análise de solo."
    )

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

def calcular_scores_por_setor(df_resultado):
    setores = df_resultado["Setor"].unique()
    setores_score = {{setor: 0 for setor in setores}}
    setores_peso = {{setor: 0 for setor in setores}}
    
    mapa = {{
        "Sim": 1,
        "Não": 0,
        "Não sei": 0.5
    }}

    for _, row in df_resultado.iterrows():
        score = mapa.get(row["Resposta"], 0) * row["Peso"]
        setores_score[row["Setor"]] += score
        setores_peso[row["Setor"]] += row["Peso"]

    porcentagens = {{
        setor: round((setores_score[setor] / setores_peso[setor]) * 100, 1) if setores_peso[setor] > 0 else 0
        for setor in setores
    }}
    return porcentagens

st.set_page_config(page_title="Rehsult Grãos", layout="centered")
st.title("🌾 Rehsult Grãos")
st.markdown("Diagnóstico com questionário interativo e análise automática")

df_resultado = pd.DataFrame({{
    "Setor": ["Análise de Solo", "Calagem e Gessagem", "Macronutrientes", "Pré-emergente", "Cobertura"],
    "Resposta": ["Sim", "Não", "Sim", "Não", "Sim"],
    "Peso": [1, 2, 1.5, 2, 1.5]
}})

pontuacoes = calcular_scores_por_setor(df_resultado)
setores_por_area = {{
    "Fertilidade": {{
        "Análise de Solo": pontuacoes.get("Análise de Solo", 0),
        "Calagem e Gessagem": pontuacoes.get("Calagem e Gessagem", 0),
        "Macronutrientes": pontuacoes.get("Macronutrientes", 0)
    }},
    "Plantas Daninhas": {{
        "Pré-emergente": pontuacoes.get("Pré-emergente", 0),
        "Cobertura": pontuacoes.get("Cobertura", 0)
    }}
}}

if st.button("✅ Finalizar Diagnóstico e Gerar Relatório"):
    st.subheader("📊 Diagnóstico Concluído")
    st.markdown("### 🤖 Análise com GPT-4")
    analise = gerar_analise_gpt4(setores_por_area)
    st.markdown(analise)

    st.markdown("---")
    st.success("📄 Relatório disponível para download:")
    pdf_data = gerar_pdf_relatorio(analise)
    st.download_button("📥 Baixar Relatório em PDF", data=pdf_data, file_name="relatorio_diagnostico.pdf")
