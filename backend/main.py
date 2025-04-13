from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import time
from dotenv import load_dotenv # Import load_dotenv
from datetime import date, timedelta # Import date and timedelta for dummy data
import random # Import random for dummy data

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
    purchase_date: str # Added purchase_date

# Simple in-memory storage - Replace with a database in a real app
user_data = {
    "testuser": { # Example user
        "positions": []
    }
}

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

# --- API Endpoints ---

@app.post("/login")
async def login(login_request: LoginRequest):
    username = login_request.username
    if username not in user_data:
        # Create a new user if they don't exist
        user_data[username] = {"positions": []}
        return {"message": f"Welcome, new user {username}!"}
    return {"message": f"Welcome back, {username}!"}

@app.post("/users/{username}/positions")
async def add_position(username: str, position: Position):
    if username not in user_data:
        raise HTTPException(status_code=404, detail="User not found")

    # Store position data including purchase_date
    user_data[username]["positions"].append(position.dict())
    return {"message": f"Position {position.ticker} added successfully for {username}"}

@app.get("/users/{username}/portfolio")
async def get_portfolio(username: str):
    if username not in user_data:
        raise HTTPException(status_code=404, detail="User not found")

    positions = user_data[username]["positions"]
    positions_pnl = []
    total_portfolio_value = 0
    total_purchase_cost = 0

    for pos in positions:
        current_price = get_current_price(pos['ticker'])
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
            # Append position even if price fetch fails, include error message
            positions_pnl.append({
                **pos,
                "current_price": "N/A",
                "current_value": "N/A",
                "pnl": "N/A",
                "pnl_percent": "N/A",
                "error": f"Could not fetch price for {pos['ticker']}"
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
    if username not in user_data:
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

# --- Run the app (for local development) ---
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
