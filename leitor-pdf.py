import streamlit as st
import pandas as pd
import pdfplumber
import openpyxl
import google.generativeai as genai

# 🔹 Configure a chave da API do Google Gemini
GOOGLE_API_KEY = "AIzaSyDHwa3byfd3rS9DNTlSSPKkcxGkLv2cIMg"
genai.configure(api_key=GOOGLE_API_KEY)

# 🔹 Função para extrair texto do PDF
def extrair_texto_pdf(pdf_path):
    texto_extraido = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                texto_extraido.append(text.strip())  
    return "\n".join(texto_extraido)

# 🔹 Função para extrair dados do Excel
def extrair_texto_excel(excel_path):
    df = pd.read_excel(excel_path, engine="openpyxl")
    return df.to_string(index=False)

# 🔹 Função para analisar os arquivos com Gemini Pro
def analisar_com_gemini(texto_pdf, texto_excel):
    prompt = f"""
    Você é um analista bancário. Sua tarefa é comparar um contrato bancário (PDF) com os registros oficiais em um arquivo Excel.

    **📄 Dados extraídos do PDF:**
    {texto_pdf}

    **📊 Dados extraídos do Excel:**
    {texto_excel}

    Gere um relatório estruturado com:
    ✅ Informações que batem
    ❌ Informações divergentes
    ⚠️ Informações faltando
    """

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text

# 🔹 Interface do Streamlit
st.title("📑 Comparador de Cartas Bancárias com IA (Gemini Pro)")

# Upload dos arquivos
pdf_file = st.file_uploader("📄 Envie o PDF da carta bancária", type=["pdf"])
xlsx_modelo = st.file_uploader("📊 Envie o modelo de referência (Excel)", type=["xlsx"])

if pdf_file and xlsx_modelo:
    if st.button("🔍 Analisar"):
        # Extrair textos
        texto_pdf = extrair_texto_pdf(pdf_file)
        texto_excel = extrair_texto_excel(xlsx_modelo)

        # Chamar a IA para análise
        resultado_ia = analisar_com_gemini(texto_pdf, texto_excel)

        # Melhorando a formatação do texto retornado
        resultado_formatado = resultado_ia.replace("✅", "\n✅").replace("❌", "\n❌").replace("⚠️", "\n⚠️")

        # Exibir resultado de forma organizada
        st.subheader("📊 Análise da IA:")
        st.text_area("", resultado_formatado, height=400)

        # Salvar a análise em um arquivo
        with open("analise_bancaria.txt", "w", encoding="utf-8") as file:
            file.write(resultado_formatado)

        # Botão para baixar o relatório
        with open("analise_bancaria.txt", "rb") as file:
            st.download_button("📥 Baixar Relatório", data=file, file_name="analise_bancaria.txt", mime="text/plain")
