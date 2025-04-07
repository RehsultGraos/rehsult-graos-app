
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
import openai

# CONFIGURAÇÃO DA CHAVE GPT
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
