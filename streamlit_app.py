
    
import streamlit as st
import yfinance as yf
import pandas as pd
from pytickersymbols import PyTickerSymbols

# Simple Practice Gate
if st.text_input("Enter Practice Key", type="password") != "munger2026":
    st.stop() # Stops the rest of the app from loading

st.set_page_config(page_title="Inversion Engine Pro", layout="wide")

# --- 1. The Stock Universe ---
@st.cache_data
def get_universe():
    pts = PyTickerSymbols()
    indices = [
        pts.get_ftse_100_london_yahoo_tickers(),
        pts.get_nasdaq_100_nyc_yahoo_tickers(),
        pts.get_dow_jones_nyc_yahoo_tickers()
    ]
    return sorted(list(set([t for idx in indices for t in idx])))

# --- 2. The Munger Scoring Engine ---
def calculate_munger_score(row, target_yield):
    score = 0
    # Yield Check (30 points)
    if row['Yield %'] >= target_yield: score += 30
    elif row['Yield %'] > 0: score += 15
    
    # Debt Check (30 points) - Inversion: Less is more
    if row['Debt/EBITDA'] <= 2: score += 30
    elif row['Debt/EBITDA'] <= 4: score += 15
    
    # Insider Check (20 points)
    if row['Insider %'] >= 5: score += 20
    elif row['Insider %'] >= 1: score += 10
    
    # Value Check (20 points) - Simulating P/E vs History
    if row['P/E'] < 15: score += 20
    elif row['P/E'] < 25: score += 10
    
    return score

# --- 3. Data Processing ---
@st.cache_data(ttl=3600)
def scan_markets(tickers, limit=50):
    results = []
    for symbol in tickers[:limit]:
        try:
            t = yf.Ticker(symbol)
            info = t.info
            price = info.get('currentPrice', 1)
            ebitda = info.get('ebitda', 0)
            debt = info.get('totalDebt', 0)
            
            data = {
                "Ticker": symbol,
                "Name": info.get('shortName', 'Unknown'),
                "Price": price,
                "Yield %": (info.get('dividendRate', 0) / price * 100),
                "Debt/EBITDA": (debt / ebitda) if ebitda > 0 else 99,
                "Insider %": info.get('heldPercentInsiders', 0) * 100,
                "P/E": info.get('forwardPE', 99)
            }
            results.append(data)
        except: continue
    return pd.DataFrame(results)

# --- 4. Sidebar & Controls ---
st.title("🧮 Inversion Engine")
st.sidebar.header("🎯 Your Requirements")
user_yield = st.sidebar.slider("Min Dividend Yield %", 0.0, 10.0, 3.5)
scan_limit = st.sidebar.select_slider("Scan Depth", options=[20, 50, 100, "Full"], value=50)

if st.sidebar.button("🚀 Run Munger Scan"):
    st.cache_data.clear()

# --- 5. Main Logic & Sorting ---
all_tickers = get_universe()
limit_val = len(all_tickers) if scan_limit == "Full" else scan_limit

with st.spinner(f"Inverting {limit_val} stocks..."):
    df = scan_markets(all_tickers, limit=limit_val)
    
    if not df.empty:
        # Calculate Scores
        df['Munger Score'] = df.apply(lambda x: calculate_munger_score(x, user_yield), axis=1)
        
        # UX IMPROVEMENT: The "Strict Hierarchy" Filter
        # 1. Filter by your sidebar requirements
        mask = (df['Yield %'] >= user_yield) & (df['Munger Score'] >= 40)
        filtered_df = df[mask].copy()
        
        # 2. SORT by Score (Highest First) then Yield
        filtered_df = filtered_df.sort_values(by=['Munger Score', 'Yield %'], ascending=[False, False])

# --- 6. The Results Display ---
st.subheader("🏆 The 'Fat Pitch' Shortlist")

if not filtered_df.empty:
    # UX IMPROVEMENT: Dynamic column formatting
    st.dataframe(
        filtered_df.style.background_gradient(subset=['Munger Score'], cmap='RdYlGn')
        .format({
            "Yield %": "{:.2f}%",
            "Debt/EBITDA": "{:.1f}x",
            "Insider %": "{:.2f}%",
            "Price": "{:.2f}",
            "P/E": "{:.1f}"
        }),
        use_container_width=True,
        hide_index=True
    )
    
    # Download Button
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Shortlist (CSV)", csv, "munger_shortlist.csv", "text/csv")
else:
    st.warning("No stocks currently meet your requirements. Try lowering the 'Min Yield' or increasing 'Scan Depth'.")
st.divider()
st.divider()
st.caption("🚨 **PERSONAL HOBBY PROJECT - NOT FOR COMMERCIAL USE**")
st.caption("""
    **DISCLAIMER:** This tool is for educational and practice purposes only. 
    It does not constitute financial advice, investment research, or an offer to buy/sell securities. 
    The 'Munger Score' is a mathematical experiment and not a verified indicator of performance. 
    The author is not FCA regulated. Always do your own due diligence.
""")
st.caption("© 2026 | Built for personal educational practice.")




