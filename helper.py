from datetime import timedelta
import pandas as pd

nr_of_days = 7

def get_data(file):
    df = pd.read_csv("https://github.com/jlomako/hospital-occupancy-tracker/raw/main/tables/"+file,
                     parse_dates=['Date']).drop_duplicates('Date')
    df['Date'] = pd.DatetimeIndex(df['Date']).floor('H') + pd.Timedelta(minutes=46) # set all to 46min
    # filter last 7 days
    df = df[(df["Date"] >= (df['Date'].max() - timedelta(days=nr_of_days))) & (df["Date"] <= df['Date'].max())]
    return df

def get_selected(df, selected, variable):
    df = df.filter(items=['Date', selected]).rename(columns={selected: variable})
    # create df_range with timestamps for every hour
    date_range = pd.date_range(start=df['Date'].min(), end=df['Date'].max(), freq='H')
    df_range = pd.DataFrame({'Date': date_range})
    # merge with df
    df = pd.merge(df_range, df, on='Date', how='outer')
    # df.rename(columns={selected: variable}, inplace=True)
    return df
