import streamlit as st
import pandas as pd
import pdfplumber
import openpyxl

# 🔹 Função para extrair os dados da carta bancária do PDF
def extrair_dados_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        texto_extraido = []
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                texto_extraido.append(text.strip())  # Remove espaços extras
    
    # Criar um dicionário com os dados extraídos
    dados_extraidos = {
        "Customer name": "",
        "Address": "",
        "Type of change": "",
        "Bank key": "",
        "Swift Code": "",
        "Account number": "",
        "IBAN": "",
        "Name of bank": ""
    }

    # Preenchendo os campos extraídos do texto
    for campo in dados_extraidos.keys():
        for linha in texto_extraido:
            if campo in linha:
                valor = linha.split("(*)")[-1].strip() if "(*)" in linha else linha.split(":")[-1].strip()
                dados_extraidos[campo] = valor
                break  # Para no primeiro match encontrado

    return pd.DataFrame([dados_extraidos])

# 🔹 Função para comparar com os dados do modelo (SAP)
def comparar_dados(df_extraido, df_modelo):
    df_resultado = df_modelo.copy()

    for coluna in df_extraido.columns:
        if coluna in df_modelo.columns:
            df_resultado[coluna] = df_modelo[coluna] == df_extraido[coluna][0]
            df_resultado[coluna] = df_resultado[coluna].map({True: "✅ Match", False: "❌ Não Bate"})

    return df_resultado

# 🔹 Interface do Streamlit
st.title("📑 Comparação de Cartas Bancárias")

# Upload do arquivo PDF e do modelo SAP
pdf_file = st.file_uploader("📄 Envie o PDF da carta bancária", type=["pdf"])
xlsx_modelo = st.file_uploader("📊 Envie o modelo de referência (Excel)", type=["xlsx"])

if pdf_file and xlsx_modelo:
    # Nome do Excel convertido
    output_excel = "dados_extraidos.xlsx"

    # Extrair os dados do PDF
    df_extraido = extrair_dados_pdf(pdf_file)

    # Carregar o modelo SAP
    df_modelo = pd.read_excel(xlsx_modelo, engine='openpyxl')

    # Comparar os dados
    df_resultado = comparar_dados(df_extraido, df_modelo)

    # Exibir resultado na tela
    st.write("📊 Resultado da Comparação:")
    st.dataframe(df_resultado)

    # Exportar resultado para Excel
    resultado_excel = "relatorio_diferencas.xlsx"
    df_resultado.to_excel(resultado_excel, index=False, engine='openpyxl')

    # Botão para baixar o relatório
    with open(resultado_excel, "rb") as file:
        st.download_button("📥 Baixar Relatório", data=file, file_name="relatorio_diferencas.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
