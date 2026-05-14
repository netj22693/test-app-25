import os
import requests
import json
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float,DateTime, BigInteger
from sqlalchemy.orm import declarative_base, Session
from typing import Optional
from datetime import datetime, timezone
from dotenv import load_dotenv
# import streamlit as st

# Only for local testing - PROD uses Github Actions secrets
if os.path.exists(".env"):
    load_dotenv()

# For debbugging
print("RUN AT:", datetime.now(timezone.utc))

# DB connection
def get_db_connection():
    try: 

        password = os.getenv("NEON_DB_PASSWORD")
        endpoint = os.getenv("NEON_DB_ENDPOINT")

        # connection string
        conn_string = f"postgresql+psycopg2://neondb_owner:{password}@{endpoint}.gwc.azure.neon.tech/neondb?sslmode=require"

        engine = create_engine(conn_string)
        return engine
    
    except Exception as e:
        print(f"DB connection failed: {e}")

# API calls 
def api_GET_request(url_string: str, api: str) -> Optional[str]: 

    try:
        api_response = requests.get(url_string, verify=False, timeout=5).text
        reason = None
        state = "SUCCESS"

        return api_response, reason, state

    except Exception as e:
        print(f"Error GET request: {e}")
        api_response  = None
        reason = f"{api} - GET request: {str(e)}"
        state = "FAIL"

        return api_response, state, reason


def api_1_kurzy_parsing(data_input: str) -> Optional[float]:

    try:
        data_json = json.loads(data_input)

        # Search for data in the API defined format - JSON
        eur_rate_parsed = data_json['kurzy']['EUR']['dev_stred']
        usd_rate_parsed = data_json['kurzy']['USD']['dev_stred']

        eur_rate_parsed = round(eur_rate_parsed, 3)
        usd_rate_parsed = round(usd_rate_parsed, 3)

        state = "SUCCESS"
        reason = None

        return eur_rate_parsed, usd_rate_parsed, state, reason

    except Exception as e:
        print(f"Error parsing API 1: {e}")

        eur_rate_parsed = None
        usd_rate_parsed = None
        state = "FAIL"
        reason = f"API 1 - parsing: {str(e)}"
        return eur_rate_parsed, usd_rate_parsed, state, reason


def api_2_freecurrency_parsing(data_input: str) -> Optional[float]:

    try:
        data_json = json.loads(data_input)

        # Search for data in the API defined format - JSON
        eur_to_usd_rate_parsed = data_json['data']['USD']
        eur_to_usd_rate_parsed = round(eur_to_usd_rate_parsed, 3)
        
        state = "SUCCESS"
        reason = None

        return eur_to_usd_rate_parsed, state, reason

    except Exception as e:
        print(f"Error parsing API 2: {e}")

        eur_to_usd_rate_parsed = None
        state = "FAIL"
        reason = f"API 2 - parsing: {str(e)}"

        return eur_to_usd_rate_parsed, state, reason


def get_run_context() -> dict:
    '''
    Function for logging purposes to be able to track the schedulers run from Github Actions
    Outcome dict -> values saved into DB
    '''

    run_id = os.getenv("GITHUB_RUN_ID")
    repo = os.getenv("GITHUB_REPOSITORY")
    url_link = f"https://github.com/{repo}/actions/runs/{run_id}"

    # ----- For test purposes ----- 
    test = {
        "run_id": "111111112",
        "run_url": "https://github.com/netj22693/backup-app-jn/actions/runs/111111111",
        "event": "test_from_codespace",
        "repo": repo
        }

    prod = {
        "run_id": run_id,
        "run_url": url_link,
        "event": os.getenv("GITHUB_EVENT_NAME"),
        "repo": repo
    }

    return prod
    #return test


