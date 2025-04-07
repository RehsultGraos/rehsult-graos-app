
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
import base64

# Função para gerar análise simulada
def gerar_analise_simulada(setores_areas):
    analise = "### 🤖 Análise com GPT-4 (simulada)\n\n"
    analise += "**✅ Análise Simulada:**\n\n"
    for area, setores in setores_areas.items():
        for setor, pct in setores.items():
            if pct < 50:
                analise += f"- A área de **{setor}** na categoria **{area}** apresenta baixa pontuação, indicando necessidade de atenção.\n"
            elif pct < 75:
                analise += f"- O setor de **{setor}** em **{area}** possui desempenho mediano, com possibilidade de melhoria.\n"
            else:
                analise += f"- O setor **{setor}** em **{area}** está com bom desempenho.\n"
    analise += "\n🎯 **Recomendações:**\n"
    analise += "- Revisar práticas de manejo e protocolos técnicos.\n"
    analise += "- Considerar consultoria especializada para áreas com menor desempenho.\n"
    return analise

# Leitura da planilha e limpeza dos nomes das colunas
df = pd.read_excel("Teste Chat.xlsx", sheet_name=None)
df_fert = df["Fertilidade"]
df_daninha = df["Plantas Daninhas"]
df_fert.columns = df_fert.columns.str.strip()
df_daninha.columns = df_daninha.columns.str.strip()

# Montar dicionário com perguntas
def carregar_perguntas(df_area):
    perguntas = {}
    for _, row in df_area.iterrows():
        perguntas[str(row["ID"]).strip()] = row.to_dict()
    return perguntas

# Função de relatório em PDF (simplificada)
def gerar_pdf_simples(analise):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, analise)
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# Streamlit interface
st.set_page_config(page_title="Rehsult Grãos", layout="centered")
st.image("LOGO REAGRO TRATADA.png", width=200)
st.title("Rehsult Grãos")
st.markdown("Versão com GPT-4 (simulada) integrada ao diagnóstico")

if "area_atual" not in st.session_state:
    st.session_state.area_atual = None
if "respostas" not in st.session_state:
    st.session_state.respostas = {}
if "pergunta_atual" not in st.session_state:
    st.session_state.pergunta_atual = "1"

area = st.radio("Qual área deseja avaliar?", ["Fertilidade", "Plantas Daninhas"])

df_area = df_fert if area == "Fertilidade" else df_daninha
perguntas_dict = carregar_perguntas(df_area)

# Lógica de perguntas
if st.session_state.pergunta_atual in perguntas_dict:
    pergunta = perguntas_dict[st.session_state.pergunta_atual]
    st.markdown(f"**{pergunta['Pergunta']}**")
    resposta = st.radio("Selecione:", ["Sim", "Não", "Não sei"], key=st.session_state.pergunta_atual)
    if st.button("Próxima"):
        st.session_state.respostas[st.session_state.pergunta_atual] = resposta
        proxima = str(pergunta["Próxima (Sim)"]) if resposta == "Sim" else str(pergunta["Próxima (Não)"])
        if proxima.lower() != "nan":
            st.session_state.pergunta_atual = proxima
        else:
            st.session_state.pergunta_atual = None

# Relatório final
if st.session_state.pergunta_atual is None:
    st.success("✅ Diagnóstico Concluído")
    df_resultado = df_area[df_area["ID"].astype(str).isin(st.session_state.respostas.keys())].copy()
    df_resultado["Resposta"] = df_resultado["ID"].astype(str).map(st.session_state.respostas)
    mapa = {"Sim": 1, "Não": 0, "Não sei": 0.5}
    df_resultado["Score"] = df_resultado["Resposta"].map(mapa) * df_resultado["Peso"]
    
    setor_scores = df_resultado.groupby("Setor")["Score"].sum()
    setor_pesos = df_resultado.groupby("Setor")["Peso"].sum()
    radar_data = (setor_scores / setor_pesos * 100).fillna(0)
    
    setores_por_area = {area: radar_data.to_dict()}

    st.markdown("## 📊 Resultados")
    st.write(radar_data)

    # Gerar Análise com GPT-4 (Simulada)
    analise = gerar_analise_simulada(setores_por_area)
    st.markdown("---")
    st.markdown(analise)

    # PDF download
    pdf_buffer = gerar_pdf_simples(analise)
    st.download_button("📄 Baixar Relatório PDF", data=pdf_buffer, file_name="relatorio_diagnostico.pdf")
