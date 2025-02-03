import streamlit as st
import pandas as pd
from google.cloud import bigquery

# Carregar credenciais do Streamlit Cloud
service_account_info = st.secrets["connections.gcs"]

# Criar cliente BigQuery usando as credenciais do secrets.toml
client = bigquery.Client.from_service_account_info(service_account_info)

# Definir as tabelas do projeto no BigQuery
PROJECT_ID = "dbt-demo-449703"
DATASET = "dbt_suprema"
TABLE_FACT = f"{PROJECT_ID}.{DATASET}.gold_fato_apostas"
TABLE_DIM_USERS = f"{PROJECT_ID}.{DATASET}.gold_dim_usuarios"

# Função para carregar os dados da camada Gold
@st.cache_data
def load_data():
    query = f"""
    SELECT f.data, f.valor_aposta, f.lucro, d.nome_usuario, d.pais
    FROM `{TABLE_FACT}` f
    JOIN `{TABLE_DIM_USERS}` d ON f.user_id = d.user_id
    WHERE f.data >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
    """
    df = client.query(query).to_dataframe()
    return df

# Carregar os dados
df = load_data()

# Criar Dashboard
st.title("📊 Relatório de Apostas - BigQuery + Streamlit")

# Criar filtros
st.sidebar.header("Filtros")
usuario = st.sidebar.selectbox("Selecione um Usuário", df["nome_usuario"].unique())
df_filtered = df[df["nome_usuario"] == usuario]

# Gráfico de Apostas por Data
import plotly.express as px
fig = px.line(df_filtered, x="data", y="valor_aposta", title=f"Apostas de {usuario}")
st.plotly_chart(fig)

# Mostrar tabela filtrada
st.subheader("📄 Detalhes das Apostas")
st.dataframe(df_filtered)
