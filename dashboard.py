import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "https://restaurant-pricing-pipeline.azurewebsites.net")

st.set_page_config(page_title="Wednesday's Pricing", layout="wide")

@st.cache_data(ttl=600)
def get_json(path):
    # cached so the page doesn't re-call the API on every click
    r = requests.get(f"{API_URL}{path}", timeout=60)
    r.raise_for_status()
    return r.json()

st.title("Wednesday's Price Simulator")
st.caption("Pick a menu item and a price change to see projected daily revenue, based on its historical price elasticity.")

try:
    restaurants = get_json("/restaurants")
except Exception:
    st.error("Couldn't reach the API. The database may be waking up, so refresh in a minute.")
    st.stop()

stores = {f"Store #{r['store_number']} ({r['location']}, {r['region']})": r["restaurant_id"] for r in restaurants}
store = st.selectbox("Restaurant", list(stores))

menu = get_json(f"/restaurants/{stores[store]}/menu")
items = {f"{m['name']} (PLU {m['PLU']})": m["PLU"] for m in menu}
item = st.selectbox("Menu item", list(items))

pct = st.slider("Price change (%)", -30, 30, 10)

if st.button("Simulate"):
    with st.spinner("Running the numbers..."):
        r = requests.post(f"{API_URL}/simulate",
                          params={"PLU": items[item], "price_change_pct": pct}, timeout=60)
    if (r.status_code != 200):
        st.error(f"Simulation failed ({r.status_code}). Try again in a minute.")
    else:
        res = r.json()
        c1, c2, c3 = st.columns(3)
        c1.metric("New price", f"${res['new_price']:.2f}", f"{pct:+}%")
        c2.metric("Projected daily revenue", f"${res['projected_daily_revenue']:.2f}",
                  f"{res['revenue_change_pct']:+}%")
        c3.metric("Elasticity", res["avg_elasticity"])

        e = res["avg_elasticity"]
        if (e > -1):
            st.info("Inelastic: customers barely react to price, so raising it tends to increase revenue.")
        else:
            st.warning("Elastic: customers are price-sensitive, so raising it tends to cost revenue.")