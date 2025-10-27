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


# Ukoly
# 1) pridat ["neon"] a passwords do secrets v code space a na PROD (!)
# 2) pridat sqlalchemy do requirements.txt
# 3) pridat psycopg2-binary do requirements. txt (pravdepodobne i nainstalovat  pip install streamlit sqlalchemy psycopg2-binary )



from sqlalchemy import create_engine
from sqlalchemy import text
import pandas as pd
import time

# conn_string = "postgresql+psycopg2://neondb_owner:npg_eycatwJ1nF3U@ep-lucky-bar-a9hww36i-pooler.gwc.azure.neon.tech/neondb?sslmode=require"


# načtení tajemství
db = st.secrets["neon"]

# sestavení connection stringu
try: 
    conn_string = f"postgresql+psycopg2://neondb_owner:{db['password']}@ep-lucky-bar-a9hww36i-pooler.gwc.azure.neon.tech/neondb?sslmode=require"


    engine = create_engine(conn_string)

except:
    st.warning("DB not connected")
    st.stop()

df = pd.read_sql("SELECT * FROM test_table LIMIT 5;", engine)
st.write(df.head())

# --- Streamlit form ---
with st.form("insert_form"):
    date = str(st.text_input("Date 2025-01-25"))
    czk = float(st.number_input("CZK"))
    eur = float(st.number_input("EUR"))
    us = float(st.number_input("US"))
    submitted = st.form_submit_button("Insert")

    if submitted:
        if date and czk and eur and us:
            try:
                with engine.begin() as conn:  # automatically commits
                    query = text("INSERT INTO public.test_table (date, rate_czk, rate_eur, rate_us) VALUES (:date, :czk, :eur, :us)")
                    conn.execute(query, {"date": date, "czk": czk, "eur": eur, "us": us})
                st.success(f"Inserted: {date}  {czk}, {eur}, {us}✅")
            except Exception as e:
                st.error(f"Insert failed: {e}")
        else:
            st.warning("Please enter a name before submitting.")

st.write(df.head())


range = st.radio("Date", options=["Last 10 days", "Last 30 days"])

       
if range == "Last 10 days":
    range = 2

if range == "Last 30 days":
    range = 3

st.write(range)

rate_czk_select = pd.read_sql(f"SELECT rate_czk FROM test_table LIMIT {range} ;", engine)

rate_eur_select = pd.read_sql(f"SELECT rate_eur FROM test_table LIMIT {range} ;", engine)

rate_us_select = pd.read_sql(f"SELECT rate_us FROM test_table LIMIT {range} ;", engine)

rate_czk_list = rate_czk_select["rate_czk"].tolist()
rate_eur_list = rate_eur_select["rate_eur"].tolist()
rate_us_list = rate_us_select["rate_us"].tolist()

st.write(rate_czk_list)
st.write(rate_eur_list)
st.write(rate_us_list)

chart_df = pd.DataFrame({
    "CZK" : rate_czk_list,
    "EUR" : rate_eur_list,
    "US" : rate_us_list
})

st.write(chart_df)

st.line_chart(
    chart_df,

)







