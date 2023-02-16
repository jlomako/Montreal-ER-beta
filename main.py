import streamlit as st
import plotly.express as px
from helper import load_data, filter_data
# terminal: streamlit run main.py

st.set_page_config(layout="wide")

df_occupancy = load_data("occupancy.csv")
df_waiting = load_data("patients_waiting.csv")
df_total = load_data("patients_total.csv")

st.title("Occupancy and Patient Counts")

# get update time and hospital names from df_occupancy
hospitals = list(df_occupancy.columns[1::])
selected = st.selectbox("Select hospital:", hospitals)

df_occupancy = filter_data(df_occupancy, selected, 'occupancy')
df_waiting = filter_data(df_waiting, selected, 'patients_waiting')
df_total = filter_data(df_total, selected, 'patients_total')

# create df with occupancy, patients_waiting and patients_total for selected hospital
df = df_occupancy.set_index("Date").join([df_waiting.set_index("Date"), df_total.set_index("Date")], how='outer')
# transform index to column "Date"
df = df.reset_index().sort_values("Date").reset_index(drop=True)


st.write(f"&emsp;Occupancy Rate: {int(df['occupancy'].max())} %<br>"
         f"&emsp;{int(df['patients_waiting'].max())} Patients waiting to be seen <br>"
         f"&emsp;{int(df['patients_total'].max())} Patients present in ER <br>"
         f"&emsp;last update: <b>{df['Date'].max()}</b>",unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Patient Counts", "Occupancy Rate"])

with tab1:
    st.write(selected)
    # plot patient counts
    fig = px.line(df, x="Date", y=["patients_waiting", "patients_total"],
                  # title="PATIENT COUNTS",
                  labels={"value": "Number of patients", "variable": ""},
                  template="plotly_white")
    fig.update_layout(xaxis_tickmode='linear', xaxis_dtick='1D')
    fig.update_layout(legend=dict(orientation="h", x=1, y=1, xanchor="right", yanchor="bottom"))
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.write(selected)
    # plot occupancy
    fig_occupany = px.line(df, x='Date', y='occupancy',
                           # title="OCCUPANCY RATE",
                           labels={"value": "Occupancy Rate", "variable": ""},
                           template="plotly_white")
    fig_occupany.update_layout(xaxis_tickmode='linear', xaxis_dtick='1D')
    fig.update_layout(legend=dict(orientation="h", x=1, y=1, xanchor="right", yanchor="bottom"))
    st.plotly_chart(fig_occupany, use_container_width=True)

st.write("Data source: Ministère de la Santé et des Services sociaux du Québec<br>"
         "© Copyright 2023, <a href='https://github.com/jlomako'>jlomako</a>", unsafe_allow_html=True)