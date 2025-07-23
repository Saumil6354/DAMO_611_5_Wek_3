import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.title("📈 Stock Price Analysis with Weekly Average")

# Sidebar for user inputs
ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., AAPL, TSLA, MSFT):", "AAPL")
period = st.sidebar.selectbox("Select Period:", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y"])
interval = "1d"  # daily data

# Fetch data
@st.cache_data
def load_data(ticker, period, interval):
    data = yf.download(ticker, period=period, interval=interval)
    return data

data = load_data(ticker, period, interval)

# Check if data exists
if data.empty:
    st.error(f"No data found for ticker {ticker}. Please try another one.")
else:
    st.success(f"Showing data for {ticker}")

    # Calculate weekly average
    data['Week'] = data.index.to_period('W')
    weekly_avg = data.groupby('Week')['Close'].mean().reset_index()
    weekly_avg['Week'] = weekly_avg['Week'].astype(str)

    # Plot with Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Daily Close'))
    fig.add_trace(go.Scatter(x=weekly_avg['Week'], y=weekly_avg['Close'], mode='lines+markers', name='Weekly Avg'))

    fig.update_layout(
        title=f"{ticker} Stock Price with Weekly Average",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_dark"
    )

    # Display plot
    st.plotly_chart(fig, use_container_width=True)

    # Show last few rows
    st.subheader("Latest Data")
    st.write(data.tail(10))
