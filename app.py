
import streamlit as st
import pandas as pd

# Título
st.set_page_config(page_title="Rehsult Grãos", layout="wide")
st.markdown("## 🌱 Rehsult Grãos")
st.markdown("### Diagnóstico de fazendas produtoras de grãos com análise simulada GPT-4")

# Inicializar sessão
if "pagina" not in st.session_state:
    st.session_state.pagina = "inicio"
if "area_atual" not in st.session_state:
    st.session_state.area_atual = None
if "pergunta_id" not in st.session_state:
    st.session_state.pergunta_id = 1
if "respostas" not in st.session_state:
    st.session_state.respostas = {}

# Carregar planilhas
df_daninha = pd.read_excel("Teste Chat.xlsx", sheet_name="Planta Daninha")
df_fertilidade = pd.read_excel("Teste Chat.xlsx", sheet_name="Fertilidade")

# Unir planilhas para facilitar o acesso por área
planilhas = {
    "Plantas Daninhas": df_daninha,
    "Fertilidade": df_fertilidade
}

# Página de início
if st.session_state.pagina == "inicio":
    st.subheader("Qual área deseja começar?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌿 Planta Daninha"):
            st.session_state.area_atual = "Plantas Daninhas"
            st.session_state.pagina = "diagnostico"
            st.session_state.pergunta_id = 1
            st.experimental_rerun()
    with col2:
        if st.button("🧪 Fertilidade"):
            st.session_state.area_atual = "Fertilidade"
            st.session_state.pagina = "diagnostico"
            st.session_state.pergunta_id = 1
            st.experimental_rerun()

# Página de diagnóstico
elif st.session_state.pagina == "diagnostico":
    df_area = planilhas[st.session_state.area_atual]
    pergunta_atual = df_area[df_area["Referência"] == st.session_state.pergunta_id]

    if pergunta_atual.empty:
        st.success("✅ Diagnóstico Finalizado!")
        st.session_state.pagina = "resultado"
        st.experimental_rerun()
    else:
        row = pergunta_atual.iloc[0]
        # Verificar se deve ser exibida (caso tenha vínculo)
        if pd.notna(row["Vínculo"]):
            ref = int(row["Vínculo"])
            if st.session_state.respostas.get(ref, {}).get("Resposta") != "Sim":
                st.session_state.pergunta_id = int(row["Sim"]) if pd.notna(row["Sim"]) else None
                st.experimental_rerun()

        st.subheader(f"📋 {row['Pergunta']}")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✅ Sim"):
                st.session_state.respostas[row["Referência"]] = {"Resposta": "Sim", "Setor": row["Setor"], "Peso": row["Peso"], "Correta": row["Resposta"] == "Sim"}
                st.session_state.pergunta_id = int(row["Sim"]) if pd.notna(row["Sim"]) else None
                st.experimental_rerun()
        with col2:
            if st.button("❌ Não"):
                st.session_state.respostas[row["Referência"]] = {"Resposta": "Não", "Setor": row["Setor"], "Peso": row["Peso"], "Correta": row["Resposta"] == "Não"}
                st.session_state.pergunta_id = int(row["Não"]) if pd.notna(row["Não"]) else None
                st.experimental_rerun()
        with col3:
            if st.button("🤷 Não sei"):
                st.session_state.respostas[row["Referência"]] = {"Resposta": "Não sei", "Setor": row["Setor"], "Peso": row["Peso"], "Correta": False}
                st.session_state.pergunta_id = int(row["Não"]) if pd.notna(row["Não"]) else None
                st.experimental_rerun()

# Resultado
elif st.session_state.pagina == "resultado":
    st.subheader("📊 Resultados")
    resultados = {}
    for ref, r in st.session_state.respostas.items():
        setor = r["Setor"]
        if setor not in resultados:
            resultados[setor] = {"corretas": 0, "total": 0}
        if r["Correta"]:
            resultados[setor]["corretas"] += r["Peso"]
        resultados[setor]["total"] += r["Peso"]
    
    for setor, dados in resultados.items():
        score = (dados["corretas"] / dados["total"]) * 100 if dados["total"] > 0 else 0
        st.write(f"✅ **{setor}**: {score:.1f}% de aproveitamento.")
