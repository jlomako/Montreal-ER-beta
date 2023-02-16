from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

@st.cache_data
def load_data(url):
    df = pd.read_csv(url, parse_dates=['Date']).drop_duplicates('Date')
    df['Date'] = pd.DatetimeIndex(df['Date']).floor('H') + pd.Timedelta(minutes=46) # set all to 46min
    # filter last 7 days
    df = df[(df["Date"] >= (df['Date'].max() - timedelta(days=7))) & (df["Date"] <= df['Date'].max())]
    # create df_range with timestamps for every hour
    date_range = pd.date_range(start=df['Date'].min(), end=df['Date'].max(), freq='H')
    df_range = pd.DataFrame({'Date': date_range})
    # merge with df
    df = pd.merge(df_range, df, on='Date', how='outer')
    return df

def filter_data(df, selected, variable_name):
  df = df.filter(items=['Date', selected])
  df.rename(columns={selected: variable_name}, inplace=True)
  return df
