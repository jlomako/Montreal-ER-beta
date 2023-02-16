import streamlit as st
import plotly.express as px
from helper import load_data, filter_data
# terminal: streamlit run main.py

# import pandas as pd
# df = pd.read_csv("wait_hours.csv", parse_dates=['Date'])

df_occupancy = load_data("https://github.com/jlomako/hospital-occupancy-tracker/raw/main/tables/occupancy.csv")
df_waiting = load_data("https://github.com/jlomako/hospital-occupancy-tracker/raw/main/tables/patients_waiting.csv")
df_total = load_data("https://github.com/jlomako/hospital-occupancy-tracker/raw/main/tables/patients_total.csv")

# get hospital names from df_occupancy
hospitals = list(df_occupancy.columns[1::])

st.title("Occupancy and Patient Counts")
# st.subheader("in Montreal ERs - hourly updated")

selected = st.selectbox("Select hospital:", hospitals)


df_occupancy = filter_data(df_occupancy, selected, 'occupancy')
df_waiting = filter_data(df_waiting, selected, 'patients_waiting')
df_total = filter_data(df_total, selected, 'patients_total')

# create df with occupancy, patients_waiting and patients_total for selected hospital
df = df_occupancy.set_index("Date").join([df_waiting.set_index("Date"), df_total.set_index("Date")], how='outer')
# transform index to column "Date"
df = df.reset_index().sort_values("Date").reset_index(drop=True)

fig = px.line(df, x="Date", y=["patients_waiting", "patients_total"],
              title=selected,
              labels={"value": "Number of patients", "variable": "Category"},
              template="plotly_white")

# fig.update_xaxes(tickformat="%Y-%m-%d %H:%M:%S")
fig.update_layout(xaxis_tickmode='linear', xaxis_dtick='1D')
st.plotly_chart(fig)

# plot occupancy
fig_occupany = px.line(df, x='Date', y='occupancy')
fig_occupany.update_layout(xaxis_tickmode='linear', xaxis_dtick='1D')
st.plotly_chart(fig_occupany)
