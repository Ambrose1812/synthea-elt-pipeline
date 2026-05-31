# Import packages
import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load secrets
load_dotenv()

# Pull the six values out of the environment
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Create Engine Connection
connection_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(connection_string)

# Synthea CSVs path
CSV_DIR = r"C:\Official_HC_Projects\synthea-tool\output\csv"

# Tables list
tables = ['patients', 'encounters']

# Loop through the tables and load each into the database
for table in tables:
    print(f"loading {table}...")
    df = pd.read_csv(f"{CSV_DIR}\\{table}.csv")
    df.to_sql(table, con=engine, schema="raw", if_exists="replace", chunksize=10000)
    print(f"  done — {len(df)} rows")