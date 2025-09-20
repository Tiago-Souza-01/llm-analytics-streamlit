import streamlit as st
import pandas as pd
import numpy as np
import psycopg2

import plotly.express as px
import plotly.graph_objects as go
import os
import pytz
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH")  

LOCAL_TZ = pytz.timezone("America/Sao_Paulo")

@st.cache_data(ttl=60)
def load_data(conn_str):
    conn = psycopg2.connect(conn_str)
    query = "SELECT provider, latency, created_at FROM documents_latencyllm"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

st.set_page_config(page_title="🚀 Dashboard de Latência LLM", layout="wide")
st.markdown("<h1 style='text-align: center; color: #4F8BF9;'>🚀 Dashboard de Latência dos LLMs</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>Visualize métricas de latência por provedor em tempo real.</p>", unsafe_allow_html=True)
st.markdown("<hr style='border:1px solid #4F8BF9'>", unsafe_allow_html=True)

df = load_data(DB_PATH)


df['created_at'] = pd.to_datetime(df['created_at'], utc=True).dt.tz_convert(LOCAL_TZ)

st.markdown("<h3 style='color:#4F8BF9;'>🗓️ Filtro de Período (Data e Hora)</h3>", unsafe_allow_html=True)
min_dt = df['created_at'].min()
max_dt = df['created_at'].max()

col1, col2 = st.columns(2)
start_date = col1.date_input("Data inicial", value=min_dt.date(), min_value=min_dt.date(), max_value=max_dt.date())
start_time = col1.time_input("Hora inicial", value=min_dt.time())
end_date = col2.date_input("Data final", value=max_dt.date(), min_value=min_dt.date(), max_value=max_dt.date())
end_time = col2.time_input("Hora final", value=max_dt.time())


start_dt = pd.Timestamp.combine(start_date, start_time).tz_localize(LOCAL_TZ)
end_dt = pd.Timestamp.combine(end_date, end_time).tz_localize(LOCAL_TZ)


df = df[(df['created_at'] >= start_dt) & (df['created_at'] <= end_dt)]

if df.empty:
    st.warning("Nenhum dado de latência encontrado para o período selecionado.")
    st.stop()

st.markdown("<h2 style='color:#4F8BF9;'>📊 Estatísticas Gerais</h2>", unsafe_allow_html=True)
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Latência Média (s)", f"{df['latency'].mean():.3f}")
col2.metric("Latência Máxima (s)", f"{df['latency'].max():.3f}")
col3.metric("Latência Mínima (s)", f"{df['latency'].min():.3f}")
col4.metric("p95 (s)", f"{np.percentile(df['latency'], 95):.3f}")
col5.metric("p99 (s)", f"{np.percentile(df['latency'], 99):.3f}")
st.markdown("<hr style='border:1px dashed #4F8BF9'>", unsafe_allow_html=True)

