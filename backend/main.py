from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import time
from dotenv import load_dotenv # Import load_dotenv
from datetime import date, timedelta, datetime # Import date, timedelta, and datetime for dummy data
import random # Import random for dummy data
import yfinance as yf  # Add yfinance import
import pandas as pd  # Add pandas import for DataFrame operations
import json
from sqlmodel import SQLModel, Field, Session, create_engine, select

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:3000", # React default port
    "localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get API key from environment variables
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

if not ALPHA_VANTAGE_API_KEY:
    print("WARNING: ALPHA_VANTAGE_API_KEY environment variable not set. Price fetching will fail.")
    # You might want to raise an exception here or handle it differently
    # raise ValueError("ALPHA_VANTAGE_API_KEY environment variable not set.")

# Database setup
DATABASE_URL = "sqlite:///./finthrust.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)

class DBPosition(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    ticker: str
    quantity: float
    purchase_price: float
    purchase_date: str

@app.on_event("startup")
def on_startup() -> None:
    SQLModel.metadata.create_all(engine)

class LoginRequest(BaseModel):
    username: str

class Position(BaseModel):
    ticker: str
    quantity: float
    purchase_price: float | None = None  # Make purchase_price optional
    purchase_date: str # Added purchase_date

class StockSearchResult(BaseModel):
    ticker: str
    name: str
    exchange: str
    type: str = "Equity"

# Remove old in-memory storage (now using SQLite database)

# --- Helper Function to Get Current Price ---
# Rate limiting mechanism
last_request_time = 0
request_interval = 15 # Minimum seconds between requests (adjust based on API limits)

def get_current_price(ticker: str):
    global last_request_time
    if not ALPHA_VANTAGE_API_KEY:
        print(f"Cannot fetch price for {ticker}. API key is missing.")
        return None

    current_time = time.time()
    time_since_last_request = current_time - last_request_time

    if time_since_last_request < request_interval:
        sleep_time = request_interval - time_since_last_request
        print(f"Rate limiting: Sleeping for {sleep_time:.2f} seconds.")
        time.sleep(sleep_time)

    # Alpha Vantage API endpoint for Global Quote
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
    last_request_time = time.time() # Update last request time

    try:
        response = requests.get(url)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        # Check if 'Global Quote' and '05. price' exist
        if "Global Quote" in data and "05. price" in data["Global Quote"]:
            price_str = data["Global Quote"]["05. price"]
            return float(price_str)
        elif "Note" in data:
            # Handle API limit exceeded or other notes
            print(f"API Note for {ticker}: {data['Note']}")
            return None
        else:
            # Handle unexpected response structure
            print(f"Unexpected response structure for {ticker}: {data}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching price for {ticker}: {e}")
        return None
    except ValueError:
        print(f"Error converting price to float for {ticker}. Received: {price_str}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred fetching price for {ticker}: {e}")
        return None

# --- Helper Function to Get Historical Price ---
def get_historical_price(ticker: str, date_str: str):
    global last_request_time
    if not ALPHA_VANTAGE_API_KEY:
        print(f"Cannot fetch historical price for {ticker}. API key is missing.")
        return None

    current_time = time.time()
    time_since_last_request = current_time - last_request_time

    if time_since_last_request < request_interval:
        sleep_time = request_interval - time_since_last_request
        print(f"Rate limiting: Sleeping for {sleep_time:.2f} seconds.")
        time.sleep(sleep_time)

    # Alpha Vantage API endpoint for Time Series Daily
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
    last_request_time = time.time() # Update last request time

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Check if 'Time Series (Daily)' exists
        if "Time Series (Daily)" in data:
            time_series = data["Time Series (Daily)"]
            
            # Find the closest date to the requested date
            closest_date = None
            min_diff = float('inf')
            
            for date_key in time_series.keys():
                date_obj = datetime.strptime(date_key, "%Y-%m-%d")
                target_date = datetime.strptime(date_str, "%Y-%m-%d")
                diff = abs((date_obj - target_date).days)
                
                if diff < min_diff:
                    min_diff = diff
                    closest_date = date_key
            
            if closest_date:
                # Get the closing price for the closest date
                price_str = time_series[closest_date]["4. close"]
                return float(price_str)
            else:
                print(f"No historical data found for {ticker} near {date_str}")
                return None
        elif "Note" in data:
            # Handle API limit exceeded or other notes
            print(f"API Note for {ticker}: {data['Note']}")
            return None
        else:
            # Handle unexpected response structure
            print(f"Unexpected response structure for {ticker}: {data}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching historical price for {ticker}: {e}")
        return None
    except ValueError as e:
        print(f"Error converting price to float for {ticker}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred fetching historical price for {ticker}: {e}")
        return None

# --- Helper Function to Get Current Price using Yahoo Finance ---
def get_current_price_yahoo(ticker: str):
    try:
        # Add exchange suffix if needed (e.g., .PA for Paris)
        exchange_suffixes = {
            "PARIS": ".PA",
            "LONDON": ".L",
            "FRANKFURT": ".DE",
            "MILAN": ".MI",
            "AMSTERDAM": ".AS",
            "BRUSSELS": ".BR",
            "MADRID": ".MC",
            "LISBON": ".LS",
            "OSLO": ".OL",
            "STOCKHOLM": ".ST",
            "HELSINKI": ".HE",
            "COPENHAGEN": ".CO",
            "VIENNA": ".VI",
            "DUBLIN": ".IR",
            "ZURICH": ".SW",
            "HONG_KONG": ".HK",
            "TOKYO": ".T",
            "SYDNEY": ".AX",
            "TORONTO": ".TO",
            "MONTREAL": ".MT",
            "VANCOUVER": ".V",
            "CALGARY": ".C",
        }
        
        # Check if the ticker already has an exchange suffix
        has_suffix = any(ticker.endswith(suffix) for suffix in exchange_suffixes.values())
        
        # If no suffix, try to determine the exchange based on the ticker format
        if not has_suffix:
            # For European stocks, you might need to add the appropriate suffix
            if ticker.isalpha() and len(ticker) <= 5:
                # This is a very simplified approach - you would need better logic
                # to determine the correct exchange
                ticker = f"{ticker}.PA"  # Default to Paris for this example
        
        # Get the stock data from Yahoo Finance
        stock = yf.Ticker(ticker)
        current_price = stock.info.get('regularMarketPrice')
        
        if current_price:
            return float(current_price)
        else:
            print(f"Could not fetch current price for {ticker} from Yahoo Finance")
            return None
            
    except Exception as e:
        print(f"Error fetching price for {ticker} from Yahoo Finance: {e}")
        return None

# --- Helper Function to Get Historical Price using Yahoo Finance ---
def get_historical_price_yahoo(ticker: str, date_str: str):
    try:
        # Parse the date and make it timezone-aware
        target_date = pd.to_datetime(date_str).tz_localize('UTC')
        
        # Get historical data from Yahoo Finance
        stock = yf.Ticker(ticker)
        
        # Get data for a wider range around the target date
        start_date = target_date - pd.Timedelta(days=10)
        end_date = target_date + pd.Timedelta(days=10)
        
        print(f"Fetching historical data for {ticker} from {start_date} to {end_date}")
        hist = stock.history(period="1mo")
        
        if hist.empty:
            print(f"No historical data found for {ticker}")
            return None
        
        print(f"Got {len(hist)} days of data for {ticker}")
        
        # Ensure the index is timezone-aware
        if hist.index.tz is None:
            hist.index = hist.index.tz_localize('UTC')
        
        # Find the closest date
        closest_date = min(hist.index, key=lambda x: abs(x - target_date))
        closest_row = hist.loc[closest_date]
        
        print(f"Found closest date {closest_date} for target date {target_date}")
        return float(closest_row['Close'])
            
    except Exception as e:
        print(f"Error fetching historical price for {ticker} from Yahoo Finance: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return None

# --- Helper Function to Get Price (tries multiple sources) ---
def get_price(ticker: str, date_str: str = None):
    """
    Get the price for a ticker, trying multiple sources.
    If date_str is provided, get the historical price for that date.
    Otherwise, get the current price.
    """
    # Try Alpha Vantage first with original ticker
    if date_str:
        price = get_historical_price(ticker, date_str)
    else:
        price = get_current_price(ticker)
    
    # If Alpha Vantage fails, try Yahoo Finance with original ticker
    if price is None:
        if date_str:
            price = get_historical_price_yahoo(ticker, date_str)
        else:
            price = get_current_price_yahoo(ticker)
    
    # If both fail and it looks like a European stock, try with .PA suffix
    if price is None and ticker.isalpha() and len(ticker) <= 5:
        ticker_with_suffix = f"{ticker}.PA"
        if date_str:
            price = get_historical_price_yahoo(ticker_with_suffix, date_str)
        else:
            price = get_current_price_yahoo(ticker_with_suffix)
    
    return price

# --- API Endpoints ---

@app.post("/login")
async def login(login_request: LoginRequest):
    username = login_request.username
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).first()
        if not user:
            user = User(username=username)
            session.add(user)
            session.commit()
            session.refresh(user)
            return {"message": f"Welcome, new user {username}!"}
    return {"message": f"Welcome back, {username}!"}

@app.post("/users/{username}/positions")
async def add_position(username: str, position: Position):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

    # If purchase_price is not provided, fetch the historical price
    if position.purchase_price is None:
        if not position.purchase_date:
            raise HTTPException(status_code=400, detail="Purchase date is required when purchase price is not provided")
        
        # Use the new get_price function that tries multiple sources
        historical_price = get_price(position.ticker, position.purchase_date)
        if historical_price is None:
            raise HTTPException(status_code=400, detail=f"Could not fetch historical price for {position.ticker} on {position.purchase_date}")
        
        position.purchase_price = historical_price

    new_pos = DBPosition(
        user_id=user.id,
        ticker=position.ticker,
        quantity=position.quantity,
        purchase_price=position.purchase_price,
        purchase_date=position.purchase_date,
    )
    session.add(new_pos)
    session.commit()
    return {"message": f"Position {position.ticker} added successfully for {username}"}

@app.get("/users/{username}/portfolio")
async def get_portfolio(username: str):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        positions = session.exec(select(DBPosition).where(DBPosition.user_id == user.id)).all()
    positions_pnl = []
    total_portfolio_value = 0
    total_purchase_cost = 0

    for pos in positions:
        # Use the new get_price function that tries multiple sources
        current_price = get_price(pos.ticker)
        if current_price is not None:
            current_value = pos.quantity * current_price
            purchase_cost = pos.quantity * pos.purchase_price
            pnl = current_value - purchase_cost
            pnl_percent = (pnl / purchase_cost) * 100 if purchase_cost != 0 else 0

            positions_pnl.append({
                "ticker": pos.ticker,
                "quantity": pos.quantity,
                "purchase_price": pos.purchase_price,
                "purchase_date": pos.purchase_date,
                "current_price": current_price,
                "current_value": round(current_value, 2),
                "pnl": round(pnl, 2),
                "pnl_percent": round(pnl_percent, 2)
            })
            total_portfolio_value += current_value
            total_purchase_cost += purchase_cost
        else:
            # Append position even if price fetch fails, include error message
            positions_pnl.append({
                "ticker": pos.ticker,
                "quantity": pos.quantity,
                "purchase_price": pos.purchase_price,
                "purchase_date": pos.purchase_date,
                "current_price": "N/A",
                "current_value": "N/A",
                "pnl": "N/A",
                "pnl_percent": "N/A",
                "error": f"Could not fetch price for {pos.ticker}"
            })
            # Note: We might want to decide how to handle total value if a price fails
            # For now, we just skip adding its value

    total_pnl = total_portfolio_value - total_purchase_cost
    total_pnl_percent = (total_pnl / total_purchase_cost) * 100 if total_purchase_cost != 0 else 0

    return {
        "positions_pnl": positions_pnl,
        "total_value": round(total_portfolio_value, 2),
        "total_pnl": round(total_pnl, 2),
        "total_pnl_percent": round(total_pnl_percent, 2)
    }

# New endpoint for portfolio history
@app.get("/users/{username}/portfolio/history")
async def get_portfolio_history(username: str):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

    # --- Dummy Data Generation ---
    # In a real application, fetch historical data and calculate portfolio value over time
    history = []
    today = date.today()
    start_value = 10000 # Initial dummy value
    for i in range(90): # Generate data for the last 90 days
        current_date = today - timedelta(days=i)
        # Simulate some random fluctuations
        fluctuation = random.uniform(-0.01, 0.015) # Small daily change percentage
        current_value = start_value * (1 + fluctuation)
        start_value = current_value # Update value for next iteration

        history.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "value": round(current_value, 2)
        })

    # Return data in reverse chronological order (oldest first)
    return history[::-1]

