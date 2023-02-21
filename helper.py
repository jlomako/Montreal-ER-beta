from datetime import timedelta
import pandas as pd

nr_of_days = 7

def load_current_data(file):
    df = pd.read_csv("https://github.com/jlomako/quebec-emergency-rooms/raw/main/data/"+file,
                     encoding='iso-8859-1', parse_dates=[' Mise_a_jour'])
    df = df[df['RSS'] == 6].iloc[:, [-1, 3, 5, 6, 9, 10]] # get columns where RSS is 6
    df.iloc[:, 2:] = df.iloc[:, 2:].apply(lambda x: pd.to_numeric(x, errors='coerce'))
    df['occupancy'] = (
                100 * df['Nombre_de_civieres_occupees'] / df['Nombre_de_civieres_fonctionnelles \t\t\t\t\t\t']).round(0)
    df.iloc[0, 1] = 'TOTAL MONTRÉAL'
    df.iloc[2, 1] = 'HÔPITAL DU SACRÉ-COEUR DE MONTRÉAL'
    df.columns = ['Date', 'hospital_name', 'beds_total', 'beds_occ', 'patients_total', 'patients_waiting', 'occupancy']
    return df

def load_data(file):
    df = pd.read_csv("https://github.com/jlomako/hospital-occupancy-tracker/raw/main/tables/"+file,
                     parse_dates=['Date']).drop_duplicates('Date')
    df['Date'] = pd.DatetimeIndex(df['Date']).floor('H') + pd.Timedelta(minutes=46) # set all to 46min
    df = df[(df["Date"] >= (df['Date'].max() - timedelta(days=nr_of_days))) & (df["Date"] <= df['Date'].max())]
    # create df_range with timestamps for every hour
    date_range = pd.date_range(start=df['Date'].min(), end=df['Date'].max(), freq='H')
    df_range = pd.DataFrame({'Date': date_range})
    df = pd.merge(df_range, df, on='Date', how='outer') # merge with df
    return df

def filter_data(df, selected, variable_name):
  df = df.filter(items=['Date', selected])
  df.rename(columns={selected: variable_name}, inplace=True)
  return df