st.markdown("<h2 style='color:#F98B4F;'>📊 Estatísticas por Provedor</h2>", unsafe_allow_html=True)
for provider, group in df.groupby('provider'):
    st.markdown(f"<h3 style='color:#F98B4F;'>{provider}</h3>", unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Média (s)", f"{group['latency'].mean():.3f}")
    col2.metric("Máxima (s)", f"{group['latency'].max():.3f}")
    col3.metric("Mínima (s)", f"{group['latency'].min():.3f}")
    col4.metric("p95 (s)", f"{np.percentile(group['latency'], 95):.3f}")
    col5.metric("p99 (s)", f"{np.percentile(group['latency'], 99):.3f}")
    st.markdown("<hr style='border:0.5px solid #F98B4F'>", unsafe_allow_html=True)

st.markdown("<h4 style='color:#4F8BF9;'>📋 Tabela de Estatísticas por Provedor</h4>", unsafe_allow_html=True)
stats = df.groupby('provider')['latency'].agg(['count', 'mean', 'std', 'min', 'max'])
st.dataframe(stats.style.background_gradient(cmap='Oranges'), use_container_width=True)
st.markdown("<hr style='border:1px dashed #F98B4F'>", unsafe_allow_html=True)

st.markdown("<h2 style='color:#4F8BF9;'>📦 Boxplot de Latência - Todos os Provedores</h2>", unsafe_allow_html=True)
fig = px.box(df, x="provider", y="latency", points="all", color="provider",
             title="Boxplot de Latência por Provedor (Geral)",
             color_discrete_sequence=px.colors.qualitative.Set2)
fig.update_layout(plot_bgcolor='#F5F5F5', paper_bgcolor='#F5F5F5', font=dict(color='#222'))
st.plotly_chart(fig, use_container_width=True)


st.markdown("<h2 style='color:#F98B4F;'>📦 Boxplot Individual por Provedor</h2>", unsafe_allow_html=True)
for provider, group in df.groupby('provider'):
    fig_ind = px.box(group, y="latency", points="all", title=f"Boxplot de Latência - {provider}",
                     color_discrete_sequence=["#F98B4F"])
    fig_ind.update_layout(plot_bgcolor='#FFF8F0', paper_bgcolor='#FFF8F0', font=dict(color='#222'))
    st.plotly_chart(fig_ind, use_container_width=True)
    st.markdown("<hr style='border:0.5px solid #F98B4F'>", unsafe_allow_html=True)

st.markdown("<h2 style='color:#4F8BF9;'>⏱️ Latência por Requisição</h2>", unsafe_allow_html=True)
df['created_at_str'] = df['created_at'].dt.strftime('%d/%m %H:%M:%S')
fig2 = px.bar(
    df.sort_values("created_at"),
    x="created_at_str",
    y="latency",
    color="provider",
    title="Latência por Requisição de Cada Provider",
    labels={"created_at_str": "Data/Hora"},
    color_discrete_sequence=px.colors.qualitative.Set1
)
fig2.update_layout(plot_bgcolor='#F5F5F5', paper_bgcolor='#F5F5F5', font=dict(color='#222'))
st.plotly_chart(fig2, use_container_width=True)

st.markdown("<h2 style='color:#4F8BF9;'>🎯 Percentis por Provedor</h2>", unsafe_allow_html=True)
percentis = []
for provider, group in df.groupby('provider'):
    percentis.append({
        'provider': provider,
        'p50': np.percentile(group['latency'], 50),
        'p95': np.percentile(group['latency'], 95),
        'p99': np.percentile(group['latency'], 99),
        'count': len(group)
    })
percentis_df = pd.DataFrame(percentis)

fig3 = go.Figure()
fig3.add_trace(go.Bar(x=percentis_df['provider'], y=percentis_df['p50'], name='p50', marker_color='#4F8BF9'))
fig3.add_trace(go.Bar(x=percentis_df['provider'], y=percentis_df['p95'], name='p95', marker_color='#F98B4F'))
fig3.add_trace(go.Bar(x=percentis_df['provider'], y=percentis_df['p99'], name='p99', marker_color='#E94F8B'))
fig3.update_layout(
    barmode='group',
    title='Percentis de Latência por Provedor',
    xaxis_title='Provedor',
    yaxis_title='Latência (s)',
    plot_bgcolor='#F5F5F5',
    paper_bgcolor='#F5F5F5',
    font=dict(color='#222')
)
st.plotly_chart(fig3, use_container_width=True)
st.markdown("<hr style='border:1px solid #4F8BF9'>", unsafe_allow_html=True)

st.markdown("<h2 style='color:#4F8BF9;'>🔎 Dados Detalhados</h2>", unsafe_allow_html=True)
st.dataframe(df.sort_values("created_at", ascending=False).style.background_gradient(cmap='Blues'), use_container_width=True)

st.markdown("<hr style='border:1px solid #4F8BF9'>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#4F8BF9;'> UERJ 💙🧡</p>", unsafe_allow_html=True)
