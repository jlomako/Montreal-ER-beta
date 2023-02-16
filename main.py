import streamlit as st
import plotly.express as px
from helper import load_data
# terminal: streamlit run main.py

# import pandas as pd
# df = pd.read_csv("wait_hours.csv", parse_dates=['Date'])

#df = load_data("https://github.com/jlomako/hospital-occupancy-tracker/raw/main/tables/occupancy.csv")
#df = load_data("https://github.com/jlomako/hospital-occupancy-tracker/raw/main/tables/patients_waiting.csv")
df = load_data("https://github.com/jlomako/hospital-occupancy-tracker/raw/main/tables/patients_total.csv")

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
