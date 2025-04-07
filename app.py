
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
from openai import OpenAI
import os
from dotenv import load_dotenv

st.set_page_config(page_title="Rehsult Grãos - Diagnóstico", layout="centered")

# Carregar variável de ambiente
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def gerar_analise_ia(setores_areas):
    prompt = '''Você é um especialista em agronomia. Com base na pontuação percentual por setor abaixo, gere uma análise de pontos de atenção e sugestões de melhoria:

'''
    for area, setores in setores_areas.items():
        prompt += f"Área: {area}\n"
        for setor, pct in setores.items():
            prompt += f"- {setor}: {pct:.1f}%\n"
        prompt += "\n"

    prompt += "Baseado nesses dados, identifique os setores com menor pontuação e escreva uma análise explicando o que esses resultados indicam e o que pode ser feito para melhorar."

    try:
        resposta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um consultor agrícola especialista em análise de dados de fazendas."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        return resposta.choices[0].message.content
    except Exception as e:
        return f"Erro ao gerar análise com IA: {str(e)}"

st.title("🌾 Rehsult Grãos")
st.markdown("Versão com GPT-3.5 integrada")

setores_exemplo = {
    "Fertilidade": {"Análise de Solo": 55.0, "Calagem e Gessagem": 42.0, "Macronutrientes": 60.0},
    "Plantas Daninhas": {"Pré-emergente": 35.0, "Cobertura": 50.0}
}

if st.button("🧠 Gerar Análise de IA (teste)"):
    st.markdown("### 🤖 Análise com GPT-3.5")
    resposta = gerar_analise_ia(setores_exemplo)
    st.write(resposta)
