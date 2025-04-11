import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';
import './App.css';

ChartJS.register(
  ArcElement, 
  Tooltip, 
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title 
);

function App() {
  const [username, setUsername] = useState('');
  const [loggedIn, setLoggedIn] = useState(false);
  const [loginMessage, setLoginMessage] = useState('');

  // State for adding positions
  const [ticker, setTicker] = useState('');
  const [quantity, setQuantity] = useState('');
  const [purchasePrice, setPurchasePrice] = useState('');
  const [positionMessage, setPositionMessage] = useState('');

  // State for portfolio data
  const [portfolio, setPortfolio] = useState({ positions_pnl: [], total_pnl: 0, total_value: 0, total_pnl_percent: 0 });
  const [isLoadingPortfolio, setIsLoadingPortfolio] = useState(false);
  const [portfolioError, setPortfolioError] = useState('');

  // --- API Calls ---
  const API_BASE_URL = 'http://localhost:8000'; // Backend URL

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginMessage('');
    try {
      const response = await fetch(`${API_BASE_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username }),
      });
      const data = await response.json();
      if (response.ok) {
        setLoggedIn(true);
        setLoginMessage(data.message);
        fetchPortfolio(); // Fetch portfolio data after login
      } else {
        setLoginMessage(data.detail || 'Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      setLoginMessage('Login failed due to network error.');
    }
  };

  const fetchPortfolio = async () => {
    if (!username) return;
    setIsLoadingPortfolio(true);
    setPortfolioError('');
    try {
      const response = await fetch(`${API_BASE_URL}/${username}/portfolio`);
      if (response.ok) {
        const data = await response.json();
        setPortfolio(data);
      } else {
        const errorData = await response.json();
        console.error('Failed to fetch portfolio:', errorData.detail);
        setPortfolioError(`Failed to load portfolio: ${errorData.detail || response.statusText}`);
      }
    } catch (error) {
      console.error('Error fetching portfolio:', error);
      setPortfolioError('Network error while fetching portfolio.');
    }
    setIsLoadingPortfolio(false);
  };

  const handleAddPosition = async (e) => {
    e.preventDefault();
    setPositionMessage('');
    if (!username) {
      setPositionMessage('Please login first');
      return;
    }
    try {
      const positionData = {
        ticker: ticker.toUpperCase(), // Standardize ticker
        quantity: parseFloat(quantity),
        purchase_price: parseFloat(purchasePrice),
      };
      const response = await fetch(`${API_BASE_URL}/${username}/positions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(positionData),
      });
      const data = await response.json();
      if (response.ok) {
        setPositionMessage(data.message);
        // Clear the form
        setTicker('');
        setQuantity('');
        setPurchasePrice('');
        // Refresh portfolio data to show the new position and updated PnL
        fetchPortfolio();
      } else {
        setPositionMessage(data.detail || 'Failed to add position');
      }
    } catch (error) {
      console.error('Error adding position:', error);
      setPositionMessage('Failed to add position due to network error.');
    }
  };

  // Fetch portfolio data periodically or on demand (e.g., refresh button)
  // For now, fetch on login and after adding a position.

  // --- Chart Data Preparation ---
  const allocationChartData = {
    labels: portfolio.positions_pnl
              .filter(p => typeof p.current_value === 'number') // Only include valid numbers
              .map(p => p.ticker),
    datasets: [
      {
        label: 'Portfolio Allocation by Value',
        data: portfolio.positions_pnl
                .filter(p => typeof p.current_value === 'number')
                .map(p => p.current_value),
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)', // Add more colors if needed
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(153, 102, 255, 0.6)',
          'rgba(255, 159, 64, 0.6)',
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
          'rgba(255, 159, 64, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  const pnlChartData = {
    labels: portfolio.positions_pnl
              .filter(p => typeof p.pnl === 'number') // Only include valid PnL numbers
              .map(p => p.ticker),
    datasets: [
      {
        label: 'Profit/Loss (PnL) per Position',
        data: portfolio.positions_pnl
                .filter(p => typeof p.pnl === 'number')
                .map(p => p.pnl),
        backgroundColor: portfolio.positions_pnl
                         .filter(p => typeof p.pnl === 'number')
                         .map(p => p.pnl >= 0 ? 'rgba(75, 192, 192, 0.6)' : 'rgba(255, 99, 132, 0.6)'), // Green for profit, Red for loss
        borderColor: portfolio.positions_pnl
                       .filter(p => typeof p.pnl === 'number')
                       .map(p => p.pnl >= 0 ? 'rgba(75, 192, 192, 1)' : 'rgba(255, 99, 132, 1)'),
        borderWidth: 1,
      },
    ],
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Portfolio Tracker</h1>
        {!loggedIn ? (
          <form onSubmit={handleLogin}>
            <label>
              Username:
              <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} required />
            </label>
            <button type="submit">Login</button>
            {loginMessage && <p style={{ color: 'red', fontSize: 'small' }}>{loginMessage}</p>}
          </form>
        ) : (
          <div>
            <h2>Welcome, {username}!</h2>

            {/* Add Position Form */}
            <div className="form-container">
              <h3>Add New Position</h3>
              <form onSubmit={handleAddPosition}>
                <div>
                  <label>Ticker: <input type="text" value={ticker} onChange={(e) => setTicker(e.target.value)} required /></label>
                </div>
                <div>
                  <label>Quantity: <input type="number" value={quantity} onChange={(e) => setQuantity(e.target.value)} required /></label>
                </div>
                <div>
                  <label>Purchase Price: <input type="number" step="0.01" value={purchasePrice} onChange={(e) => setPurchasePrice(e.target.value)} required /></label>
                </div>
                <button type="submit">Add Position</button>
                {positionMessage && <p style={{ color: 'lightblue', fontSize: 'small' }}>{positionMessage}</p>}
              </form>
            </div>

            {/* Portfolio Display */}
            <div className="portfolio-container">
              <h3>Your Portfolio</h3>
              {isLoadingPortfolio && <p>Loading portfolio data...</p>}
              {portfolioError && <p style={{ color: 'red' }}>{portfolioError}</p>}
              {!isLoadingPortfolio && !portfolioError && (
                <>
                  <div className="portfolio-summary">
                     <p>Total Value: ${portfolio.total_value?.toFixed(2)}</p>
                     <p>Total PnL: <span style={{ color: portfolio.total_pnl >= 0 ? 'lightgreen' : '#FFCCCB' }}>${portfolio.total_pnl?.toFixed(2)} ({portfolio.total_pnl_percent?.toFixed(2)}%)</span></p>
                  </div>

                  {portfolio.positions_pnl.length > 0 ? (
                    <>
                    <table className="positions-table">
                      <thead>
                        <tr>
                          <th>Ticker</th>
                          <th>Quantity</th>
                          <th>Purchase Price</th>
                          <th>Current Price</th>
                          <th>Current Value</th>
                          <th>PnL</th>
                          <th>PnL %</th>
                        </tr>
                      </thead>
                      <tbody>
                        {portfolio.positions_pnl.map((pos, index) => (
                          <tr key={index}>
                            <td>{pos.ticker}</td>
                            <td>{pos.quantity}</td>
                            <td>${pos.purchase_price?.toFixed(2)}</td>
                            <td>{typeof pos.current_price === 'number' ? `$${pos.current_price.toFixed(2)}` : pos.current_price}</td>
                            <td>{typeof pos.current_value === 'number' ? `$${pos.current_value.toFixed(2)}` : pos.current_value}</td>
                            <td style={{ color: typeof pos.pnl === 'number' ? (pos.pnl >= 0 ? 'lightgreen' : '#FFCCCB') : 'white' }}>
                              {typeof pos.pnl === 'number' ? `$${pos.pnl.toFixed(2)}` : pos.pnl}
                            </td>
                            <td style={{ color: typeof pos.pnl_percent === 'number' ? (pos.pnl_percent >= 0 ? 'lightgreen' : '#FFCCCB') : 'white' }}>
                              {typeof pos.pnl_percent === 'number' ? `${pos.pnl_percent.toFixed(2)}%` : pos.pnl_percent}
                            </td>
                            {pos.error && <td colSpan="7" style={{color: 'orange', fontSize: 'smaller'}}>{pos.error}</td>}
                          </tr>
                        ))}
                      </tbody>
                    </table>

                    {/* Charts */}
                    <div className="charts-container">
                       {portfolio.positions_pnl.some(p => typeof p.current_value === 'number') && (
                         <div className="chart">
                           <h4>Allocation by Value</h4>
                           <Pie data={allocationChartData} />
                         </div>
                       )}
                       {portfolio.positions_pnl.some(p => typeof p.pnl === 'number') && (
                         <div className="chart">
                           <h4>PnL per Position</h4>
                            <Bar data={pnlChartData} options={{ plugins: { legend: { display: false } } }} />
                         </div>
                       )}
                    </div>
                  </>
                  ) : (
                    <p>Add positions to see your portfolio details.</p>
                  )}
                </>
              )}
            </div>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
