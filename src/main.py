import streamlit as st
import pandas as pd
import numpy as np
import backtrader as bt
import matplotlib.pyplot as plt

class MACrossover(bt.Strategy):
    params = (
        ('short_period', 20),
        ('long_period', 50),
    )

    def __init__(self):
        self.short_ma = bt.indicators.SMA(self.data.close, period=self.params.short_period)
        self.long_ma = bt.indicators.SMA(self.data.close, period=self.params.long_period)
        self.crossover = bt.indicators.CrossOver(self.short_ma, self.long_ma)

    def next(self):
        if self.crossover > 0:
            # Simple buy logic: buy 10 shares
            self.buy(size=10)
        elif self.crossover < 0:
            # Simple sell logic: sell all positions
            self.close()

def run_backtest(data, short_period=20, long_period=50):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MACrossover, short_period=short_period, long_period=long_period)

    # Ensure data has the correct format for PandasData
    if not isinstance(data.index, pd.DatetimeIndex):
        try:
            # Attempt to convert the index to datetime, assuming it's the first column if not the index
            if data.index.name is None or not pd.api.types.is_datetime64_any_dtype(data.index):
                 # Find the first column that might be a date
                potential_date_cols = [col for col in data.columns if 'date' in col.lower() or 'time' in col.lower()]
                if potential_date_cols:
                    date_col = potential_date_cols[0]
                    st.write(f"Attempting to parse dates from column: {date_col}")
                    data[date_col] = pd.to_datetime(data[date_col])
                    data.set_index(date_col, inplace=True)
                else:
                     # Fallback: try parsing the first column
                     st.write("No obvious date column found, attempting to parse the first column.")
                     first_col = data.columns[0]
                     data[first_col] = pd.to_datetime(data[first_col])
                     data.set_index(first_col, inplace=True)

            else: # The index exists but isn't datetime
                data.index = pd.to_datetime(data.index)

        except Exception as e:
             st.error(f"Failed to automatically convert index/column to DatetimeIndex. Please ensure your CSV has a parsable date column and it's set as the index. Error: {e}")
             return None, None, None, None, None # Indicate failure


    # Check for required columns (case-insensitive)
    required_columns = ['open', 'high', 'low', 'close', 'volume']
    data.columns = [col.lower() for col in data.columns] # Standardize column names to lower case first
    if not all(col in data.columns for col in required_columns):
        st.error(f"Input data must contain columns (case-insensitive): {', '.join(required_columns)}. Found: {', '.join(data.columns)}")
        return None, None, None, None, None # Indicate failure


    data_feed = bt.feeds.PandasData(dataname=data)

    cerebro.adddata(data_feed)
    cerebro.broker.setcash(100000.0)
    # Add broker observer
    cerebro.addobserver(bt.observers.Broker)
    # Add analyzers
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

    results = cerebro.run()
    strategy = results[0]

    final_portfolio_value = cerebro.broker.getvalue()
    sharpe_ratio = strategy.analyzers.sharpe_ratio.get_analysis().get('sharperatio', None)
    max_drawdown = strategy.analyzers.drawdown.get_analysis().max.drawdown
    total_return = strategy.analyzers.returns.get_analysis().rtot

    return strategy, final_portfolio_value, sharpe_ratio, max_drawdown, total_return

def plot_portfolio_value(strategy):
    """Generates a plot of the portfolio value over time."""
    fig = plt.figure(figsize=(10, 5))
    # Access portfolio values from the Broker observer
    try:
        portfolio_values = [x.value[0] for x in strategy.observers.broker]
        # Get the corresponding dates from the data feed
        dates = [bt.num2date(x.datetime[0]) for x in strategy.observers.broker]
        if not dates:
            st.warning("No trades were executed, cannot plot portfolio value.")
            plt.close(fig) # Close the empty figure
            return None

        plt.plot(dates, portfolio_values, label='Portfolio Value')
        plt.xlabel('Date')
        plt.ylabel('Portfolio Value ($)')
        plt.title('Portfolio Value Over Time')
        plt.legend()
        plt.grid(True)
        # Improve date formatting on x-axis if possible
        try:
            fig.autofmt_xdate()
        except Exception:
            pass # Ignore if formatting fails
        return fig
    except Exception as e:
        st.error(f"Error generating plot: {e}")
        plt.close(fig) # Close the figure if error occurs
        return None


# --- Streamlit App ---
st.title("Backtrader Moving Average Crossover Strategy")

st.sidebar.header("Strategy Parameters")
short_period_input = st.sidebar.number_input("Short MA Period", 1, 200, 20)
long_period_input = st.sidebar.number_input("Long MA Period", 1, 200, 50)

st.sidebar.header("Data Input")
uploaded_file = st.sidebar.file_uploader("Upload CSV Data", type="csv")

run_button = st.sidebar.button("Run Backtest")

# Placeholders for results and plot
results_container = st.container()
plot_container = st.container()


if run_button and uploaded_file is not None:
    try:
        data = pd.read_csv(uploaded_file)
        st.write("Uploaded Data Preview:")
        st.dataframe(data.head())

        # Run the backtest
        strategy, final_value, sharpe, max_dd, total_ret = run_backtest(
            data.copy(), # Pass a copy to avoid modifying original df
            short_period=short_period_input,
            long_period=long_period_input
        )

        if strategy is not None: # Check if backtest ran successfully
            with results_container:
                st.subheader("Backtest Results")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Final Portfolio Value", f"${final_value:,.2f}")
                col2.metric("Total Return", f"{total_ret*100:.2f}%" if total_ret is not None else "N/A")
                col3.metric("Sharpe Ratio", f"{sharpe:.2f}" if sharpe is not None else "N/A")
                col4.metric("Max Drawdown", f"{max_dd:.2f}%" if max_dd is not None else "N/A")


            with plot_container:
                st.subheader("Portfolio Value Over Time")
                fig = plot_portfolio_value(strategy)
                if fig:
                    st.pyplot(fig)
        else:
             results_container.error("Backtest failed. Check errors above or in data format.")


    except pd.errors.EmptyDataError:
        st.error("The uploaded CSV file is empty.")
    except Exception as e:
        st.error(f"An error occurred during data processing or backtesting: {e}")

elif run_button and uploaded_file is None:
    st.sidebar.warning("Please upload a CSV file.")


# (Optional) Add instructions or default message when no data is loaded
if uploaded_file is None:
     results_container.info("Upload a CSV file and click 'Run Backtest' to see the results.")

# Remove or comment out the old __main__ block if it exists
# if __name__ == '__main__':
#     # ... old example code ...
#     pass

