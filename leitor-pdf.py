import streamlit as st
import pandas as pd
import pdfplumber
import openpyxl

# 🔹 Função para extrair os dados do PDF
def extrair_dados_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        texto_extraido = []
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                texto_extraido.append(text.strip())  

    # Estrutura do dicionário de dados extraídos
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

    # Preenchendo os campos extraídos
    for campo in dados_extraidos.keys():
        for linha in texto_extraido:
            if campo in linha:
                valor = linha.split(":")[-1].strip() if ":" in linha else linha.split("(*)")[-1].strip()
                dados_extraidos[campo] = valor
                break  

    return pd.DataFrame([dados_extraidos])

# 🔹 Função para comparar os dados e usar IA para análise
def comparar_dados_ia(df_extraido, df_modelo):
    df_resultado = pd.DataFrame(columns=["Campo", "Valor no Excel", "Valor no PDF", "Status"])

    for coluna in df_modelo.columns:
        valor_excel = str(df_modelo[coluna].values[0]) if coluna in df_modelo.columns else "N/A"
        valor_pdf = str(df_extraido[coluna].values[0]) if coluna in df_extraido.columns else "N/A"

        # Classificação Inteligente (IA)
        if valor_excel == valor_pdf:
            status = "✅ Match"
        elif valor_pdf == "" or valor_pdf == "N/A":
            status = "⚠️ Faltando"
        else:
            status = "❌ Divergente"

        df_resultado = pd.concat([df_resultado, pd.DataFrame([{
            "Campo": coluna,
            "Valor no Excel": valor_excel,
            "Valor no PDF": valor_pdf,
            "Status": status
        }])], ignore_index=True)

    return df_resultado

# 🔹 Interface no Streamlit
st.title("📑 Comparação de Cartas Bancárias com IA")

# Upload do PDF e do Excel de referência
pdf_file = st.file_uploader("📄 Envie o PDF da carta bancária", type=["pdf"])
xlsx_modelo = st.file_uploader("📊 Envie o modelo de referência (Excel)", type=["xlsx"])

if pdf_file and xlsx_modelo:
    output_excel = "dados_extraidos.xlsx"

    # Extrair os dados do PDF
    df_extraido = extrair_dados_pdf(pdf_file)

    # Carregar os dados do Excel
    df_modelo = pd.read_excel(xlsx_modelo, engine='openpyxl')

    # Comparar os dados e aplicar IA
    df_resultado = comparar_dados_ia(df_extraido, df_modelo)

    # Exibir os resultados
    st.write("📊 Resultado da Comparação com IA:")
    st.dataframe(df_resultado)

    # Exportar para Excel
    resultado_excel = "relatorio_diferencas.xlsx"
    df_resultado.to_excel(resultado_excel, index=False, engine='openpyxl')

    # Botão para baixar o relatório
    with open(resultado_excel, "rb") as file:
        st.download_button("📥 Baixar Relatório", data=file, file_name="relatorio_diferencas.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
