import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Page Config for Mobile
st.set_page_config(page_title="Inversion Engine", layout="centered")

st.title("🧮 Inversion Engine")
st.caption("A Munger-inspired tool for rational investors.")

# 2. The Dividend Goal Tool (User Inputs)
with st.container(border=True):
    st.subheader("🎯 Dividend Target")
    ticker = st.text_input("Stock Ticker (e.g., ADBE, GAMA.L, KO)", value="KO").upper()
    target_income = st.number_input("Desired Annual Income (£/$)", value=1000)

    if ticker:
        stock = yf.Ticker(ticker)
        # Fetching price and yield
        price = stock.fast_info['lastPrice']
        div_yield = stock.info.get('dividendYield', 0)

        if div_yield and div_yield > 0:
            shares_needed = target_income / (price * div_yield)
            total_investment = shares_needed * price
            
            # Mobile-friendly metrics
            m1, m2 = st.columns(2)
            m1.metric("Shares Needed", f"{int(shares_needed):,}")
            m2.metric("Total Cost", f"£{total_investment:,.2f}")
            st.write(f"Current Yield: **{div_yield*100:.2f}%** | Price: **{price:.2f}**")
        else:
            st.warning("Yield data not found for this ticker.")

# 3. The Munger Hierarchy (Simple Table)
st.divider()
st.subheader("📋 The Hierarchy")
hierarchy_data = {
    "Stock": ["Adobe", "Uber", "Coca-Cola"],
    "Trigger": ["$250", "$68", "$72"],
    "Status": ["Watching", "Watching", "Fair Value"]
}
st.table(pd.DataFrame(hierarchy_data))

# 4. Mandatory Disclaimer (For hobby/informational use)
st.divider()
st.caption("NOT FINANCIAL ADVICE. For informational purposes only. "
           "Dividends are never guaranteed.")