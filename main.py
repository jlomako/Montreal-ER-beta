import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import timedelta
# terminal: streamlit run main.py

nr_of_days = 7


@st.cache_data(ttl=600) # 10min cache
def get_data(file):
    df = pd.read_csv("https://github.com/jlomako/hospital-occupancy-tracker/raw/main/tables/"+file,
        parse_dates=['Date']).drop_duplicates('Date').rename(
        columns={"HÔPITAL DE SOINS PSYCHIATRIQUES DE L'EST-DE-MONTRÉAL": "HÔPITAL DE SOINS PSYCHIATRIQUES",
                 "L'HÔPITAL DE MONTRÉAL POUR ENFANTS": "HÔPITAL DE MONTRÉAL POUR ENFANTS",
                 "CENTRE HOSPITALIER DE L'UNIVERSITÉ DE MONTRÉAL": "CHUM"})
    df['Date'] = pd.DatetimeIndex(df['Date']).floor('H') + pd.Timedelta(minutes=46) # set all to 46min
    df = df[(df["Date"] >= (df['Date'].max() - timedelta(days=nr_of_days))) & (df["Date"] <= df['Date'].max())]
    return df


def get_selected(df, selected, variable):
    df = df.filter(items=['Date', selected]).rename(columns={selected: variable})
    # create df_range with timestamps for every hour then merge
    date_range = pd.date_range(start=df['Date'].min(), end=df['Date'].max(), freq='H')
    df_range = pd.DataFrame({'Date': date_range})
    df = pd.merge(df_range, df, on='Date', how='outer')
    return df


def plot_data(df, x_col, y_col, label, title=None):
    fig = px.line(df, x=x_col, y=y_col, labels={"value": label, "variable": ""}, title=title)
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True
    fig.update_layout(legend=dict(orientation="h", x=1, y=1, xanchor="right", yanchor="bottom"))
    fig.update_layout(xaxis_tickmode='auto', xaxis_dtick='1D')
    return fig


# load data
df_occupancy = get_data("occupancy.csv")
df_waiting = get_data("patients_waiting.csv")
df_total = get_data("patients_total.csv")

# DISPLAY CURRENT DATA

# create df with latest data
df_current = pd.merge(df_occupancy.iloc[-1, 1:].reset_index().set_axis(['hospital_name', 'occupancy'], axis=1),
               df_waiting.iloc[-1, 1:].reset_index().set_axis(['hospital_name', 'patients_waiting'], axis=1),
               on='hospital_name', how='outer')
df_current = pd.merge(df_current,
               df_total.iloc[-1, 1:].reset_index().set_axis(['hospital_name', 'patients_total'], axis=1),
               on='hospital_name', how='outer')

# transform cols to numeric
df_current[df_current.columns[1:]] = df_current[df_current.columns[1:]].apply(pd.to_numeric, errors='coerce')



st.title("Montréal Emergency Room Status")


options = {
    "Patients waiting": {"selection": ['patients_waiting', 'patients_total'] , "sort": 'patients_waiting', "title": f"Patient counts on {df_waiting['Date'].max()}"},
    "Patients total": {"selection": ['patients_waiting', 'patients_total'], "sort": 'patients_total', "title": f"Patient counts on {df_total['Date'].max()}"},
    "Occupancy Rate": {"selection": "occupancy", "sort": "occupancy", "title": f"Occupancy Rates on {df_occupancy['Date'].max()}"},
}

option = st.radio("Sort from highest to lowest by:", options.keys(), horizontal=True)


fig_bar = px.bar(df_current[df_current['hospital_name'] != 'TOTAL MONTRÉAL'].sort_values(by=options[option]["sort"]),
                 x=options[option]["selection"], y="hospital_name",
                 title=options[option]["title"],
                 labels={"value": "", "variable": ""},
                 orientation='h', # horizontal
                 text_auto=True, # show numbers
                 height=700,
                 barmode='overlay' if options[option]["sort"] != "occupancy" else None,
                 color_discrete_sequence=['#023858', '#2c7fb8'] if options[option]["sort"] != "occupancy" else None,
                 color=options[option]["sort"] if options[option]["sort"] == "occupancy" else None,
                 color_continuous_scale="blues" if options[option]["sort"] == "occupancy" else None,
                ).update_layout(
                    xaxis_title="",
                    yaxis_title="",
                    xaxis_fixedrange=True, # switch off annoying zoom functions
                    yaxis_fixedrange=True,
                    bargap=0.1, # gap between bars
                    legend=dict(orientation="h", x=1, y=1, xanchor="right", yanchor="bottom")
                ).update_traces(
                    textfont_size=12,
                    textangle=0,
                    textposition="auto",
                    cliponaxis=False
                ).update_coloraxes(showscale=False  # remove legend for color_continuous_scale
                ).update_xaxes(showticklabels=False)
st.plotly_chart(fig_bar, use_container_width=True)

st.caption(f"""
         <small>
         <b>Patients Waiting:</b> The number of patients in the emergency room who are waiting to be seen by a 
         physician.<br>
         <b>Patients Total</b>: The total number of patients in the emergency room, including those 
         who are currently waiting to be seen by a physician.<br>
         <b>Occupancy Rate</b>: The occupancy rate refers to the percentage of stretchers that are occupied by patients. 
         An occupancy rate of over 100% indicates that the emergency room is over capacity, 
         typically meaning that there are more patients than there are stretchers.
         </small>
         <br><br><br>
""", unsafe_allow_html=True)

# SELECT HOSPITAL

# get update time and hospital names from df_occupancy
st.subheader("Select a hospital for more information: ")
hospitals = list(df_occupancy.columns[1::])
selected = st.selectbox("Select a hospital", hospitals, label_visibility="hidden")

# create df with occupancy, patients_waiting and patients_total for selected hospital
df = pd.merge(get_selected(df_occupancy, selected, "occupancy"), get_selected(df_waiting, selected, "patients_waiting"), on='Date', how='outer')
df = pd.merge(df, get_selected(df_total, selected, "patients_total"), on='Date', how='outer')

st.write(f"""
         last update <b>{df['Date'].max()}</b>:<br>
         Out of a total of <b>{int(df.iloc[-1]['patients_total'])}</b>
         patients in the emergency room, <b>{int(df.iloc[-1]['patients_waiting'])}</b>
         are currently waiting to be seen by a physician.
         The current occupancy rate is <b>{int(df.iloc[-1]['occupancy'])}</b> %.
""", unsafe_allow_html=True)


tab1, tab2 = st.tabs(["Patient Counts", "Occupancy Rate"])

with tab1:
    st.write(selected)
    fig_patients = plot_data(df, "Date", ["patients_waiting", "patients_total"], "Number of Patients")
    st.plotly_chart(fig_patients, use_container_width=True)
with tab2:
    st.write(selected)
    fig_occupancy = plot_data(df, "Date", ["occupancy"], "Occupancy Rate")
    st.plotly_chart(fig_occupancy, use_container_width=True)


st.write("Data source: Ministère de la Santé et des Services sociaux du Québec<br>"
         "© Copyright 2023, <a href='https://github.com/jlomako'>jlomako</a>", unsafe_allow_html=True)