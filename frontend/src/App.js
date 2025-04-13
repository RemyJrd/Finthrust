import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, useNavigate } from 'react-router-dom';
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
import { 
  CssBaseline, 
  AppBar, 
  Toolbar, 
  Typography, 
  Button, 
  Container, 
  Box, 
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
  useMediaQuery,
  useTheme as useMuiTheme
} from '@mui/material';
import PortfolioTracking from './PortfolioTracking';
import Advisor from './Advisor';
import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import MenuIcon from '@mui/icons-material/Menu';
import CloseIcon from '@mui/icons-material/Close';

ChartJS.register(
  ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title
);

// Create a dark theme
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#A7C7E7', // Pastel blue
    },
    secondary: {
      main: '#FFB6C1', // Pastel pink
    },
    background: {
      default: '#121212',
      paper: '#1E1E1E',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
      fontSize: '2.5rem',
    },
    h2: {
      fontWeight: 500,
      fontSize: '2rem',
    },
    h3: {
      fontWeight: 500,
      fontSize: '1.5rem',
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
  },
});

function App() {
  const [username, setUsername] = useState('');
  const [loggedIn, setLoggedIn] = useState(false);
  const [loginMessage, setLoginMessage] = useState('');
  const [portfolio, setPortfolio] = useState({ positions_pnl: [], total_pnl: 0, total_value: 0, total_pnl_percent: 0 });
  const [Advisor, setAdvisor] = useState(false);
  const [isLoadingPortfolio, setIsLoadingPortfolio] = useState(false);
  const [portfolioError, setPortfolioError] = useState('');
  const [loginOpen, setLoginOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const muiTheme = useMuiTheme();
  const isMobile = useMediaQuery(muiTheme.breakpoints.down('md'));

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
        setLoginOpen(false);
        fetchPortfolio(); // Fetch portfolio data after login
      } else {
        setLoginMessage(data.detail || 'Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      setLoginMessage('Login failed due to network error.');
    }
  };

  const handleLogout = () => {
    setLoggedIn(false);
    setUsername('');
    setPortfolio({ positions_pnl: [], total_pnl: 0, total_value: 0, total_pnl_percent: 0 });
  };

  const fetchPortfolio = async () => {
    if (!username) return;
    setIsLoadingPortfolio(true);
    setPortfolioError('');
    try {
      const response = await fetch(`${API_BASE_URL}/users/${username}/portfolio`);
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
          'rgba(255, 99, 132, 0.6)',
          '#A7C7E7',
          '#FFB6C1',
          '#B0E2E2',
          '#CDB4DB',
          '#F2D2BD',
          '#B5EAD7',
        ],
        borderColor: [
          '#121212',
          '#121212',
          '#121212',
          '#121212',
          '#121212',
          '#121212',
        ],
        borderWidth: 1,
      },
    ],
  };

  const allocationChartOptions = {
    plugins: {
      legend: {
        display: false,
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
          <AppBar position="static" elevation={0}>
            <Toolbar>
              <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
                Portfolio Tracker
              </Typography>
              
              {loggedIn ? (
                <>
                  {isMobile ? (
                    <IconButton
                      color="inherit"
                      onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                      edge="end"
                    >
                      {mobileMenuOpen ? <CloseIcon /> : <MenuIcon />}
                    </IconButton>
                  ) : (
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Button color="inherit" component={Link} to="/portfolio">
                        Portfolio
                      </Button>
                      <Button color="inherit" component={Link} to="/tracking">
                        Tracking
                      </Button>
                      <Button color="inherit" component={Link} to="/advisor">
                        Advisor
                      </Button>
                      <Box sx={{ display: 'flex', alignItems: 'center', ml: 2 }}>
                        <AccountCircleIcon sx={{ mr: 1 }} />
                        <Typography variant="body1" sx={{ mr: 2 }}>
                          {username}
                        </Typography>
                        <Button 
                          variant="outlined" 
                          color="inherit" 
                          onClick={handleLogout}
                          size="small"
                        >
                          Logout
                        </Button>
                      </Box>
                    </Box>
                  )}
                </>
              ) : (
                <Button 
                  color="inherit" 
                  startIcon={<AccountCircleIcon />}
                  onClick={() => setLoginOpen(true)}
                >
                  Login
                </Button>
              )}
            </Toolbar>
          </AppBar>

          {/* Mobile Menu */}
          {loggedIn && mobileMenuOpen && (
            <Paper 
              elevation={3} 
              sx={{ 
                position: 'absolute', 
                top: 64, 
                right: 16, 
                zIndex: 1000,
                width: '200px',
                p: 2
              }}
            >
              <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                <Button 
                  color="inherit" 
                  component={Link} 
                  to="/portfolio"
                  onClick={() => setMobileMenuOpen(false)}
                  sx={{ justifyContent: 'flex-start', mb: 1 }}
                >
                  Portfolio
                </Button>
                <Button 
                  color="inherit" 
                  component={Link} 
                  to="/tracking"
                  onClick={() => setMobileMenuOpen(false)}
                  sx={{ justifyContent: 'flex-start', mb: 1 }}
                >
                  Tracking
                </Button>
                <Button 
                  color="inherit" 
                  component={Link} 
                  to="/advisor"
                  onClick={() => setMobileMenuOpen(false)}
                  sx={{ justifyContent: 'flex-start', mb: 1 }}
                >
                  Advisor
                </Button>
                <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                  <AccountCircleIcon sx={{ mr: 1 }} />
                  <Typography variant="body2" sx={{ flexGrow: 1 }}>
                    {username}
                  </Typography>
                  <Button 
                    variant="outlined" 
                    color="inherit" 
                    onClick={handleLogout}
                    size="small"
                  >
                    Logout
                  </Button>
                </Box>
              </Box>
            </Paper>
          )}

          {/* Login Dialog */}
          <Dialog open={loginOpen} onClose={() => setLoginOpen(false)}>
            <DialogTitle>Login</DialogTitle>
            <DialogContent>
              <form onSubmit={handleLogin} style={{ marginTop: '16px' }}>
                <TextField
                  autoFocus
                  margin="dense"
                  label="Username"
                  type="text"
                  fullWidth
                  variant="outlined"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
                {loginMessage && (
                  <Typography 
                    variant="body2" 
                    color={loginMessage.includes('failed') ? 'error' : 'success'}
                    sx={{ mt: 1 }}
                  >
                    {loginMessage}
                  </Typography>
                )}
              </form>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setLoginOpen(false)}>Cancel</Button>
              <Button onClick={handleLogin} variant="contained" color="primary">
                Login
              </Button>
            </DialogActions>
          </Dialog>

          {/* Main Content */}
          <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            {loggedIn ? (
              <Routes>
                <Route path="/" element={
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <Typography variant="h4" gutterBottom>
                      Welcome to Portfolio Tracker
                    </Typography>
                    <Typography variant="body1" paragraph>
                      Select a section from the menu above to get started.
                    </Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, mt: 4 }}>
                      <Button 
                        variant="contained" 
                        color="primary" 
                        component={Link} 
                        to="/portfolio"
                        size="large"
                      >
                        View Portfolio
                      </Button>
                      <Button 
                        variant="outlined" 
                        color="primary" 
                        component={Link} 
                        to="/tracking"
                        size="large"
                      >
                        Track Performance
                      </Button>
                    </Box>
                  </Box>
                } />
                <Route path="/portfolio" element={
                  <PortfolioManagement 
                    portfolio={portfolio} 
                    username={username} 
                    fetchPortfolio={fetchPortfolio} 
                    API_BASE_URL={API_BASE_URL} 
                  />
                } />
                <Route path="/tracking" element={
                  <PortfolioTracking 
                    username={username} 
                    API_BASE_URL={API_BASE_URL} 
                  />
                } />
                <Route path="/advisor" element={<Advisor />} />
              </Routes>
            ) : (
              <Box sx={{ 
                display: 'flex', 
                flexDirection: 'column', 
                alignItems: 'center', 
                justifyContent: 'center',
                minHeight: '70vh',
                textAlign: 'center'
              }}>
                <Typography variant="h4" gutterBottom>
                  Welcome to Portfolio Tracker
                </Typography>
                <Typography variant="body1" paragraph sx={{ maxWidth: '600px', mb: 4 }}>
                  Track your investments, monitor performance, and get personalized advice.
                  Login to get started.
                </Typography>
                <Button 
                  variant="contained" 
                  color="primary" 
                  size="large"
                  startIcon={<AccountCircleIcon />}
                  onClick={() => setLoginOpen(true)}
                >
                  Login
                </Button>
              </Box>
            )}
          </Container>
        </div>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
