# Finthrust - Portfolio Management Application

Finthrust is a modern web application for managing and tracking your stock portfolio. It provides real-time stock data, historical price tracking, and portfolio performance visualization.

## Features

- 🔍 Real-time stock search with company information
- 📈 Live stock price tracking
- 📊 Portfolio performance visualization
- 📅 Historical price data support
- 📱 Responsive modern UI
- 📈 Interactive charts and analytics
- 🔄 Automatic price updates
- 🌍 Support for multiple stock exchanges

## Tech Stack

### Backend
- FastAPI (Python)
- yfinance for stock data
- pandas for data processing
- Alpha Vantage API (alternative data source)

### Frontend
- React.js
- Material-UI
- Recharts for data visualization
- Axios for API communication

## Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn
- (Optional) Alpha Vantage API key for additional data source

## Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd Finthrust/backend
```

2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the backend directory with:
```
ALPHA_VANTAGE_API_KEY=your_api_key_here  # Optional
```
5. The backend uses an SQLite database stored in `finthrust.db` in the backend
   directory. The file is created automatically on first run.

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd Finthrust/frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Run frontend tests:
```bash
npm test
```

## Running the Application

### Start the Backend Server

```bash
cd backend
uvicorn main:app --reload
```
The backend will be available at `http://localhost:8000`

### Start the Frontend Development Server

```bash
cd frontend
npm start
# or
yarn start
```
The frontend will be available at `http://localhost:3000`

## Usage

1. Open your browser and navigate to `http://localhost:3000`
2. Enter your username to access your portfolio
3. Use the search function to find stocks
4. Add positions to your portfolio with:
   - Stock symbol
   - Quantity
   - Purchase price (optional)
   - Purchase date
5. View your portfolio performance and analytics

## API Documentation

Once the backend is running, you can access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache-2.0 license - see the LICENSE file for details.
