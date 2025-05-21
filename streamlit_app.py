
import pymysql as mys
import pandas as pd
import streamlit as st


pripojeni_na_DB = mys.connect(
    host= st.secrets["host"], 
    port = st.secrets["port"],
    database= st.secrets["database"],
    password= st.secrets["password"],
    user= st.secrets["user"]
    )

df_zamestnanci = pd.read_sql_query("select * from EMP", con=pripojeni_na_DB)
st.write(df_zamestnanci)