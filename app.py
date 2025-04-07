
import streamlit as st

st.set_page_config(page_title="Rehsult Grãos - Diagnóstico", layout="centered")

st.title("🌾 Rehsult Grãos")
st.markdown("Versão com resposta de IA **simulada** (sem consumo de API)")

def gerar_analise_simulada(setores_areas):
    return '''
✅ Análise Simulada:
- A área de **Calagem e Gessagem** apresenta baixa pontuação, indicando a necessidade de correção da acidez do solo.
- O setor de **Pré-emergente** nas plantas daninhas foi um dos mais críticos, sugerindo que o controle inicial está falhando.
- A aplicação de **macronutrientes** está razoável, mas pode ser otimizada para elevar a produtividade da soja.

🎯 Recomendações:
- Realizar análise de solo completa e aplicar calcário/gesso conforme recomendação.
- Revisar o protocolo de pré-emergência e considerar produtos com maior residual.
- Ajustar a adubação com base nas necessidades específicas da cultura e época.'''.strip()

# Simulação de dados
setores_exemplo = {
    "Fertilidade": {"Análise de Solo": 55.0, "Calagem e Gessagem": 42.0, "Macronutrientes": 60.0},
    "Plantas Daninhas": {"Pré-emergente": 35.0, "Cobertura": 50.0}
}

if st.button("🧠 Gerar Análise de IA (Simulada)"):
    st.markdown("### 🤖 Resultado Simulado")
    st.markdown(gerar_analise_simulada(setores_exemplo))
