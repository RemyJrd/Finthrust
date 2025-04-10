import streamlit as st
import pandas as pd
import datetime
import yfinance as yf

st.set_page_config(page_title="Portfolio Tracker", layout="wide")

st.title("Portfolio Tracker")

# Check login status (if implemented in app.py)
# if not st.session_state.get("logged_in", False):
#     st.warning("Please log in first.")
#     st.stop()

# --- Function to add a transaction ---
def add_transaction(ticker, quantity, transaction_type, transaction_date, price):
    if not ticker or quantity <= 0 or not transaction_date or price <= 0:
        st.error("Please fill in all transaction details with valid values.")
        return
    st.session_state.portfolio_transactions.append({
        "ticker": ticker.upper(),
        "quantity": quantity,
        "type": transaction_type,
        "date": transaction_date,
        "price": price # Price per share at the time of transaction
    })
    st.success(f"{transaction_type} {quantity} shares of {ticker.upper()} added.")

# --- Transaction Input Form ---
st.header("Add New Transaction")
with st.form("transaction_form", clear_on_submit=True):
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        ticker_input = st.text_input("Stock Ticker", placeholder="e.g., AAPL")
    with col2:
        quantity_input = st.number_input("Quantity", min_value=0.01, step=0.01, format="%.2f")
    with col3:
        type_input = st.selectbox("Type", ["Buy", "Sell"])
    with col4:
        date_input = st.date_input("Transaction Date", datetime.date.today())
    with col5:
        price_input = st.number_input("Price per Share", min_value=0.01, step=0.01, format="%.2f")

    submitted = st.form_submit_button("Add Transaction")
    if submitted:
        add_transaction(ticker_input, quantity_input, type_input, date_input, price_input)

# --- Display Current Portfolio --- 
st.header("Current Portfolio Summary")

if not st.session_state.portfolio_transactions:
    st.info("Your portfolio is empty. Add transactions above.")
else:
    transactions_df = pd.DataFrame(st.session_state.portfolio_transactions)
    transactions_df['date'] = pd.to_datetime(transactions_df['date'])

    # Calculate current holdings
    holdings = {}
    for index, row in transactions_df.iterrows():
        ticker = row['ticker']
        quantity = row['quantity']
        ttype = row['type']
        price = row['price']

        if ttype == 'Buy':
            if ticker not in holdings:
                holdings[ticker] = {'quantity': 0, 'total_cost': 0.0}
            holdings[ticker]['quantity'] += quantity
            holdings[ticker]['total_cost'] += quantity * price
        elif ttype == 'Sell':
            if ticker in holdings:
                # Adjust cost basis proportionally (simple FIFO-like)
                # More complex logic needed for tax lots (LIFO, HIFO, specific ID)
                original_quantity = holdings[ticker]['quantity'] + quantity # Estimate quantity before this sale
                if original_quantity > 0:
                    cost_per_share_before_sale = holdings[ticker]['total_cost'] / original_quantity
                    cost_reduction = quantity * cost_per_share_before_sale
                    holdings[ticker]['total_cost'] -= cost_reduction
                holdings[ticker]['quantity'] -= quantity
                # Ensure cost doesn't go negative due to floating point issues or selling more than bought
                holdings[ticker]['total_cost'] = max(holdings[ticker]['total_cost'], 0)
            else:
                st.warning(f"Attempted to sell {ticker} which is not in the portfolio or already sold.")

    # Filter out empty holdings (after selling everything)
    holdings = {ticker: data for ticker, data in holdings.items() if data['quantity'] > 0.001} # Use tolerance

    if not holdings:
        st.info("Your portfolio is currently empty (all positions might have been sold).")
        st.subheader("All Transactions")
        st.dataframe(transactions_df.sort_values(by='date', ascending=False), use_container_width=True)
    else:
        portfolio_summary = []
        tickers = list(holdings.keys())
        current_prices = {}
        fetch_errors = []

        # Fetch current prices
        if tickers:
            try:
                # yfinance can take a list of tickers
                ticker_data = yf.Tickers(tickers)
                for ticker in tickers:
                    hist = ticker_data.tickers[ticker].history(period="2d") # Get last couple days
                    if not hist.empty:
                        current_prices[ticker] = hist['Close'].iloc[-1]
                    else:
                         current_prices[ticker] = 0 # Handle cases where price isn't found
                         fetch_errors.append(ticker)
            except Exception as e:
                st.error(f"Error fetching current prices: {e}")

        if fetch_errors:
            st.warning(f"Could not fetch current price for: {', '.join(fetch_errors)}. Market value calculation might be incomplete.")

        # Prepare summary data
        total_portfolio_value = 0.0
        total_portfolio_cost = 0.0
        for ticker, data in holdings.items():
            current_price = current_prices.get(ticker, 0)
            market_value = data['quantity'] * current_price
            total_cost = data['total_cost']
            gain_loss = market_value - total_cost
            avg_cost_per_share = total_cost / data['quantity'] if data['quantity'] else 0

            portfolio_summary.append({
                "Ticker": ticker,
                "Quantity": data['quantity'],
                "Avg Cost/Share": avg_cost_per_share,
                "Total Cost": total_cost,
                "Current Price": current_price,
                "Market Value": market_value,
                "Gain/Loss ($)": gain_loss
            })
            total_portfolio_value += market_value
            total_portfolio_cost += total_cost

        summary_df = pd.DataFrame(portfolio_summary)

        # Display summary metrics
        st.subheader("Portfolio Overview")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Market Value", f"${total_portfolio_value:,.2f}")
        col2.metric("Total Cost Basis", f"${total_portfolio_cost:,.2f}")
        total_gain_loss = total_portfolio_value - total_portfolio_cost
        gain_loss_percent = (total_gain_loss / total_portfolio_cost * 100) if total_portfolio_cost else 0
        col3.metric("Total Gain/Loss", f"${total_gain_loss:,.2f}", f"{gain_loss_percent:.2f}%" if total_portfolio_cost else "N/A")

        st.dataframe(summary_df.style.format({
            "Avg Cost/Share": "${:,.2f}",
            "Total Cost": "${:,.2f}",
            "Current Price": "${:,.2f}",
            "Market Value": "${:,.2f}",
            "Gain/Loss ($)": "${:,.2f}",
            "Quantity": "{:,.2f}"
        }), use_container_width=True)

        # --- Placeholder for Portfolio Graph ---
        st.subheader("Portfolio Performance (Placeholder)")
        st.write("Graph showing portfolio value over time will be implemented here.")
        # TODO: Implement historical portfolio value calculation and plotting

        # --- Display Raw Transactions ---
        with st.expander("View All Transactions"):
            st.dataframe(transactions_df.sort_values(by='date', ascending=False), use_container_width=True)

