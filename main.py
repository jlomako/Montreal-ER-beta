import streamlit as st
import plotly.express as px
import pandas as pd
from helper import load_data, filter_data, load_current_data
# terminal: streamlit run main.py

df_current = load_current_data()

st.title("Montreal Emergency Room Status")
#st.subheader("Track emergency room capacity with real-time data updated every hour")

option = st.radio("Sort by:",
                  ("Occupancy Rate", "Patients waiting", "Patients total"), horizontal=True)
if option == "Occupancy Rate":
    bar_selection = "occupancy"
    bar_title = f"Occupancy Rates on {df_current['Date'].max()}"
elif option == "Patients waiting":
    bar_selection = "patients_waiting"
    bar_title = f"Patients waiting to be seen on {df_current['Date'].max()}"
else:
    bar_selection = "patients_total"
    bar_title = f"Total Number of Patients waiting in ER on {df_current['Date'].max()}"

# bar plot with horizontal orientation
fig_bar = px.bar(df_current[df_current['hospital_name'] != 'TOTAL MONTRÉAL'].sort_values(by=bar_selection),
                 x=bar_selection, y="hospital_name",
                 orientation='h',
                 title=bar_title,
                 hover_data=[bar_selection],
                 text_auto=True,
                 height=700,
                 color=bar_selection,
                 color_continuous_scale="reds")
fig_bar.layout.xaxis.fixedrange = True # removes plotly zoom functions
fig_bar.layout.yaxis.fixedrange = True
fig_bar.update_xaxes(title="")
fig_bar.update_yaxes(title="")
fig_bar.update_traces(textfont_size=12, textangle=0, textposition="inside", cliponaxis=False)
st.plotly_chart(fig_bar, use_container_width=True)

# get update time and hospital names from df_current
st.subheader("Select a hospital for more information: ")
hospitals = list(df_current.sort_values(by='occupancy', ascending=False)['hospital_name'])
selected = st.selectbox("Select a hospital", hospitals, label_visibility="hidden")

st.write(f"last update <b>{df_current['Date'].max()}</b>:<br>"
         f"&emsp;&emsp;{df_current.loc[df_current['hospital_name'] == selected, 'patients_waiting'].values[0]} Patients waiting to be seen <br>"
         f"&emsp;&emsp;{df_current.loc[df_current['hospital_name'] == selected, 'patients_total'].values[0]} Patients total present in ER <br>"
         f"&emsp;&emsp;Occupancy rate: {df_current.loc[df_current['hospital_name'] == selected, 'occupancy'].values[0]} %<br>"
         f"&emsp;&emsp;{df_current.loc[df_current['hospital_name'] == selected, 'beds_occ'].values[0]} of "
         f"{df_current.loc[df_current['hospital_name'] == selected, 'beds_total'].values[0]} Stretchers occupied ",
         unsafe_allow_html=True)

df_occupancy = load_data("occupancy.csv")
df_waiting = load_data("patients_waiting.csv")
df_total = load_data("patients_total.csv")

df_occupancy = filter_data(df_occupancy, selected, 'occupancy')
df_waiting = filter_data(df_waiting, selected, 'patients_waiting')
df_total = filter_data(df_total, selected, 'patients_total')

# create df with occupancy, patients_waiting and patients_total for selected hospital
df = df_occupancy.set_index("Date").join([df_waiting.set_index("Date"), df_total.set_index("Date")], how='outer')
# transform index to column "Date"
df = df.reset_index().sort_values("Date").reset_index(drop=True)


tab1, tab2 = st.tabs(["Patient Counts", "Occupancy Rate"])

with tab1:
    st.write(selected)
    # plot patient counts
    fig_patients = px.line(df, x="Date", y=["patients_waiting", "patients_total"],
                  # title="PATIENT COUNTS",
                  labels={"value": "Number of patients", "variable": ""},
                  template="plotly_white")
    fig_patients.update_layout(xaxis_tickmode='linear', xaxis_dtick='1D')
    fig_patients.update_layout(legend=dict(orientation="h", x=1, y=1, xanchor="right", yanchor="bottom"))
    fig_patients.layout.xaxis.fixedrange = True
    fig_patients.layout.yaxis.fixedrange = True
    st.plotly_chart(fig_patients, use_container_width=True)
    # st.line_chart(df, x="Date", y=["patients_waiting", "patients_total"], use_container_width=True)

with tab2:
    st.write(selected)
    # plot occupancy
    fig_occupany = px.line(df, x='Date', y='occupancy',
                           # title="OCCUPANCY RATE",
                           labels={"value": "Occupancy Rate", "variable": ""},
                           template="plotly_white")
    fig_occupany.update_layout(xaxis_tickmode='linear', xaxis_dtick='1D')
    fig_occupany.update_layout(legend=dict(orientation="h", x=1, y=1, xanchor="right", yanchor="bottom"))
    fig_occupany.layout.xaxis.fixedrange = True
    fig_occupany.layout.yaxis.fixedrange = True
    st.plotly_chart(fig_occupany, use_container_width=True)
    # st.line_chart(df, x="Date", y="occupancy")

st.write("Data source: Ministère de la Santé et des Services sociaux du Québec<br>"
         "© Copyright 2023, <a href='https://github.com/jlomako'>jlomako</a>", unsafe_allow_html=True)