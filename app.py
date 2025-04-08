
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Função para gerar gráfico radar corrigida
def gerar_grafico_radar(setores, area):
    st.subheader(f"📊 Resultados - {area}")
    valores = list(setores.values())
    labels = list(setores.keys())

    # Verificação de integridade
    if len(valores) != len(labels):
        st.warning("⚠️ Inconsistência no gráfico: número de valores e setores não coincidem.")
        return

    valores += valores[:1]
    labels += labels[:1]
    angulos = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angulos += angulos[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angulos, valores, marker='o')
    ax.fill(angulos, valores, alpha=0.25)
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(labels)
    ax.set_yticklabels([])
    ax.set_title(f"Radar - {area}", size=16, pad=20)

    st.pyplot(fig)

# Exemplo de uso
st.title("🌱 Rehsult Grãos")
st.markdown("Versão com GPT-4 (simulada) integrada ao diagnóstico")

# Exemplo de setores com valores simulados
setores_exemplo = {
    "Pré-emergente": 60,
    "Cobertura": 75,
    "Pós-emergente": 90
}

gerar_grafico_radar(setores_exemplo, "Plantas Daninhas")
