import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd

# URL da logo
LOGO_URL = "https://supremagaming.com.br/wp-content/uploads/2024/10/logo-supremagaming-preto.svg"

# Definir estilo da página
st.set_page_config(layout="wide")

# Exibir a logo centralizada no topo
st.markdown(
    f"""
    <div style="text-align: center;">
        <img src="{LOGO_URL}" width="250">
    </div>
    """,
    unsafe_allow_html=True
)

st.title("Análise de Apostas - BigQuery")

# Carregar credenciais do Streamlit Secrets
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["connections"]["gcs"]
)

# Criar cliente do BigQuery
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# Definir a consulta SQL com agregações
query = query = """
SELECT 
    date_key,
    SUM(bet_amount_brl_today) AS total_apostado_brl,
    SUM(profit_brl_today) AS lucro_diario_brl
FROM `dbt-demo-449703.dbt_suprema.gold_fact_bet_analysis`
GROUP BY date_key
ORDER BY date_key
"""

# Executar a query
query_job = client.query(query)
df = query_job.to_dataframe()

# Exibir as métricas principais
st.subheader("Resumo Geral")
col1, col2, col3 = st.columns(3)
col1.metric("Total Apostado (BRL)", f"R$ {df['total_apostado_brl'].sum():,.2f}")
col2.metric("Lucro Total (BRL)", f"R$ {df['lucro_diario_brl'].sum():,.2f}") 

# Exibir a tabela com detalhes diários
st.subheader("Detalhamento Diário")
st.dataframe(df)

# Criar gráfico da evolução das apostas ao longo do tempo
st.subheader("Evolução das Apostas e Lucros")
st.line_chart(df.set_index("date_key")[["total_apostado_brl", "lucro_diario_brl"]])
