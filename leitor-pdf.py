import streamlit as st
import pdfplumber
import pandas as pd
import openpyxl

# Função para extrair os dados do PDF e salvar como Excel
def extrair_dados_pdf(pdf_file, output_excel):
    with pdfplumber.open(pdf_file) as pdf:
        dados = []
        for page in pdf.pages:
            tabelas = page.extract_tables()
            for tabela in tabelas:
                for linha in tabela:
                    dados.append(linha)

    df = pd.DataFrame(dados)
    df.to_excel(output_excel, index=False, engine='openpyxl')

# Função para comparar dois arquivos XLSX
def comparar_xlsx(file1, file2):
    df1 = pd.read_excel(file1)
    df2 = pd.read_excel(file2)

    # Identificar chave de comparação automaticamente
    chaves_comuns = list(set(df1.columns) & set(df2.columns))
    if not chaves_comuns:
        return "Nenhuma chave comum encontrada para comparação!"

    chave = chaves_comuns[0]  # Pega a primeira chave encontrada
    df_merged = df1.merge(df2, on=chave, how='outer', suffixes=('_pdf', '_sap'))

    # Identificar diferenças
    diferencas = df_merged[df_merged.filter(like="_pdf").ne(df_merged.filter(like="_sap")).any(axis=1)]
    
    return diferencas

# Interface Streamlit
st.title("Comparador de Cartas Bancárias")

# Upload dos arquivos
pdf_file = st.file_uploader("Envie o PDF com os dados da carta bancária", type=["pdf"])
xlsx_base = st.file_uploader("Envie o arquivo XLSX base (SAP)", type=["xlsx"])

if pdf_file and xlsx_base:
    output_excel = "extraido.xlsx"
    extrair_dados_pdf(pdf_file, output_excel)

    resultado = comparar_xlsx(output_excel, xlsx_base)
    
    st.write("📊 Resultado da comparação:")
    st.dataframe(resultado)

    # Exportar para Excel
    resultado.to_excel("resultado.xlsx", index=False, engine='openpyxl')
    st.download_button("📥 Baixar Relatório de Diferenças", data=open("resultado.xlsx", "rb"), file_name="relatorio_diferencas.xlsx")
