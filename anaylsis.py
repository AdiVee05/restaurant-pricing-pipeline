from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text

#from faker import Faker
#fake = Faker()
#import numpy as np
#rng = np.random.default_rng()

import random
from datetime import datetime

import pandas as pd
import logging

#from azure.storage.blob import BlobServiceClient
#import json
#from azure.storage.blob import BlobServiceClient
#import json

logging.basicConfig(level = logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", 
                    handlers = [logging.FileHandler("anaylsis.log"), logging.StreamHandler() ])

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

def get_volume_by_hour(restaurant_id, PLU):
    try:
        with engine.connect() as conn: 
                sql_result = conn.execute(text("""
                SELECT TOT, COUNT(*) as volume
                FROM transactions t
                JOIN transaction_items ti ON t.transaction_id = ti.transaction_id
                WHERE ti.PLU = :PLU
                AND t.restaurant_id = :restaurant_id
                GROUP BY TOT
                ORDER BY TOT
            """), {"PLU": PLU, "restaurant_id": restaurant_id})
                return sql_result.fetchall()
                
    except Exception as e:
        logging.error(f"Failed to get and join data: {e}")
        sql_result = []

#result = get_volume_by_hour(1, 53352)
#print(result)

""" def get_price_elasticity(PLU):
    try:
        with engine.connect() as conn: 
            elasticity_sql = conn.execute(text(SELECT price, effective_date, end_date, PLU 
            FROM price_history 
            WHERE PLU = :PLU
            ORDER BY effective_date), {"PLU": PLU})
            rows = elasticity_sql.fetchall()
            return rows
                 
    except Exception as e:
        logging.error(f"failed to get data: {e}")  
elasticity_result = get_price_elasticity(53352)
#print(elasticity_result) """

def get_volume_for_period(PLU, start_date, end_date):
    try:
        with engine.connect() as conn:
            volume_sql = conn.execute(text("""SELECT COUNT(*) as volume
                FROM transaction_items ti
                JOIN transactions t ON ti.transaction_id = t.transaction_id
                WHERE ti.PLU = :PLU
                AND DATEFROMPARTS(t.year, t.month, t.day) >= :start_date
                AND DATEFROMPARTS(t.year, t.month, t.day) < :end_date"""),  {"PLU": PLU, "start_date": start_date, "end_date": end_date})
            rows = volume_sql.fetchone()[0]
            return rows
    except Exception as e:
         logging.error(f"failed to get data: {e}")

#print(get_volume_for_period(53352, datetime(2024, 1, 16), datetime(2024, 3, 25)))

def get_price_elasticity(PLU):
    try: 
        #elasticity = (% change in volume) / (% change in price)
        with engine.connect() as conn: 
            elasticity_sql = conn.execute(text("""SELECT price, effective_date, end_date, PLU 
            FROM price_history 
            WHERE PLU = :PLU
            ORDER BY effective_date"""), {"PLU": PLU})
            rows = elasticity_sql.fetchall()
            results = []
            for i, row in enumerate(rows):
                if (i == 0):
                    continue;
                previous_row = rows[i-1]
                previous_price = previous_row[0]
                new_price = row[0]

                volume_before = get_volume_for_period(PLU, previous_row[1], row[1])
                #volume_after = get_volume_for_period(PLU, row[1], row[2])
                end = row[2] if row[2] is not None else datetime(2025, 12, 29)
                #Generator only creates dates till Dec 28th 2025 because sales only exist for that range
                volume_after = get_volume_for_period(PLU, row[1], end)

                days_before = (row[1] - previous_row[1]).days
                days_after = (end - row[1]).days
                rate_before = volume_before / days_before
                rate_after = volume_after / days_after

                pct_price_change = (new_price - previous_price) / (previous_price)
                pct_volume_change = (rate_after - rate_before) / rate_before
                elasticity = pct_volume_change / pct_price_change

                results.append({
                    "PLU": PLU,
                    "effective_date": row[1],
                    "previous_price": previous_price,
                    "new_price": new_price,
                    "volume_before": volume_before,
                    "volume_after": volume_after,
                    "elasticity": elasticity
                })
            return results

    except Exception as e:
        logging.error(f"failed to get data {e}")

print(get_price_elasticity(53352))