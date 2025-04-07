
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
import openai

st.set_page_config(page_title="Rehsult Grãos - Diagnóstico", layout="centered")

# Configuração da chave da OpenAI
openai.api_key = "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"

def gerar_analise_ia(setores_areas):
    prompt = """Você é um especialista em agronomia. Com base na pontuação percentual por setor abaixo, gere uma análise de pontos de atenção e sugestões de melhoria:

"""
    for area, setores in setores_areas.items():
        prompt += f"Área: {area}\n"
        for setor, pct in setores.items():
            prompt += f"- {setor}: {pct:.1f}%\n"
        prompt += "\n"

    prompt += "Baseado nesses dados, identifique os setores com menor pontuação e escreva uma análise explicando o que esses resultados indicam e o que pode ser feito para melhorar."

    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um consultor agrícola especialista em análise de dados de fazendas."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        return resposta["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erro ao gerar análise com IA: {str(e)}"

# Garantir conteúdo na tela
st.title("🌾 Rehsult Grãos")
st.markdown("Versão com GPT-4 integrada ao diagnóstico")

# Verificação básica da API (teste se aparece algo)
try:
    models = openai.Model.list()
    st.success("✅ GPT-4 conectado com sucesso!")
except Exception as err:
    st.error("Erro na conexão com OpenAI: " + str(err))

# Exemplo simulado (para forçar renderização da IA)
setores_exemplo = {
    "Fertilidade": {"Análise de Solo": 55.0, "Calagem e Gessagem": 42.0, "Macronutrientes": 60.0},
    "Plantas Daninhas": {"Pré-emergente": 35.0, "Cobertura": 50.0}
}

if st.button("🧠 Gerar Análise de IA (teste)"):
    st.markdown("### 🤖 Análise com GPT-4")
    resposta = gerar_analise_ia(setores_exemplo)
    st.write(resposta)
