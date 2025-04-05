import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
import base64

# Configuração da página
st.set_page_config(page_title="Rehsult Grãos - Diagnóstico", layout="centered")
st.title("🌾 Rehsult Grãos - Diagnóstico de Fazenda")

# Logo
st.image("https://tecnocoffeeapi.rehagro.com.br/storage/imagens/rehagro.png", width=150)

# Dados do Excel
@st.cache_data
def carregar_dados():
    df = pd.read_excel("Teste Chat.xlsx", sheet_name=None)
    perguntas_df = df['Perguntas']
    setores_df = df['Setores']
    return perguntas_df, setores_df

perguntas_df, setores_df = carregar_dados()

# Inicialização do estado
if 'fase' not in st.session_state:
    st.session_state.fase = 'inicio'
if 'respostas' not in st.session_state:
    st.session_state.respostas = {}
if 'indice_pergunta' not in st.session_state:
    st.session_state.indice_pergunta = 0

# Perguntas iniciais
if st.session_state.fase == 'inicio':
    st.subheader("Bem-vindo ao Rehsult Grãos!")
    st.write("Este é um sistema de diagnóstico para fazendas produtoras de grãos. Você responderá uma pergunta por vez, e ao final, verá um relatório com pontuação geral, gráfico de radar e recomendações.")

    st.session_state.fazenda = st.text_input("Nome da Fazenda")
    st.session_state.responsavel = st.text_input("Nome do Responsável")
    st.session_state.prod_soja = st.number_input("Produtividade da última safra de soja (sc/ha):", min_value=0)
    st.session_state.prod_milho = st.number_input("Produtividade da última safra de milho (sc/ha):", min_value=0)

    if st.button("Iniciar Diagnóstico"):
        st.session_state.fase = 'perguntas'
        st.rerun()

# Função para verificar dependências

def deve_exibir(pergunta):
    if pd.isna(pergunta['Pergunta condicional']):
        return True
    id_cond = int(pergunta['Pergunta condicional'])
    valor_cond = pergunta['Valor condicional']
    return st.session_state.respostas.get(id_cond) == valor_cond

# Lógica das perguntas
if st.session_state.fase == 'perguntas':
    perguntas_filtradas = perguntas_df[perguntas_df.apply(deve_exibir, axis=1)]

    if st.session_state.indice_pergunta < len(perguntas_filtradas):
        pergunta = perguntas_filtradas.iloc[st.session_state.indice_pergunta]
        st.write(pergunta['Pergunta'])
        resposta = st.radio("", ["Sim", "Não", "Não sei"], key=pergunta['ID'])

        if st.button("Responder"):
            st.session_state.respostas[pergunta['ID']] = resposta
            st.session_state.indice_pergunta += 1
            st.rerun()
    else:
        st.session_state.fase = 'resultado'
        st.rerun()

# Fase de resultados
if st.session_state.fase == 'resultado':
    st.subheader("Resultados do Diagnóstico")

    # Cálculo das notas por setor
    perguntas_df['Respondida'] = perguntas_df['ID'].apply(lambda x: x in st.session_state.respostas)
    perguntas_df['Valor'] = perguntas_df['ID'].apply(lambda x: st.session_state.respostas.get(x))

    def pontuar(row):
        if not row['Respondida']:
            return 0
        if row['Valor'] == 'Sim':
            return row['Nota']
        elif row['Valor'] == 'Não sei':
            return 0
        return 0

    perguntas_df['Nota obtida'] = perguntas_df.apply(pontuar, axis=1)
    setores = perguntas_df.groupby('Setor').agg({'Nota obtida': 'sum', 'Nota': 'sum', 'Respondida': 'sum'})
    setores = setores[setores['Respondida'] > 0]  # remove setores não respondidos
    setores['Pontuacao'] = (setores['Nota obtida'] / setores['Nota'] * 100).round(0)

    nota_geral = (setores['Nota obtida'].sum() / setores['Nota'].sum()) * 100
    nota_geral = round(nota_geral)

    st.markdown(f"**Pontuação Geral da Fazenda:** {nota_geral}/100")

    # Classificação da produtividade
    def classificar_soja(p):
        if p < 65: return "Baixa"
        elif p <= 75: return "Média"
        elif p <= 90: return "Alta"
        return "Muito Alta"

    def classificar_milho(p):
        if p < 170: return "Baixa"
        elif p <= 190: return "Média"
        elif p <= 205: return "Alta"
        return "Muito Alta"

    soja_txt = classificar_soja(st.session_state.prod_soja)
    milho_txt = classificar_milho(st.session_state.prod_milho)

    st.write(f"Produtividade da Soja: {st.session_state.prod_soja} sc/ha - {soja_txt}")
    st.write(f"Produtividade do Milho: {st.session_state.prod_milho} sc/ha - {milho_txt}")

    # Radar
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    categorias = setores.index.tolist()
    valores = setores['Pontuacao'].tolist()
    categorias += [categorias[0]]
    valores += [valores[0]]
    angulos = np.linspace(0, 2 * np.pi, len(categorias))
    ax.plot(angulos, valores, 'g')
    ax.fill(angulos, valores, alpha=0.25)
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(categorias, fontsize=8)
    ax.set_title("Desempenho por Setor")
    st.pyplot(fig)

    # Sugestão por IA
    sugestoes = []
    for i, row in setores.iterrows():
        if row['Pontuacao'] < 60:
            sugestoes.append(f"O setor {i} teve desempenho abaixo do esperado. Avaliar melhores práticas pode ajudar na evolução.")

    st.markdown("### Recomendações por IA")
    for s in sugestoes:
        st.markdown(f"- {s}")

    # Geração do PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(190, 10, "Relatório de Diagnóstico - Rehsult Grãos", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Fazenda: {st.session_state.fazenda}", ln=True)
    pdf.cell(200, 10, f"Responsável: {st.session_state.responsavel}", ln=True)
    pdf.cell(200, 10, f"Pontuação Geral: {nota_geral}/100", ln=True)
    pdf.cell(200, 10, f"Produtividade da Soja: {st.session_state.prod_soja} sc/ha - {soja_txt}", ln=True)
    pdf.cell(200, 10, f"Produtividade do Milho: {st.session_state.prod_milho} sc/ha - {milho_txt}", ln=True)
    pdf.ln(5)
    for s in sugestoes:
        pdf.multi_cell(0, 10, f"- {s}")

    # Salva gráfico no buffer
    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    buffer.seek(0)
    pdf.image(buffer, x=10, y=None, w=180)

    # Download
    pdf_out = BytesIO()
    pdf.output(pdf_out)
    st.download_button("📄 Baixar Relatório em PDF", data=pdf_out.getvalue(), file_name="diagnostico_fazenda.pdf", mime="application/pdf")
