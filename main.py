import streamlit as st
import pandas as pd
import plotly.express as px
# terminal: streamlit run main.py

def get_data():
    url = "https://github.com/jlomako/hospital-occupancy-tracker/raw/main/tables/patients_total.csv"
    df = pd.read_csv(url, parse_dates=['Date']).drop_duplicates('Date')
    df['Date'] = pd.DatetimeIndex(df['Date']).floor('H') + pd.Timedelta(minutes=46) # set all to 46min
    # create df with timestamps for every hour
    date_range = pd.date_range(start=df['Date'].min(), end=df['Date'].max(), freq='H')
    df_range = pd.DataFrame({'Date': date_range})
    df = pd.merge(df_range, df, on='Date', how='outer')
    return df


df = get_data()
hospitals = list(df.columns[1::])

st.title("Patients waiting in ER")

selected = st.selectbox("Select ER", hospitals)
# st.subheader(f"{selected}")

df = df.filter(items=['Date', selected])


# plot
fig = px.line(df, x='Date', y=selected, title=selected)
fig.update_layout(xaxis_tickmode='linear', xaxis_dtick='1D')
st.plotly_chart(fig)

# scatter
fig1 = px.scatter(df, x='Date', y=selected,  title=selected, opacity=0.7)
fig1.update_traces(marker=dict(size=3, line=dict(width=1)))
fig1.update_layout(xaxis_tickmode='linear', xaxis_dtick='1D')
st.plotly_chart(fig1)

