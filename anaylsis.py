from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
from datetime import datetime
import logging

logging.basicConfig(level = logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", 
                    handlers = [logging.FileHandler("anaylsis.log"), logging.StreamHandler() ])

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

DATA_END = datetime(2025, 12, 29)   # generator only makes sales till Dec 28th 2025

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
        return []

def get_volume_for_period(PLU, start_date, end_date):
    try:
        with engine.connect() as conn:
            volume_sql = conn.execute(text("""SELECT COUNT(*) as volume
                FROM transaction_items ti
                JOIN transactions t ON ti.transaction_id = t.transaction_id
                WHERE ti.PLU = :PLU
                AND DATEFROMPARTS(t.year, t.month, t.day) >= :start_date
                AND DATEFROMPARTS(t.year, t.month, t.day) < :end_date"""),
                {"PLU": PLU, "start_date": start_date, "end_date": end_date})
            return volume_sql.fetchone()[0]
    except Exception as e:
        logging.error(f"failed to get data: {e}")

def get_price_elasticity(PLU):
    #elasticity = (% change in volume) / (% change in price)
    try:
        with engine.connect() as conn:
            elasticity_sql = conn.execute(text("""SELECT price, effective_date, end_date, PLU
                FROM price_history
                WHERE PLU = :PLU
                ORDER BY effective_date"""), {"PLU": PLU})
            rows = elasticity_sql.fetchall()

        results = []
        for i, row in enumerate(rows):
            if (i == 0):
                continue
            previous_row = rows[i-1]
            previous_price = previous_row[0]
            new_price = row[0]

            end = row[2] if row[2] is not None else DATA_END

            volume_before = get_volume_for_period(PLU, previous_row[1], row[1])
            volume_after = get_volume_for_period(PLU, row[1], end)

            days_before = (row[1]-previous_row[1]).days
            days_after = (end-row[1]).days
            rate_before = volume_before/days_before
            rate_after = volume_after/days_after

            pct_price_change = (new_price-previous_price)/previous_price
            pct_volume_change = (rate_after-rate_before)/rate_before
            elasticity = pct_volume_change/pct_price_change

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
        return []

def get_revenue_impact(PLU, price_change_pct):
    changes = get_price_elasticity(PLU)
    if (not changes):
        return None
    avg_elasticity = sum(c["elasticity"] for c in changes)/len(changes)

    last = changes[-1]
    current_price = last["new_price"]
    days = (DATA_END-last["effective_date"]).days
    current_daily_volume = last["volume_after"]/days

    new_price = current_price*(1 + price_change_pct/100)
    new_daily_volume = current_daily_volume*(1 + avg_elasticity*price_change_pct/100)

    current_revenue = current_price*current_daily_volume
    new_revenue = new_price*new_daily_volume

    return {
        "PLU": PLU,
        "avg_elasticity": round(avg_elasticity, 2),
        "current_price": current_price,
        "new_price": round(new_price, 2),
        "current_daily_revenue": round(current_revenue, 2),
        "projected_daily_revenue": round(new_revenue, 2),
        "revenue_change_pct": round((new_revenue/current_revenue-1)*100, 1)
    }

def compare_categories(restaurant_id):
    try:
        with engine.connect() as conn:
            items = conn.execute(text("""
                SELECT PLU, food_type
                FROM menu_items
                WHERE restaurant_id = :restaurant_id
            """), {"restaurant_id": restaurant_id}).fetchall()
    except Exception as e:
        logging.error(f"failed to get menu items: {e}")
        return []

    by_type = {}   # food_type -> list of each item's average elasticity
    for plu, food_type in items:
        changes = get_price_elasticity(plu)
        if (not changes):
            continue
        item_avg = sum(c["elasticity"] for c in changes)/len(changes)
        if (food_type not in by_type):
            by_type[food_type] = []
        by_type[food_type].append(item_avg)

    results = []
    for food_type, values in by_type.items():
        results.append({"food_type": food_type, "avg_elasticity": round(sum(values)/len(values), 2)})

    results.sort(key=lambda r: r["avg_elasticity"])   # most negative first
    return results

# tests only run when this file is run directly, not when FastAPI imports it
if __name__ == "__main__":
    TEST_PLU = 0   # put a real PLU from menu_items here
    print(get_revenue_impact(11416, 10))
    print(compare_categories(1))