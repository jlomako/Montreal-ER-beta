import streamlit as st
import plotly.express as px
from helper import get_data
# terminal: streamlit run main.py


df = get_data()

hospitals = list(df.columns[1::])

st.title("Patients waiting in ER")

selected = st.selectbox("Select ER", hospitals)
# st.subheader(f"{selected}")

df_hospital = df.filter(items=['Date', selected])
df_hospital.rename(columns={selected: 'total_patients'}, inplace=True)


# plot
fig = px.line(df_hospital, x='Date', y='total_patients', title=selected)
fig.update_layout(xaxis_tickmode='linear', xaxis_dtick='1D')
st.plotly_chart(fig)

# scatter
fig1 = px.scatter(df_hospital, x='Date', y='total_patients',  title=selected, opacity=0.7)
fig1.update_traces(marker=dict(size=3, line=dict(width=1)))
fig1.update_layout(xaxis_tickmode='linear', xaxis_dtick='1D')
st.plotly_chart(fig1)

