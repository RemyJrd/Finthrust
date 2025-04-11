from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import time
from dotenv import load_dotenv # Import load_dotenv

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

class LoginRequest(BaseModel):
    username: str

class Position(BaseModel):
    ticker: str
    quantity: float
    purchase_price: float

# Simple in-memory storage - Replace with a database in a real app
user_data = {
    "testuser": { # Example user
        "positions": []
    }
}

# --- Helper Function to Get Current Price ---
def get_current_price(ticker: str):
    if not ALPHA_VANTAGE_API_KEY:
        print(f"Cannot fetch price for {ticker}. API key is missing.")
        return None

    # Alpha Vantage API endpoint for Global Quote
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}'
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise an exception for bad status codes
        data = response.json()

        # Check if 'Global Quote' and '05. price' exist
        quote = data.get('Global Quote')
        if quote and '05. price' in quote:
            return float(quote['05. price'])
        elif 'Note' in data:
            # Handle API rate limit note
            print(f"Alpha Vantage API Note for {ticker}: {data['Note']}")
            # Consider waiting or returning a specific indicator for rate limit
            return None # Indicate rate limit or other issue
        elif 'Error Message' in data:
             print(f"Alpha Vantage API Error for {ticker}: {data['Error Message']}")
             return None # Indicate API error
        else:
            print(f"Could not retrieve price for {ticker}. Response: {data}")
            return None # Price not found or other API error
    except requests.exceptions.RequestException as e:
        print(f"Error fetching price for {ticker}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while fetching price for {ticker}: {e}")
        return None

# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Welcome to the Portfolio Tracker API"}

@app.post("/login")
def login(login_request: LoginRequest):
    username = login_request.username
    if username not in user_data:
        user_data[username] = {"positions": []}
        print(f"New user created: {username}")
    else:
        print(f"User logged in: {username}")
    return {"message": f"Login successful for {username}"}

@app.post("/{username}/positions")
def add_position(username: str, position: Position):
    if username not in user_data:
        raise HTTPException(status_code=404, detail="User not found")

    user_data[username]["positions"].append(position.dict())
    print(f"Added position for {username}: {position.dict()}")
    return {"message": "Position added successfully", "position": position.dict()}

@app.get("/{username}/positions")
def get_positions(username: str):
    if username not in user_data:
        raise HTTPException(status_code=404, detail="User not found")
    return {"positions": user_data[username].get("positions", [])}

@app.get("/{username}/portfolio")
def get_portfolio_pnl(username: str):
    if username not in user_data:
        raise HTTPException(status_code=404, detail="User not found")

    positions = user_data[username].get("positions", [])
    if not positions:
        return {"positions_pnl": [], "total_pnl": 0, "total_value": 0, "message": "No positions to calculate PnL."}

    positions_pnl = []
    total_portfolio_value = 0
    total_purchase_cost = 0
    api_call_counter = 0
    max_calls_per_minute = 4 # Adjusted for safety margin with free tier (5/min)
    last_api_call_time = 0

    for pos in positions:
        # Rate limiting
        current_time = time.time()
        if api_call_counter >= max_calls_per_minute:
            time_since_last_batch = current_time - last_api_call_time
            if time_since_last_batch < 65: # Wait if less than 65s passed since last batch start
                wait_time = 65 - time_since_last_batch
                print(f"Rate limit approaching. Pausing for {wait_time:.1f} seconds...")
                time.sleep(wait_time)
            api_call_counter = 0 # Reset counter after waiting

        if api_call_counter == 0:
             last_api_call_time = time.time() # Record time when a new batch of calls starts

        current_price = get_current_price(pos['ticker'])
        api_call_counter += 1

        if current_price is not None:
            current_value = pos['quantity'] * current_price
            purchase_cost = pos['quantity'] * pos['purchase_price']
            pnl = current_value - purchase_cost
            pnl_percent = (pnl / purchase_cost) * 100 if purchase_cost != 0 else 0

            positions_pnl.append({
                **pos,
                "current_price": current_price,
                "current_value": round(current_value, 2),
                "pnl": round(pnl, 2),
                "pnl_percent": round(pnl_percent, 2)
            })
            total_portfolio_value += current_value
            total_purchase_cost += purchase_cost
        else:
            positions_pnl.append({
                **pos,
                "current_price": "N/A",
                "current_value": "N/A",
                "pnl": "N/A",
                "pnl_percent": "N/A",
                "error": f"Could not fetch price for {pos['ticker']}"
            })

    total_pnl = total_portfolio_value - total_purchase_cost
    total_pnl_percent = (total_pnl / total_purchase_cost) * 100 if total_purchase_cost != 0 else 0

    return {
        "positions_pnl": positions_pnl,
        "total_pnl": round(total_pnl, 2),
        "total_value": round(total_portfolio_value, 2),
        "total_pnl_percent": round(total_pnl_percent, 2)
    }

# To run the app (from the backend directory):
# Ensure .env file exists
# pip install -r requirements.txt
# uvicorn main:app --reload --port 8000
