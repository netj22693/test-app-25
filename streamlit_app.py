import streamlit as st


with st.expander("Test"):
    st.write("Test")


import streamlit as st
import mysql.connector as mys
import pandas as pd

# # Načtení údajů z secrets.toml
# db = st.secrets["mysql"]

# # Připojení k DB
# connection = mys.connect(
#     host=db["host"],
#     port=db["port"],
#     database=db["database"],
#     user=db["user"],
#     password=db["password"]
# )

# if connection.is_connected():
#     st.success("✅ Připojeno k databázi!")

# df_zamestnanci = pd.read_sql_query("select * from EMP where JOB LIKE '%C%'", con=connection)
# st.write(df_zamestnanci)


from sqlalchemy import create_engine
import pandas as pd

# conn_string = "postgresql+psycopg2://neondb_owner:npg_eycatwJ1nF3U@ep-lucky-bar-a9hww36i-pooler.gwc.azure.neon.tech/neondb?sslmode=require"


# načtení tajemství
db = st.secrets["neon"]

# sestavení connection stringu
conn_string = f"postgresql+psycopg2://neondb_owner:{db['password']}@ep-lucky-bar-a9hww36i-pooler.gwc.azure.neon.tech/neondb?sslmode=require"


engine = create_engine(conn_string)

df = pd.read_sql("SELECT * FROM test_table LIMIT 5;", engine)
st.write(df.head())
