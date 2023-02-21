import streamlit as st
import plotly.express as px
import pandas as pd
from helper import load_data, filter_data, load_current_data
# terminal: streamlit run main.py

# df_current = load_current_data("urgence_time.csv")
df_occupancy = load_data("occupancy.csv")
df_waiting = load_data("patients_waiting.csv")
df_total = load_data("patients_total.csv")

st.title("Montréal Emergency Room Status")
#st.subheader("Track emergency room capacity with real-time data updated every hour")

options = {
    "Occupancy Rate": {"selection": "occupancy", "data": df_occupancy, "title": f"Occupancy Rates on {df_occupancy['Date'].max()}"},
    "Patients waiting": {"selection": "patients_waiting", "data": df_waiting, "title": f"Patients waiting to be seen on {df_waiting['Date'].max()}"},
    "Patients total": {"selection": "patients_total", "data": df_total, "title": f"Total Number of Patients waiting in ER on {df_total['Date'].max()}"},
}

option = st.radio("Sort by:", options.keys(), horizontal=True)
bar_selection = options[option]["selection"]
bar_title = options[option]["title"]

# load selected data and reshape for plotting (does not include 'Date' and 'TOTAL MONTREAL')
bar_data = options[option]["data"].iloc[-1, 1:22].reset_index().set_axis(['hospital_name', bar_selection], axis=1)
bar_data[bar_selection] = pd.to_numeric(bar_data[bar_selection], errors='coerce')

fig_bar = px.bar(bar_data.sort_values(by=bar_selection),
                 x=bar_selection, y="hospital_name",
                 orientation='h', # horizontal
                 text_auto=True, # show numbers
                 height=700,
                 title=bar_title,
                 hover_data=[bar_selection],
                 color=bar_selection,
                 color_continuous_scale="blues"
                ).update_layout(
                    xaxis_title="",
                    yaxis_title="",
                    xaxis_fixedrange=True, # switch of zoom functions etc
                    yaxis_fixedrange=True
                ).update_traces(
                    textfont_size=12,
                    textangle=0,
                    textposition="inside",
                    cliponaxis=False
                ).update_coloraxes(showscale=False  # remove legend
                ).update_xaxes(showticklabels=False)
st.plotly_chart(fig_bar, use_container_width=True)

# SELECT HOSPITAL

# get update time and hospital names from df_occupancy
st.subheader("Select a hospital for more information: ")
hospitals = list(df_occupancy.columns[1::])
selected = st.selectbox("Select a hospital", hospitals, label_visibility="hidden")


df_occupancy = filter_data(df_occupancy, selected, 'occupancy')
df_waiting = filter_data(df_waiting, selected, 'patients_waiting')
df_total = filter_data(df_total, selected, 'patients_total')

# create df with occupancy, patients_waiting and patients_total for selected hospital
df = df_occupancy.set_index("Date").join([df_waiting.set_index("Date"), df_total.set_index("Date")], how='outer')
# transform index to column "Date"
df = df.reset_index().sort_values("Date").reset_index(drop=True)

st.write(f"""
         last update <b>{df['Date'].max()}</b>:<br>
         Out of a total of <b>{int(df.iloc[-1]['patients_total'])}</b>
         patients in the emergency room, <b>{int(df.iloc[-1]['patients_waiting'])}</b>
         are currently waiting to be seen by a physician.
         The current occupancy rate is <b>{int(df.iloc[-1]['occupancy'])}</b> %.
""", unsafe_allow_html=True)

def plot_data(df, x_col, y_col, label, title=None):
    fig = px.line(df, x=x_col, y=y_col, labels={"value": label, "variable": ""}, title=title)
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True
    fig.update_layout(legend=dict(orientation="h", x=1, y=1, xanchor="right", yanchor="bottom"))
    fig.update_layout(xaxis_tickmode='auto', xaxis_dtick='1D')
    return fig


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