from faker import Faker
fake = Faker()
import numpy as np
rng = np.random.default_rng()
import random

restaurants_avaliable = []
menu_items_avaliable = []
PLU_duplicates = set()

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
        elif food_type == "Sandwich":
            base_cost = round(random.uniform(6.00, 9.00), 2)
            
        menu_items = {"name": name, "PLU": PLU, "base_cost": base_cost, "food_type": food_type, "restaurant_id": restaurant_id}
        menu_items_avaliable.append(menu_items)
       