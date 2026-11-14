from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from anaylsis import engine, get_price_elasticity, get_revenue_impact, compare_categories, get_volume_by_hour

app = FastAPI(title="Restaurant Pricing API")

def rows_to_dicts(result):
    # turns SQL rows into dictionaries so FastAPI can send them as JSON
    return [dict(r._mapping) for r in result.fetchall()]

@app.get("/")
def root():
    return {"status": "alive"}

@app.get("/restaurants")
def list_restaurants():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT restaurant_id, store_number, name, location, region FROM restaurants"))
        return rows_to_dicts(result)

@app.get("/restaurants/{restaurant_id}/menu")
def restaurant_menu(restaurant_id: int):
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT PLU, name, food_type, base_cost
            FROM menu_items
            WHERE restaurant_id = :restaurant_id
        """), {"restaurant_id": restaurant_id})
        menu = rows_to_dicts(result)
    if(not menu):
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return menu

@app.get("/items/{PLU}/price-history")
def price_history(PLU: int):
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT price, effective_date, end_date, change_reason
            FROM price_history
            WHERE PLU = :PLU
            ORDER BY effective_date
        """), {"PLU": PLU})
        history = rows_to_dicts(result)
    if(not history):
        raise HTTPException(status_code=404, detail="Item not found")
    return history

@app.get("/items/{PLU}/elasticity")
def item_elasticity(PLU: int):
    changes = get_price_elasticity(PLU)
    if(not changes):
        raise HTTPException(status_code=404, detail="Item not found")
    return changes

@app.get("/restaurants/{restaurant_id}/insights")
def restaurant_insights(restaurant_id: int):
    return {"restaurant_id": restaurant_id, "categories": compare_categories(restaurant_id)}

@app.get("/restaurants/{restaurant_id}/items/{PLU}/volume-by-hour")
def volume_by_hour(restaurant_id: int, PLU: int):
    rows = get_volume_by_hour(restaurant_id, PLU)
    return [{"hour": r[0], "volume": r[1]} for r in rows]

@app.post("/simulate")
def simulate(PLU: int, price_change_pct: float):
    result = get_revenue_impact(PLU, price_change_pct)
    if(result is None):
        raise HTTPException(status_code=404, detail="Item not found")
    return result