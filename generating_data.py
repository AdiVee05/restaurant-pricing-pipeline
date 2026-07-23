from dotenv import load_dotenv
import os
from sqlalchemy import create_engine

from faker import Faker
fake = Faker()

import numpy as np
rng = np.random.default_rng()

import random
from datetime import datetime

import pandas as pd

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

restaurants_avaliable = []
menu_items_avaliable = []
PLU_duplicates = set()
full_transactions = []
for i in range(10): #restaurants
    name = "Wednesday's"
    location = fake.city()
    region = fake.state()
    store_number = random.randint(1000, 9999)
    restaurant_id = i+1
    restaurant = {"name": name, "location": location, "region": region, "store_number": store_number, "restaurant_id": restaurant_id}
    restaurants_avaliable.append(restaurant)

    #food_types = ["Burger", "Sandwich", "Fries", "Drink", "Tenders", "Chicken Nuggets"]
    #food_names = ["Dvinci Burger", "Medium Fries", "Small Fries", "Gator Sandwich", "Small Choc Chilly", "Large Choc Chilly", "Small Vanilla Chilly", "Large Vanilla Chilly", "Tendy Tenders", "Soda", "Philly Jalepeno Cheese Chicken"]
    menu_options = [{"name": "Dvinci Burger", "food_type": "Burger"}, {"name": "Medium Fries", "food_type": "Fries"}, {"name": "Small Fries", "food_type": "Fries"}, {"name": "Gator Sandwich", "food_type": "Sandwich"}, {"name": "Chocolate Chilly", "food_type": "Drink"}, {"name": "Vanilla Chilly", "food_type": "Drink"}, {"name": "Tendy Tenders", "food_type": "Tenders"}, {"name": "Soda", "food_type": "Drink"}, {"name": "Philly Jalepeno Cheese Chicken", "food_type": "Sandwich"}, ]
    
    for item in menu_options: #menu items
        name = item["name"]
        PLU = random.randint(10000, 99999)
        while PLU in PLU_duplicates:
            PLU = random.randint(10000, 99999)
        PLU_duplicates.add(PLU)
        base_cost = round(random.uniform(1.00, 9.00), 2)
        food_type = item["food_type"]
        ## Checking food_type
        if food_type == "Burger":
            base_cost = round(random.uniform(6.00, 9.00), 2)
        elif food_type == "Sandwich":
            base_cost = round(random.uniform(6.00, 9.00), 2)
        elif food_type == "Fries":
            base_cost = round(random.uniform(1.00, 3.00), 2)
        elif food_type == "Drink":
            base_cost = round(random.uniform(1.00, 2.00), 2)
        elif food_type == "Tenders":
            base_cost = round(random.uniform(5.00, 9.00), 2)
        elif food_type == "Chicken Nuggets":
            base_cost = round(random.uniform(4.00, 8.00), 2)
            
        menu_items = {"name": name, "PLU": PLU, "base_cost": base_cost, "food_type": food_type, "restaurant_id": restaurant_id}
        menu_items_avaliable.append(menu_items)

## Transactions
for t in range(90000):
    month = random.randint(1,12)
    day = random.randint(1,28)
    year = random.choice([2024,2025])

    transaction_id = t+1;
    restaurant_id = random.choice(restaurants_avaliable)["restaurant_id"] ##index needed to access specific id 
    TOT = random.randint(0,23) #(1,24)                                    ##instead of making random id
    amount = round(random.uniform(6.00, 15.00), 2)
    transactions = {"month": month, "day": day, "year": year, "transaction_id": transaction_id, "restaurant_id": restaurant_id, "TOT": TOT, "amount": amount}
    full_transactions.append(transactions)

#### price_history
change_reasons = ["Supply Cost Adjustment", "Seasonal Price Change", "Labor Changes", "Fuel Cost Change", "Menu Restructure"]
price_change_dates = [datetime(2024, 1, 16), datetime(2024, 3, 25), datetime(2024, 6, 11), datetime(2024, 9, 4), datetime(2025, 1, 5)]
price_id_counter = 0
price_history_avalible = []

for item in menu_items_avaliable:
    previous_price = item["base_cost"]

    for i, date in enumerate(price_change_dates):
        price = round((previous_price * random.uniform(1.10, 1.15)),2)
        change_reason = random.choice(change_reasons)
        price_id = price_id_counter
        if i == len(price_change_dates)-1:
            end_date = None
        else:
            end_date = price_change_dates[i+1]

        price_id_counter+=1
        previous_price = price 

        price_history = {"price": price, "PLU": item["PLU"], "effective_date": date, "change_reason": change_reason, "price_id": price_id, "end_date": end_date}
        price_history_avalible.append(price_history)

## transaction_items
transaction_items_avalible = []
t_id_count = 1

for transactions in full_transactions:
    menu_match = []

    for i in menu_items_avaliable:
        if i["restaurant_id"]==transactions["restaurant_id"]:
            menu_match.append(i)
    
    num_of_items= random.randint(1,4);
    receipt = random.sample(menu_match, num_of_items)

    for j in receipt:
        id = t_id_count
        restaurant_id = transactions["restaurant_id"]
        transaction_id = transactions["transaction_id"]
        PLU = j["PLU"]
        price_ats = j["base_cost"]
        quantity = random.randint(1,3)
        receipt_transactions = {"id": id, "restaurant_id": restaurant_id, "transaction_id": transaction_id, "PLU": PLU, "price_ats": price_ats, "quantity": quantity}
        transaction_items_avalible.append(receipt_transactions)
    
    t_id_count+=1

### importing data
##DataFrame.to_sql(name, con, *, schema=None, if_exists='fail', index=True, index_label=None, chunksize=None, dtype=None, method=None)

df_restaurants = pd.DataFrame(restaurants_avaliable)
df_restaurants.to_sql("restaurants", engine, if_exists="append", index=False)

df_menu_items = pd.DataFrame(menu_items_avaliable)
df_menu_items.to_sql("menu_items", engine, if_exists="append", index=False)

df_transactions = pd.DataFrame(full_transactions)
df_transactions.to_sql("transactions", engine, if_exists="append", index=False)

df_transaction_items = pd.DataFrame(transaction_items_avalible)
df_transaction_items.to_sql("transaction_items", engine, if_exists="append", index=False)

df_price_history = pd.DataFrame(price_history_avalible)
df_price_history.to_sql("price_history", engine, if_exists="append", index=False)