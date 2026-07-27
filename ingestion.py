from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text

from faker import Faker
fake = Faker()

import numpy as np
rng = np.random.default_rng()

import random
from datetime import datetime

import pandas as pd

import logging

#from azure.storage.blob import BlobServiceClient
#import json

from azure.storage.blob import BlobServiceClient
import json

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

##logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
""" while True:
    try:
        x = int(input("Please enter a number: "))
        break
    except ValueError:
        print("Oops!  That was no valid number.  Try again...") """

logging.basicConfig(level = logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", 
                    handlers = [logging.FileHandler("ingestion.log"), logging.StreamHandler() ])

try:
    with engine.connect() as conn: ## connection for table with transact ids
        result = conn.execute(text("SELECT MAX(transaction_id) FROM transactions"))
        max_id = result.fetchone()[0]
        logging.info(f"max_id aqquired: {max_id}")
except Exception as e:
    logging.error(f"Failed to get max_id: {e}")
    max_id = 0

""" with engine.connect() as conn: ## connection for table with transact ids
    result = conn.execute(text("SELECT MAX(transaction_id) FROM transactions"))
    max_id = result.fetchone()[0]
    logging.info(f"max_id aqquired: {max_id}") """

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT restaurant_id FROM restaurants")) ## connection to table with rest ids
        restaurant_ids = [row[0] for row in result.fetchall()]
        logging.info(f"restaurant_id aqquired: {restaurant_ids}")
except Exception as e:
    logging.error(f"Failed to get restaurant_id: {e}")
    restaurant_ids = []
    
""" with engine.connect() as conn:
    result = conn.execute(text("SELECT restaurant_id FROM restaurants")) ## connection to table with rest ids
    restaurant_ids = [row[0] for row in result.fetchall()]
    logging.info(f"restaurant_id aqquired: {restaurant_ids}") """

###############################################################################################
### NOT NEEDED
""" with engine.connect() as conn:
    result = conn.execute(text("SELECT TOT FROM transactions")) ## connection to table with rest ids
    TOTs_s = [row[0] for row in result.fetchall()]
    logging.info(f"TOTs aqquired: {TOTs_s}")

with engine.connect() as conn:
    result = conn.execute(text("SELECT amount FROM transactions")) ## connection to table TOTS which is in transactions
    amounts = [row[0] for row in result.fetchall()]
    logging.info(f"amounts aqquired: {amounts}") """
###############################################################################################

daily_transactions = []
today = datetime.now()
day = today.day
month = today.month
year = today.year
for i in range(123):
    transaction_id = max_id + 1 + i #have to increment
    restaurant_id = random.choice(restaurant_ids)
    TOT = random.randint(0,23)
    amount = round(random.uniform(6.00, 15.00))
    daily_load = {"day": day, "year": year, "month": month, "transaction_id": transaction_id, "restaurant_id": restaurant_id, "TOT": TOT, "amount": amount}
    daily_transactions.append(daily_load)

try:
    blob_service_client = BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
    #BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
    container_client = blob_service_client.get_container_client("restaurantpipelineblobed")
    blob_name = f"{today.strftime('%Y-%m-%d')}.json"
    blob_data = json.dumps(daily_transactions, default=str)
    container_client.upload_blob(blob_name, blob_data, overwrite=True)
except Exception as e:
    logging.error(f"Failed to make blob: {e}")

try:
    df_daily = pd.DataFrame(daily_transactions)
    df_daily.to_sql("transactions", engine, if_exists="append", index=False)
    logging.info("Inserted daily transactions successfully")
except Exception as e:
    logging.error(f"Failed to upload new data: {e}")
    max_id = 0
    
""" df_daily = pd.DataFrame(daily_transactions)
df_daily.to_sql("transactions", engine, if_exists="append", index=False)
logging.info("Inserted daily transactions successfully")
 """



