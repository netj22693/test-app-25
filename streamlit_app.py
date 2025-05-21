# streamlit_app.py
import streamlit as st
import sqlalchemy


import pymysql as mys
import pandas as pd

# já jsem si to ještě profesionálně obalil do try a except, abych viděl, zda se povedlo nebo ne

# POZOR - pokud se připojuju na DB, musím být mimo VPN 
pripojeni_na_DB = mys.connect(
    host= "mysql57.r2.websupport.sk", 
    port = 3311,
    database="Kurz_SQL",
    password= "",
    user= "Kurz_SQL"
        )
st.write("All good - complete")

df_zamestnanci_all = pd.read_sql_query("select * from EMP", con=pripojeni_na_DB)
st.write(df_zamestnanci_all)



import streamlit as st

host=st.secrets.db_credentials.host,
user=st.secrets.db_credentials.user,
password=st.secrets.db_credentials.password,
db=st.secrets.db_credentials.database

conn = st.connection('db_credentials', type='sql')
pet_owners = conn.query('select * from EMP')
st.dataframe(pet_owners)

