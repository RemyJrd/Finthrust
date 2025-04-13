import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
} from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';
import './App.css';
import PortfolioManagement from './PortfolioManagement';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import PortfolioTracking from './PortfolioTracking';
import Advisor from './Advisor';
import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';

ChartJS.register(
  ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title
);

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#64B5F6', // A more vibrant blue
    },
    secondary: {
      main: '#E57373', // A more vibrant red
    },
    background: {
      default: '#121212', // Dark background
      paper: '#1E1E1E', // Slightly lighter for paper elements
    },
    text: {
      primary: '#E0F7FA', // Light text color
    },
  },
  typography: {
    fontFamily: 'Roboto, sans-serif',
    h1: {
      fontWeight: 700,
      fontSize: '2.5rem',
      letterSpacing: '-0.05rem',
    },
    h2: {
      fontWeight: 600,
      fontSize: '2rem',
      letterSpacing: '-0.03rem',
    },
  },
  shape: {
    borderRadius: 8, // Slightly rounded corners
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 500,
          boxShadow: '0 2px 4px rgba(0,0,0,0.2)', // Subtle shadow
          transition: 'transform 0.2s ease-in-out',
          '&:hover': {
            transform: 'scale(1.05)', // Slight scale effect on hover
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
            '&:hover fieldset': {
              borderColor: '#64B5F6', // Highlight on hover
            },
            '&.Mui-focused fieldset': {
              borderColor: '#64B5F6',
            },
          },
        },
      },
    },
    MuiTableContainer: {
      styleOverrides: {
        root: {
          boxShadow: '0 4px 8px rgba(0,0,0,0.1)', // Shadow for the table
          borderRadius: 8,
        },
      },
    },
  },
  typography: {
    fontFamily: 'Roboto, sans-serif',
  },
);

function App() {
  const [username, setUsername] = useState('');
  const [loggedIn, setLoggedIn] = useState(false);
  const [loginMessage, setLoginMessage] = useState('');
  const [portfolio, setPortfolio] = useState({ positions_pnl: [], total_pnl: 0, total_value: 0, total_pnl_percent: 0 });
  const [Advisor, setAdvisor] = useState(false);

  const [isLoadingPortfolio, setIsLoadingPortfolio] = useState(false);
  const [portfolioError, setPortfolioError] = useState('');

  const API_BASE_URL = 'http://localhost:8000';

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


  const allocationChartData = {
    labels: portfolio.positions_pnl
              .filter(p => typeof p.current_value === 'number')
              .map(p => p.ticker),
    datasets: [

      {
        label: 'Portfolio Allocation by Value',
        data: portfolio.positions_pnl
                .filter(p => typeof p.current_value === 'number')
                .map(p => p.current_value),
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)', // Add more colors if needed
          '#A7C7E7', // Bleu pastel
          '#FFB6C1', // Rose pastel
          '#B0E2E2', // Vert d'eau pastel
          '#CDB4DB', // Lavande pastel
          '#F2D2BD', // Beige pastel
          '#B5EAD7', // Vert clair pastel
        ],
        borderColor: [
          '#121212',
          '#121212',
          '#121212',
          '#121212',
          '#121212',
          '#121212',
        ], // Couleur de fond sombre pour les bordures

        borderWidth: 1,
      },
    ],
  };

  const allocationChartOptions = {
    plugins: {
      legend: {
        display: false, // Hide legend
      },
    },
  };

  const pnlChartData = {
    labels: portfolio.positions_pnl
              .filter(p => typeof p.pnl === 'number')
              .map(p => p.ticker),
    datasets: [
      {
        label: 'Profit/Loss (PnL) per Position',
        data: portfolio.positions_pnl
                .filter(p => typeof p.pnl === 'number')
                .map(p => p.pnl),
        backgroundColor: portfolio.positions_pnl.filter(p => typeof p.pnl === 'number').map(p => (p.pnl >= 0 ? '#B5EAD7' : '#FFB6C1')),
        borderColor:'#121212',
        borderWidth: 1
      },
    ],
    options: {}
  };

  return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <BrowserRouter>
                <div className="App">
                    <header className="App-header">
                        <h1 >Portfolio Tracker</h1>
                        {!loggedIn ? (
                            <form onSubmit={handleLogin}>
                              <label>
                                Username:<br />
                                <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} required />
                              </label>
                              <button type="submit">Login</button>
                              {loginMessage && (
                                <p className={`message ${loginMessage.includes('failed') ? 'error' : 'info'}`}>{loginMessage}</p>
                              )}
                            </form>
                        ) : (
                            <div>
                                <h2 style={{ color: '#A7C7E7' }}>Welcome, {username}!</h2>

                                <nav>
                                    <ul className="nav-links">
                                        <li>
                                            <Link to="/portfolio">Gestion de patrimoine</Link>
                                        </li>
                                        <li>
                                            <Link to="/tracking">Suivi</Link>
                                        </li>
                                        <li>
                                            <Link to="/advisor">Conseiller</Link>
                                        </li>
                                    </ul>
                                </nav>
                                <Routes>
                                    <Route path="/portfolio" element={<PortfolioManagement portfolio={portfolio} username={username} fetchPortfolio={fetchPortfolio} API_BASE_URL={API_BASE_URL} />} />
                                    <Route path="/tracking" element={<PortfolioTracking username={username} API_BASE_URL={API_BASE_URL} />} />
                                    <Route path="/advisor" element={<Advisor />} />
                                </Routes>
                            </div>
                        )}
                    </header>
                </div>
            </BrowserRouter>
        </ThemeProvider>
  );
}

export default App;
