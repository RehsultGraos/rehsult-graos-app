import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# Carregar dados
@st.cache
def carregar_dados():
    # Ajuste para garantir que a planilha seja lida corretamente
    df = pd.read_excel('Teste Chat.xlsx', sheet_name='Fertilidade')  # Altere para o caminho correto se necessário
    return df

# Função para classificar as produtividades
def classificar_produtividade(valor, cultura):
    if cultura == 'Soja':
        if valor < 65:
            return 'Baixa'
        elif 65.1 <= valor <= 75:
            return 'Média'
        elif 75.1 <= valor <= 90:
            return 'Alta'
        else:
            return 'Muito Alta'
    elif cultura == 'Milho':
        if valor < 170:
            return 'Baixa'
        elif 171 <= valor <= 190:
            return 'Média'
        elif 191 <= valor <= 205:
            return 'Alta'
        else:
            return 'Muito Alta'

# Função para exibir o gráfico radar
def gerar_grafico(setores, notas):
    fig, ax = plt.subplots(figsize=(6, 6), dpi=80)
    ax.set_theta_offset(0.5 * np.pi)
    ax.set_theta_direction(-1)
    
    categorias = setores
    valores = notas

    ax.plot(categorias, valores, color='green', linewidth=3)
    ax.fill(categorias, valores, color='green', alpha=0.3)

    ax.set_xticklabels(categorias, fontsize=8)
    ax.set_yticklabels([f'{x}%' for x in range(0, 101, 20)], fontsize=8)
    plt.title("Desempenho por Setor", size=14)
    return fig

# Função para gerar PDF
def gerar_pdf():
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Inserir informações no PDF
    pdf.cell(200, 10, txt="Relatório de Diagnóstico - Rehsult Grãos", ln=True, align="C")
    pdf.cell(200, 10, txt=f"Fazenda: {st.session_state.fazenda}", ln=True)
    pdf.cell(200, 10, txt=f"Responsável: {st.session_state.responsavel}", ln=True)
    pdf.cell(200, 10, txt=f"Pontuação Geral: {st.session_state.pontuacao}%", ln=True)

    # Inserir gráfico
    img_buffer = BytesIO()
    fig = gerar_grafico(st.session_state.setores, st.session_state.notas)
    fig.savefig(img_buffer, format="png")
    img_buffer.seek(0)
    pdf.image(img_buffer, x=10, y=50, w=190)

    # Gerar o arquivo PDF
    return pdf.output(dest='S').encode('latin1')

# Interface com o usuário
def main():
    st.set_page_config(page_title="Rehsult Grãos - Diagnóstico", layout="centered")
    
    st.title("🌾 Rehsult Grãos - Diagnóstico de Fertilidade")

    # Receber informações sobre a fazenda
    st.session_state.fazenda = st.text_input('Nome da Fazenda')
    st.session_state.responsavel = st.text_input('Nome do Responsável')

    # Receber a produtividade de soja e milho
    soja_produtividade = st.number_input('Produtividade de Soja (safra passada)', min_value=0)
    milho_produtividade = st.number_input('Produtividade de Milho (safra passada)', min_value=0)

    # Classificar as produtividades
    soja_classificacao = classificar_produtividade(soja_produtividade, 'Soja')
    milho_classificacao = classificar_produtividade(milho_produtividade, 'Milho')

    st.write(f"Classificação de Soja: {soja_classificacao}")
    st.write(f"Classificação de Milho: {milho_classificacao}")

    # Carregar os dados e exibir a tabela
    df = carregar_dados()
    st.write(df)

    # Lógica de vínculo (dependendo da resposta, mostrar as perguntas seguintes)
    # Exemplo de vínculo: Perguntas que dependem de respostas anteriores
    if pd.notna(df.iloc[10]['G']):
        st.write("Exibindo pergunta vinculada 10")
        # Adicione aqui a lógica para exibir a pergunta 10, dependendo da resposta

    # Gerar o gráfico e PDF quando o usuário finalizar
    if st.button('Gerar Relatório'):
        st.session_state.setores = ['Adubação Orgânica', 'Análise de Solo', 'Fertilizantes', 'Manutenção de Áreas']  # Exemplo de setores
        st.session_state.notas = [80, 70, 90, 60]  # Exemplo de notas
        pdf_output = gerar_pdf()
        
        st.download_button("Baixar Relatório PDF", data=pdf_output, file_name="relatorio_fazenda.pdf", mime="application/pdf")

if __name__ == "__main__":
    main()

