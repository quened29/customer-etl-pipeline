import pandas as pd 
import re
import os
import logging

from datetime import datetime
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

load_dotenv()

pd.set_option("display.max_columns", None)

server = os.getenv("DB_SERVER")
database = os.getenv("DB_NAME")
username = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

connection_string = (
    f"mssql+pyodbc://{username}:{password}@{server}/{database}"
    "?driver=ODBC+Driver+17+for+SQL+Server"
)

engine = create_engine(connection_string)

with engine.connect() as connection:
    logging.info("Connection successful!")

def extract():
    try:
        df = pd.read_csv("data/customers_raw.csv")
        return df

    except FileNotFoundError:
        logging.error("Source file not found.")
        return None

# Data Cleaning
def clean_names(df):
    df['customer_name'] = (
        df['customer_name']
        .str.strip()
        .str.title()
        .str.replace(r'\s+', ' ', regex=True)
    )

    return df

def clean_emails(df):
    # E-mail standardization
    df['email'] = df['email'].str.strip().str.lower()

    df['email'] = df['email'].replace('', pd.NA)

    # E-mail validation
    def valid_email(email):
        if pd.isna(email):
            return False
        return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email))

    df['email_valid'] = df['email'].apply(valid_email)

    # E-mail status
    def email_status(email): 
        if not valid_email(email):
            return "Check Email"
        return "OK"

    df['email_status'] = df['email'].apply(email_status)

    return df

def clean_dates(df):
    # Birth date standardization
    df["birth_date"] = pd.to_datetime(
        df["birth_date"],
        format="mixed",
        errors="coerce"
    )

    # Registration date standardization
    df["registration_date"] = pd.to_datetime(
        df["registration_date"],
        format="mixed",
        errors="coerce"
    )  

    return df

def clean_phone(df):
    # Phone standardization
    df["phone"] = pd.to_numeric(df["phone"], errors="coerce").astype("Int64")

    return df

def create_customer_features(df):
    # Birth date and age calculation
    df['age'] = datetime.now().year - df['birth_date'].dt.year 

    def age_group(age):
        if pd.isna(age):
            return "Unknown"
        elif age < 25:
            return "Young"
        elif age <= 34:
            return "Young Adult"
        elif age <= 44:
            return "Adult"
        else:
            return "Senior"
        
    df['age_range'] = df['age'].apply(age_group)

    # Customer tenure calculation
    df["customer_tenure"] = (datetime.now().year - df["registration_date"].dt.year)

    return df

# Duplicate Handling
def clean_duplicates(df):
    df = df.drop_duplicates()
    return df

# Data Validation
def validate_data(df):
    validation_passed = True

    if df.duplicated().any():
        logging.error("Duplicate records found.")
        validation_passed = False

    if not df["email_valid"].all():
        logging.warning("Invalid emails found.")

    if validation_passed:
        logging.info("Validation successful.")

    return validation_passed
    
def load(df):
    try:
        with engine.begin() as connection:
            connection.execute(text("TRUNCATE TABLE customers"))

            df.to_sql(
                "customers",
                con=connection,
                if_exists="append",
                index=False
            )

        logging.info("Data loaded successfully.")

    except Exception as e:
        logging.error(f"Data loading failed: {e}")

def transform(df):
    df = clean_names(df)
    df = clean_emails(df)
    df = clean_dates(df)
    df = clean_phone(df)
    df = create_customer_features(df)
    df = clean_duplicates(df)

    return df

def run_pipeline():
    df = extract()

    if df is None:
        return

    df = transform(df)

    if validate_data(df):
        load(df)
        
run_pipeline()

# df.to_csv("output/customers_clean.csv", index=False)




