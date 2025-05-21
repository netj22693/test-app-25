# streamlit_app.py
import streamlit as st
import sqlalchemy


import pymysql as mys
import pandas as pd





import streamlit as st

# Everything is accessible via the st.secrets dict:

st.write("DB username:", st.secrets["db_username"])
#st.write("DB password:", st.secrets["db_password2"])
st.write("DB username:", st.secrets["user"])
st.write("DB password:", st.secrets["password"])


conn = st.connection("ahoj", type = "sql")

