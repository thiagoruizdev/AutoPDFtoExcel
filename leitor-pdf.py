import streamlit as st
import pandas as pd
import pdfplumber
import openpyxl
from transformers import pipeline

# 🔹 Carregar um modelo leve para rodar localmente sem precisar de API
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
    Você é um analista bancário. Compare os dados extraídos do PDF com o Excel.
    
    Identifique:
    - ✅ Informações que batem (iguais nos dois documentos)
    - ❌ Informações divergentes (dados diferentes entre os documentos)
    - ⚠️ Informações que faltam (estão no Excel, mas não no PDF)

    **📄 Dados extraídos do PDF:**
    {texto_pdf}

    **📊 Dados extraídos do Excel:**
    {texto_excel}

    Gere uma análise detalhada e estruturada.
    """

    resposta = modelo_ia(prompt, max_length=500, do_sample=True)
    return resposta[0]["generated_text"]

# 🔹 Interface do Streamlit
st.title("📑 Comparador de Cartas Bancárias com IA")

# Upload dos arquivos
pdf_file = st.file_uploader("📄 Envie o PDF da carta bancária", type=["pdf"])
xlsx_modelo = st.file_uploader("📊 Envie o modelo de referência (Excel)", type=["xlsx"])

if pdf_file and xlsx_modelo:
    # Extrair textos
    texto_pdf = extrair_texto_pdf(pdf_file)
    texto_excel = extrair_texto_excel(xlsx_modelo)

    # Chamar a IA para análise
    resultado_ia = analisar_com_ia(texto_pdf, texto_excel)

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
