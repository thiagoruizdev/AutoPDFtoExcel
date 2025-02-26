import streamlit as st
import pandas as pd
import pdfplumber
import openpyxl
from transformers import pipeline

# Carregar um modelo pequeno para evitar problemas de memória no Streamlit Cloud
modelo_ia = pipeline("text2text-generation", model="google/flan-t5-small")

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

# 🔹 Função para a IA analisar os arquivos
def analisar_com_ia(texto_pdf, texto_excel):
    prompt = f"""
    Você é um analista bancário responsável por verificar documentos de clientes. 
    Compare as informações extraídas de um contrato bancário (PDF) com os dados cadastrados no sistema (Excel).
    
    Identifique:
    - ✅ Informações que batem (iguais nos dois documentos)
    - ❌ Informações divergentes (dados diferentes entre os documentos)
    - ⚠️ Informações que faltam (estão no Excel mas não no PDF)

    **📄 Conteúdo do PDF extraído:**
    {texto_pdf}

    **📊 Conteúdo do Excel extraído:**
    {texto_excel}

    Gere uma análise clara e objetiva, como um relatório bancário.
    """

    resposta = modelo_ia(prompt, max_length=500, do_sample=True)
    return resposta[0]["generated_text"]

# 🔹 Interface do Streamlit
st.title("📑 Comparador de Cartas Bancárias com IA (Gratuita)")

# Upload do PDF e do Excel
pdf_file = st.file_uploader("📄 Envie o PDF da carta bancária", type=["pdf"])
xlsx_modelo = st.file_uploader("📊 Envie o modelo de referência (Excel)", type=["xlsx"])

if pdf_file and xlsx_modelo:
    # Extrair texto dos arquivos
    texto_pdf = extrair_texto_pdf(pdf_file)
    texto_excel = extrair_texto_excel(xlsx_modelo)

    # Chamar a IA para análise
    resultado_ia = analisar_com_ia(texto_pdf, texto_excel)

    # Exibir resultado
    st.write("📊 **Análise da IA:**")
    st.text_area("", resultado_ia, height=400)

    # Exportar análise para arquivo
    with open("analise_bancaria.txt", "w", encoding="utf-8") as file:
        file.write(resultado_ia)

    # Botão para download do relatório
    with open("analise_bancaria.txt", "rb") as file:
        st.download_button("📥 Baixar Relatório de Análise", data=file, file_name="analise_bancaria.txt", mime="text/plain")
