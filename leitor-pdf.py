import streamlit as st
import pandas as pd
import pdfplumber
import openpyxl
import google.generativeai as genai
from datetime import datetime

# 🔹 Configurar a chave da API do Google Gemini
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
    data_atual = datetime.now().strftime("%d/%m/%Y")  # 📌 Gera a data atual

    prompt = f"""
    Você é um analista bancário especializado em verificação de dados e detecção de inconsistências.
    Compare os dados extraídos do contrato bancário (PDF) com os registros oficiais no arquivo Excel.

    **📅 Data da Análise:** {data_atual}

    **📄 Dados extraídos do PDF:**
    {texto_pdf}

    **📊 Dados extraídos do Excel:**
    {texto_excel}

    **Regras de Análise:**  
    1️⃣ **✅ Informações que batem** → Quando um dado do PDF for exatamente igual ao do Excel.  
    2️⃣ **❌ Informações divergentes** → Quando há diferenças nos valores entre os documentos.  
    3️⃣ **⚠️ Informações faltando** → Quando o Excel deveria ter um dado, mas não tem.  
    4️⃣ **🔍 Erros ou suspeitas de fraude** → Caso os dados no PDF pareçam inconsistentes.  

    **IMPORTANTE:**  
    - Se houver erros ou suspeitas de fraude, destaque no relatório.  
    - A análise deve ser rigorosa, garantindo máxima precisão.  
    - Se o Excel estiver com formatação errada, explique como corrigir.  

    Gere um relatório estruturado e formatado, utilizando listas, markdown e organização clara.
    """

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text

# 🔹 Interface do Streamlit
st.title("📑 Comparador de Cartas Bancárias com IA (Melhorado)")

# 🔹 Upload de múltiplos PDFs e Excels
pdf_files = st.file_uploader("📄 Envie os PDFs das cartas bancárias", type=["pdf"], accept_multiple_files=True)
xlsx_files = st.file_uploader("📊 Envie os arquivos Excel para comparação", type=["xlsx"], accept_multiple_files=True)

# Criar botão para rodar a IA
if pdf_files and xlsx_files:
    if st.button("🔍 Analisar Todos"):
        resultados = []
        
        for pdf_file, xlsx_file in zip(pdf_files, xlsx_files):  # Processa cada par PDF-Excel
            texto_pdf = extrair_texto_pdf(pdf_file)
            texto_excel = extrair_texto_excel(xlsx_file)
            resultado_ia = analisar_com_gemini(texto_pdf, texto_excel)

            resultados.append((pdf_file.name, xlsx_file.name, resultado_ia))  # Armazena os resultados

        # 🔹 Exibir os resultados formatados
        for pdf_name, xlsx_name, resultado in resultados:
            st.markdown(f"### 📂 Comparação entre **{pdf_name}** e **{xlsx_name}**")
            
            st.markdown("---")  # Linha separadora
            
            st.markdown("#### ✅ Informações que batem:")
            st.success(resultado.split("✅ Informações que batem:")[1].split("❌")[0] if "✅" in resultado else "Nenhuma informação confirmada.")

            st.markdown("#### ❌ Informações divergentes:")
            st.warning(resultado.split("❌ Informações divergentes:")[1].split("⚠️")[0] if "❌" in resultado else "Nenhuma divergência encontrada.")

            st.markdown("#### ⚠️ Informações faltando:")
            st.error(resultado.split("⚠️ Informações faltando:")[1].split("🔍")[0] if "⚠️" in resultado else "Nenhum dado faltando.")

            st.markdown("#### 🔍 Erros ou suspeitas de fraude:")
            st.info(resultado.split("🔍 Erros ou suspeitas de fraude:")[1] if "🔍" in resultado else "Nenhuma suspeita detectada.")

            st.markdown("---")  # Linha separadora
        
        # Botão para baixar todos os relatórios
        with open("relatorio_completo.txt", "w", encoding="utf-8") as file:
            for pdf_name, xlsx_name, resultado in resultados:
                file.write(f"\n📂 Comparação entre {pdf_name} e {xlsx_name}\n")
                file.write(resultado + "\n" + "=" * 50 + "\n")

        with open("relatorio_completo.txt", "rb") as file:
            st.download_button("📥 Baixar Relatório Completo", data=file, file_name="relatorio_completo.txt", mime="text/plain")
