import os
import requests
import pandas as pd
import streamlit as st
from plotly.subplots import make_subplots

API_URL = os.getenv("API_URL", "https://restaurant-pricing-pipeline.azurewebsites.net")
DATA_END = pd.Timestamp(2025, 12, 28)   # generated sales stop here

st.set_page_config(page_title="Wednesday's Pricing", layout="wide")

@st.cache_data(ttl=600)
def get_json(path):
    # cached so the page doesn't re-call the API on every click
    r = requests.get(f"{API_URL}{path}", timeout=60)
    r.raise_for_status()
    return r.json()

try:
    restaurants = get_json("/restaurants")
except Exception:
    st.error("Couldn't reach the API. The database may be waking up, so refresh in a minute.")
    st.stop()

st.sidebar.title("🍟 Wednesday's")
st.sidebar.caption("Menu pricing analytics")
# sidebar: page picker plus shared rstaurant/item pickers
page = st.sidebar.radio("Page", ["How It Works", "Price Simulator", "Price History"])
stores = {f"Store #{r['store_number']} ({r['location']}, {r['region']})": r["restaurant_id"] for r in restaurants}
store = st.sidebar.selectbox("Restaurant", list(stores))

menu = get_json(f"/restaurants/{stores[store]}/menu")
items = {f"{m['name']} (PLU {m['PLU']})": m["PLU"] for m in menu}
item = st.sidebar.selectbox("Menu item", list(items))
PLU = items[item]

########################################################################
if (page == "How It Works"):
    st.title("🍟 Wednesday's Pricing Analytics")
    st.markdown("""
A cloud data pipeline that answers one question a restaurant manager actually asks:
**if we raise the price of this item, do we make more money or less?**

Inspired by seeing how pricing decisions get made across locations while working with
POS systems at Wendy's.
""")

    st.subheader("How to use it")
    c1, c2, c3 = st.columns(3)
    c1.markdown("**1. Pick an item**  \nChoose a restaurant and menu item in the sidebar.")
    c2.markdown("**2. See its history**  \n**Price History** shows every price change next to monthly sales.")
    c3.markdown("**3. Simulate**  \n**Price Simulator** projects revenue for any price change you try.")

    st.subheader("What is price elasticity?")
    st.markdown("""
Elasticity measures how much sales react when the price changes:

`elasticity = % change in sales ÷ % change in price`

| Elasticity | Meaning | Raising the price... |
|---|---|---|
| 0 to -1 | **Inelastic**: customers barely react | usually increases revenue |
| -1 | Breakeven | revenue stays about the same |
| below -1 | **Elastic**: customers are price-sensitive | usually costs revenue |

For example, an elasticity of -0.5 means a 10% price increase loses about 5% of sales,
so revenue goes up.
""")

    st.subheader("How it's built")
    st.markdown("""
- **Data:** 10 locations, 90 menu items, 90,000 transactions over 2 years, generated in Python
- **Storage:** Azure SQL for queryable data, Azure Blob Storage for raw daily JSON dumps
- **Ingestion:** a Python script that loads each day's transactions with logging and error handling
- **API:** FastAPI on Azure App Service, which runs the elasticity and revenue math
- **Dashboard:** this Streamlit app, which calls the API
""")

    st.info("""
**About the data:** it's synthetic. Each food category was given a known price sensitivity
(burgers most sensitive, drinks least), and the analysis recovers those values within
sampling noise. That's how the elasticity math was validated.
""")
    
elif (page == "Price Simulator"):
    st.title("Wednesday's Price Simulator")
    st.caption("Pick a price change to see projected daily revenue, based on the item's historical price elasticity.")
    with st.expander("How to read this"):
        st.markdown("Slide the price change and hit **Simulate**. The projection uses this item's average elasticity from its price history. Green revenue means the change makes money; red means it loses money. The model assumes customer sensitivity stays constant, so treat big changes like +30% as rough estimates.")
    pct = st.slider("Price change (%)", -30, 30, 10)

    if st.button("Simulate"):
        with st.spinner("Running the numbers..."):
            r = requests.post(f"{API_URL}/simulate",
                              params={"PLU": PLU, "price_change_pct": pct}, timeout=60)
        if (r.status_code != 200):
            st.error(f"Simulation failed ({r.status_code}). Try again in a minute.")
        else:
            res = r.json()
            c1, c2, c3 = st.columns(3)
            c1.metric("New price", f"${res['new_price']:.2f}", f"{pct:+}%")
            c2.metric("Projected daily revenue", f"${res['projected_daily_revenue']:.2f}",
                      f"{res['revenue_change_pct']:+}%")
            c3.metric("Elasticity", res["avg_elasticity"])

            if (res["avg_elasticity"] > -1):
                st.info("Inelastic: customers barely react to price, so raising it tends to increase revenue.")
            else:
                st.warning("Elastic: customers are price-sensitive, so raising it tends to cost revenue.")

########################################################################
elif (page == "Price History"):
    st.title("Price vs. Sales Volume")
    st.caption("Bars are orders per month. The line is the menu price. Watch the bars step down after each price increase.")
    with st.expander("How to read this"):
        st.markdown("The orange line is the item's price, stepping up at each change. The gray bars are orders per month. If the bars drop after a price step, customers are reacting to the price. The table below shows the elasticity for each change. Burgers drop the most, drinks the least.")
    history = pd.DataFrame(get_json(f"/items/{PLU}/price-history"))
    monthly = pd.DataFrame(get_json(f"/items/{PLU}/monthly-volume"))
    changes = pd.DataFrame(get_json(f"/items/{PLU}/elasticity"))

    # stat cards across the top
    first_price = history["price"].iloc[0]
    last_price = history["price"].iloc[-1]
    c1, c2, c3 = st.columns(3)
    c1.metric("Current price", f"${last_price:.2f}")
    c2.metric("Total price increase", f"{(last_price/first_price-1)*100:.0f}%", f"{len(history)-1} changes")
    c3.metric("Avg elasticity", round(changes["elasticity"].mean(), 2))

    # turn year + month into a real date for the x axis
    monthly["date"] = pd.to_datetime(monthly[["year", "month"]].assign(day=1))

    # price line: each price holds until the next change, the last one runs to the end of the data
    history["effective_date"] = pd.to_datetime(history["effective_date"])
    price_x = list(history["effective_date"]) + [DATA_END]
    price_y = list(history["price"]) + [last_price]

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_bar(x=monthly["date"], y=monthly["orders"], name="Orders per month",
                marker_color="#3A4250", secondary_y=False)
    fig.add_scatter(x=price_x, y=price_y, name="Price", mode="lines",
                    line_shape="hv", line_width=3, line_color="#F25C2E", secondary_y=True)
    fig.update_yaxes(title_text="Orders per month", showgrid=False, secondary_y=False)
    fig.update_yaxes(title_text="Price ($)", tickprefix="$", gridcolor="#2A2F38", secondary_y=True)
    fig.update_layout(height=450, legend=dict(orientation="h", y=1.1),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      margin=dict(t=40, b=20))
    st.plotly_chart(fig)

    st.subheader("Price changes")
    changes["effective_date"] = pd.to_datetime(changes["effective_date"]).dt.date
    changes["elasticity"] = changes["elasticity"].round(2)
    st.dataframe(changes[["effective_date", "previous_price", "new_price", "elasticity"]],
                 hide_index=True)