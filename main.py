import streamlit as st
import pandas as pd
import plotly.express as px
# terminal: streamlit run main.py

def get_data():
    url = "https://github.com/jlomako/hospital-occupancy-tracker/raw/main/tables/patients_total.csv"
    df = pd.read_csv(url, encoding="latin1")
    df = df.drop_duplicates("Date")
    df['Date'] = pd.to_datetime(df['Date'])
    # df = df.dropna() # ?
    return df

df = get_data()
hospitals = list(df.columns[1::])

st.title("Patients waiting in ER")

selected = st.selectbox("Select ER", hospitals)
# st.subheader(f"{selected}")

df = df.filter(items=['Date', selected])



# create plot
#figure = px.line(x=dates, y=temperatures, labels={"x": "Date", "y": "Temperature (in C)"})
#st.plotly_chart(figure)

fig = px.line(df, x='Date', y=selected, title=selected,
              labels={"x": "Time", "y": "Patients Total"})
fig.update_layout(xaxis=dict(tickformat='%d-%m\n%hh'))
st.plotly_chart(fig)

#fig.show()

