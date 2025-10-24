import streamlit as st


with st.expander("Test"):
    st.write("Test")


import streamlit as st
import mysql.connector as mys
import pandas as pd

# Načtení údajů z secrets.toml
db = st.secrets["mysql"]

# Připojení k DB
connection = mys.connect(
    host=db["host"],
    port=db["port"],
    database=db["database"],
    user=db["user"],
    password=db["password"]
)

if connection.is_connected():
    st.success("✅ Připojeno k databázi!")

df_zamestnanci = pd.read_sql_query("select * from EMP where JOB LIKE '%C%'", con=connection)
st.write(df_zamestnanci)