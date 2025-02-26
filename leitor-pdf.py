import streamlit as st
import pandas as pd
import pdfplumber
import os

# Função para extrair texto do PDF e converter para Excel
def extrair_dados_pdf(pdf_path, output_excel):
    with pdfplumber.open(pdf_path) as pdf:
        all_text = []
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text.append(text)

    # Criando um DataFrame simples
    df = pd.DataFrame({"Dados Extraídos": all_text})

    # Exportando para Excel
    df.to_excel(output_excel, index=False, engine='openpyxl')
    return output_excel

# Função para comparar os arquivos XLSX
def comparar_xlsx(arquivo1, arquivo2):
    df1 = pd.read_excel(arquivo1, engine='openpyxl')
    df2 = pd.read_excel(arquivo2, engine='openpyxl')

    # Identificando colunas comuns para comparação
    colunas_comuns = list(set(df1.columns) & set(df2.columns))
    
    if not colunas_comuns:
        return "Nenhuma chave comum encontrada para comparação!"
    
    # Fazendo a junção para comparação
    df_comparacao = df1.merge(df2, on=colunas_comuns, how="outer", indicator=True)

    # Pegando apenas as diferenças
    diferencas = df_comparacao[df_comparacao["_merge"] != "both"].drop(columns=["_merge"])

    return diferencas

# Interface do Streamlit
st.title("📑 Comparador de Dados Bancários")

# Upload de arquivos
pdf_file = st.file_uploader("📄 Faça upload do arquivo PDF com os dados", type=["pdf"])
xlsx_base = st.file_uploader("📊 Faça upload do arquivo Excel base para comparação", type=["xlsx"])

if pdf_file and xlsx_base:
    # Nome temporário para o Excel convertido
    output_excel = "dados_extraidos.xlsx"

    # Extraindo dados do PDF
    extrair_dados_pdf(pdf_file, output_excel)

    # Comparando os arquivos XLSX
    resultado = comparar_xlsx(output_excel, xlsx_base)

    # Exibindo o resultado
    st.write("📊 Resultado da comparação:")

    if isinstance(resultado, pd.DataFrame) and not resultado.empty:
        st.dataframe(resultado)
        
        # Exportando para Excel
        resultado.to_excel("resultado.xlsx", index=False, engine='openpyxl')

        # Botão de download do relatório
        with open("resultado.xlsx", "rb") as file:
            st.download_button("📥 Baixar Relatório de Diferenças", data=file, file_name="relatorio_diferencas.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.warning("⚠️ Nenhuma diferença encontrada ou arquivos não possuem chaves comuns para comparação!")
