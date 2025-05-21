import streamlit as st
import sqlalchemy

# Create the SQL connection to pets_db as specified in your secrets file.
conn = st.connection('pets_db', type='sql')

# Query and display the data you inserted
#pet_owners = conn.query('select * from pet_owners')
#st.dataframe(pet_owners)