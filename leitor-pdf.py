import streamlit as st
import pdfplumber
import pandas as pd

def extrair_dados_pdf(pdf_file):
    dados_extraidos = []
    with pdfplumber.open(pdf_file) as pdf:
        for i, pagina in enumerate(pdf.pages):
            texto = pagina.extract_text()
            dados_extraidos.append([f"Página {i+1}", texto.strip() if texto else "[Nenhum texto encontrado]"])
    return pd.DataFrame(dados_extraidos, columns=["Página", "Texto"])

# Interface no Streamlit
st.title("Extrator de Dados de PDF para Excel 📄➡️📊")
st.write("Faça upload de um PDF e baixe os dados extraídos em Excel.")

uploaded_file = st.file_uploader("Escolha um arquivo PDF", type="pdf")

if uploaded_file is not None:
    st.success("Arquivo carregado com sucesso!")
    df = extrair_dados_pdf(uploaded_file)

    # Exibir dados na tela
    st.dataframe(df)

    # Botão para baixar
    excel_file = "dados_extraidos.xlsx"
    df.to_excel(excel_file, index=False, engine='openpyxl')

    with open(excel_file, "rb") as file:
        st.download_button(label="📥 Baixar Excel", data=file, file_name="dados_extraidos.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