def insert_exchange_rate_data(engine, data, reason_1, reason_2):


    actual_time = datetime.now(timezone.utc)

    env_logs = get_run_context()

    Base = declarative_base()

    class Rate(Base):
        __tablename__ = "exchange_rate_data"
        __table_args__ = {"schema": "function5"}

        id = Column(Integer, primary_key=True, autoincrement=True)
        created_at = Column(DateTime(timezone=True))

        cz_to_eur = Column(Float)
        cz_to_eur_state = Column(String)

        cz_to_usd = Column(Float)
        cz_to_usd_state = Column(String)

        eur_to_usd = Column(Float)
        eur_to_usd_state = Column(String)


    class Failure_api_1(Base):
        __tablename__ = "api_kurzy_failure"
        __table_args__ = {"schema": "function5"}

        id = Column(Integer, primary_key=True, autoincrement=True)
        exchange_rate_id = Column(Integer)
        failure = Column(String)


    class Failure_api_2(Base):
        __tablename__ = "api_freecurrency_failure"
        __table_args__ = {"schema": "function5"}

        id = Column(Integer, primary_key=True, autoincrement=True)
        exchange_rate_id = Column(Integer)
        failure = Column(String)
    
    class Scheduler(Base):
        __tablename__ = "scheduler"
        __table_args__ = {"schema": "function5"}     

        id = Column(Integer, primary_key=True, autoincrement=True)   
        exchange_rate_id = Column(Integer)
        github_run_id = Column(BigInteger)
        github_run_url = Column(String)
        event = Column(String)
        run_at = Column(DateTime(timezone=True))
        github_repo = Column(String)

        
    with Session(engine) as session:

            new_rate = Rate(
                created_at=actual_time,
                **data
            )
            session.add(new_rate)

            session.flush()
            rate_id = new_rate.id

            if reason_1 is not None:
                session.add(
                    Failure_api_1(
                        exchange_rate_id=rate_id,
                        failure=reason_1
                    )
                )

            if reason_2 is not None:
                session.add(
                    Failure_api_2(
                        exchange_rate_id=rate_id,
                        failure=reason_2
                    )
                )

            session.add(
                Scheduler(
                    exchange_rate_id=rate_id,
                    github_run_id=env_logs["run_id"],
                    github_run_url=env_logs["run_url"], 
                    event=env_logs["event"],
                    run_at = actual_time,
                    github_repo=env_logs["repo"]
                )
            )

            session.commit()

def main():


    conn = get_db_connection()

    # =================== Build of API strings =================== 
    api_1_kurzy_url_string = "https://data.kurzy.cz/json/meny/b[1].json"

    secrets_api_2 = os.getenv("F5_API_2_PASSWORD")

    api_2_freecurrency_url_string = f"https://api.freecurrencyapi.com/v1/latest?apikey={secrets_api_2}&currencies=USD&base_currency=EUR"


    # =================== API call ===================
    api_1_kurzy, api_1_state, api_1_reason  = api_GET_request(api_1_kurzy_url_string, "API 1")
    api_2_freecurrency, api_2_state, api_2_reason = api_GET_request(api_2_freecurrency_url_string, "API 2")

    if api_1_kurzy is not None:
        eur_rate, usd_rate, api_1_state, api_1_reason = api_1_kurzy_parsing(api_1_kurzy)
    
    if api_1_kurzy is None:
        eur_rate = None
        usd_rate = None
    
    if api_2_freecurrency is not None:
        eur_to_usd_rate, api_2_state, api_2_reason = api_2_freecurrency_parsing(api_2_freecurrency)
    
    if api_2_freecurrency is None:
        eur_to_usd_rate = None


    # mapping 
    mapped_data_exhange_rate_table = {
        "cz_to_eur": eur_rate,
        "cz_to_eur_state": api_1_state,
        "cz_to_usd" : usd_rate,
        "cz_to_usd_state" : api_1_state,
        "eur_to_usd": eur_to_usd_rate,
        "eur_to_usd_state" : api_2_state
        }

    try:
        insert_exchange_rate_data(conn, mapped_data_exhange_rate_table, api_1_reason, api_2_reason)
        print("All complete")



    except Exception as e:
        print(f"[DB ERROR]: {e}")
    
if __name__ == "__main__":
    main()

# ----- For test purposes ----- 
# if st.button("test"):
#     main()
    