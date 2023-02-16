import pandas as pd
import streamlit as st

@st.cache_data
def load_data(url):
#    url = "https://github.com/jlomako/hospital-occupancy-tracker/raw/main/tables/patients_total.csv"
    df = pd.read_csv(url, parse_dates=['Date']).drop_duplicates('Date')
    df['Date'] = pd.DatetimeIndex(df['Date']).floor('H') + pd.Timedelta(minutes=46) # set all to 46min
    # create df_range with timestamps for every hour
    date_range = pd.date_range(start=df['Date'].min(), end=df['Date'].max(), freq='H')
    df_range = pd.DataFrame({'Date': date_range})
    # merge with df
    df = pd.merge(df_range, df, on='Date', how='outer')
    return df
