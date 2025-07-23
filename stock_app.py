import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Multi-Stock Analysis", layout="wide")
st.title("📊 Multi-Stock Analysis with Weekly Averages")

# Sidebar inputs
tickers_input = st.sidebar.text_input(
    "Enter Stock Tickers (comma-separated):", "AAPL, TSLA, MSFT"
)
tickers = [t.strip().upper() for t in tickers_input.split(",")]

period = st.sidebar.selectbox("Select Period:", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y"])
interval = "1d"

@st.cache_data
def load_data(ticker, period, interval):
    df = yf.download(ticker, period=period, interval=interval)
    df['Ticker'] = ticker
    return df

all_data = []
for t in tickers:
    df = load_data(t, period, interval)
    if not df.empty:
        all_data.append(df)
    else:
        st.warning(f"No data found for {t}")

if all_data:
    data = pd.concat(all_data)
    
    # Create Plotly figure
    fig = go.Figure()
    for t in tickers:
        df_t = data[data['Ticker'] == t].copy()
        
        # Fix: use start_time for weekly period
        df_t['Week'] = df_t.index.to_period('W').start_time
        weekly_avg = df_t.groupby('Week')['Close'].mean().reset_index()

        # Add daily close line
        fig.add_trace(go.Scatter(
            x=df_t.index, y=df_t['Close'], mode='lines', name=f'{t} Daily'
        ))

        # Add weekly average line
        fig.add_trace(go.Scatter(
            x=weekly_avg['Week'], y=weekly_avg['Close'], mode='lines+markers', name=f'{t} Weekly Avg'
        ))

    fig.update_layout(
        title="Stock Prices & Weekly Averages",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_dark",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Display last 5 rows for each ticker
    st.subheader("Latest Data")
    for t in tickers:
        st.write(f"**{t}**")
        st.dataframe(data[data['Ticker'] == t].tail(5))