def search_stocks(query: str):
    try:
        matches = []
        
        # Use Yahoo Finance API for search suggestions
        search_url = f"https://query1.finance.yahoo.com/v6/finance/autocomplete?query={query}&lang=en"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(search_url, headers=headers)
        data = response.json()

        if 'ResultSet' in data and 'Result' in data['ResultSet']:
            for result in data['ResultSet']['Result']:
                symbol = result.get('symbol', '')
                if symbol:
                    try:
                        # Get additional info for each symbol
                        stock = yf.Ticker(symbol)
                        info = stock.info
                        if info:
                            matches.append(StockSearchResult(
                                ticker=symbol,
                                name=info.get('longName', info.get('shortName', result.get('name', 'Unknown'))),
                                exchange=info.get('exchange', 'Unknown'),
                                type=info.get('quoteType', 'Equity')
                            ))
                    except Exception as e:
                        print(f"Error getting details for {symbol}: {str(e)}")
                        # Still add the result with basic info
                        matches.append(StockSearchResult(
                            ticker=symbol,
                            name=result.get('name', 'Unknown'),
                            exchange='Unknown',
                            type='Equity'
                        ))

        return matches[:10]  # Limit to top 10 results
    except Exception as e:
        print(f"Error searching stocks: {str(e)}")
        return []

@app.get("/search/stocks")
async def search_stocks_endpoint(query: str = Query(..., min_length=1)):
    """
    Search for stocks by name or ticker symbol.
    Returns up to 10 matching results with ticker symbol, company name, and exchange.
    """
    results = search_stocks(query)
    if not results:
        # If no results found, try with .PA suffix for European stocks
        if query.isalpha() and len(query) <= 5:
            euro_query = f"{query.upper()}.PA"
            results = search_stocks(euro_query)
    
    return results

# --- Run the app (for local development) ---
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
