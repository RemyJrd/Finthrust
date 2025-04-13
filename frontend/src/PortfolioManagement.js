import React, { useState, useEffect } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TextField,
  Button,
  Grid,
  CircularProgress,
  Snackbar,
  Alert,
  FormControlLabel,
  Switch,
  Typography,
  Autocomplete,
  Box,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  Chip,
} from '@mui/material';
import { styled } from '@mui/material/styles';

// Add styled components for better organization and styling
const StyledFormContainer = styled('div')(({ theme }) => ({
  padding: theme.spacing(3),
  '& .MuiGrid-container': {
    marginTop: theme.spacing(2),
  },
}));

const StyledAutocomplete = styled(Autocomplete)(({ theme }) => ({
  '& .MuiAutocomplete-listbox': {
    maxHeight: '400px',
    '& .MuiAutocomplete-option': {
      padding: theme.spacing(2),
    },
  },
  '& .MuiAutocomplete-popper': {
    width: '500px !important',
  },
  '& .MuiInputBase-root': {
    minHeight: '56px',
  },
}));

const StyledPortfolioContainer = styled('div')(({ theme }) => ({
  padding: theme.spacing(3),
  '& .portfolio-summary': {
    marginBottom: theme.spacing(4),
    '& p': {
      fontSize: '1.1rem',
      marginBottom: theme.spacing(1),
    },
  },
  '& .positions-table': {
    marginBottom: theme.spacing(4),
  },
}));

function PortfolioManagement({ portfolio, username, fetchPortfolio, API_BASE_URL }) {
  const [ticker, setTicker] = useState('');
  const [quantity, setQuantity] = useState('');
  const [purchasePrice, setPurchasePrice] = useState('');
  const [purchaseDate, setPurchaseDate] = useState(''); // New state for purchase date
  const [useHistoricalPrice, setUseHistoricalPrice] = useState(false); // Toggle for historical price
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('success'); // 'success', 'error', 'info', 'warning'
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);

  // Function to search for stocks
  const searchStocks = async (query) => {
    if (!query || query.length < 2) {
      setSearchResults([]);
      return;
    }
    
    setSearchLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/search/stocks?query=${encodeURIComponent(query)}`);
      const data = await response.json();
      setSearchResults(data);
      setSearchOpen(true);
    } catch (error) {
      console.error('Error searching stocks:', error);
    } finally {
      setSearchLoading(false);
    }
  };

  // Debounce the search to avoid too many API calls
  useEffect(() => {
    const timer = setTimeout(() => {
      if (ticker) {
        searchStocks(ticker);
      } else {
        setSearchResults([]);
      }
    }, 300); // 300ms delay
    
    return () => clearTimeout(timer);
  }, [ticker]);

  const handleAddPosition = async (e) => {
    e.preventDefault();
    if (!username) {
      setSnackbarMessage('Please login first');
      setSnackbarSeverity('warning');
      setOpenSnackbar(true);
      return;
    }
    
    // Validate required fields
    if (!ticker || !quantity || (!purchasePrice && !purchaseDate)) {
      setSnackbarMessage('Please fill in all required fields');
      setSnackbarSeverity('error');
      setOpenSnackbar(true);
      return;
    }
    
    try {
      const positionData = {
        ticker: ticker.toUpperCase(),
        quantity: parseFloat(quantity),
        purchase_date: purchaseDate,
      };
      
      // Only include purchase_price if manually entered
      if (!useHistoricalPrice && purchasePrice) {
        positionData.purchase_price = parseFloat(purchasePrice);
      }
      
      const response = await fetch(`${API_BASE_URL}/users/${username}/positions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(positionData),
      });
      const data = await response.json();
      if (response.ok) {
        setSnackbarMessage(data.message);
        setSnackbarSeverity('success');
        setOpenSnackbar(true);
        setTicker('');
        setQuantity('');
        setPurchasePrice('');
        setPurchaseDate(''); // Clear the date field
        fetchPortfolio();
      } else {
        setSnackbarMessage(data.detail || 'Failed to add position');
        setSnackbarSeverity('error');
        setOpenSnackbar(true);
      }
    } catch (error) {
      console.error('Error adding position:', error);
      setSnackbarMessage('Failed to add position due to network error.');
      setSnackbarSeverity('error');
      setOpenSnackbar(true);
    }
  };

  const handleCloseSnackbar = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }
    setOpenSnackbar(false);
  };

  const handleToggleHistoricalPrice = (event) => {
    setUseHistoricalPrice(event.target.checked);
    // Clear purchase price when switching to historical price
    if (event.target.checked) {
      setPurchasePrice('');
    }
  };

  const handleSelectStock = (selectedStock) => {
    if (selectedStock) {
      setTicker(selectedStock.ticker);
      setSearchOpen(false);
    }
  };

  if (!portfolio) {
    return <CircularProgress />; // Loading indicator
  }

  return (
    <StyledPortfolioContainer>
      <Typography variant="h4" gutterBottom>
        Your Portfolio
      </Typography>
      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <div className="portfolio-summary">
          <Typography variant="h6" gutterBottom>
            Total Value: ${portfolio.total_value?.toFixed(2)}
          </Typography>
          <Typography variant="h6">
            Total P&L:{' '}
            <Box component="span" sx={{ 
              color: portfolio.total_pnl >= 0 ? 'success.main' : 'error.main',
              fontWeight: 'bold'
            }}>
              ${portfolio.total_pnl?.toFixed(2)} ({portfolio.total_pnl_percent?.toFixed(2)}%)
            </Box>
          </Typography>
        </div>

        {portfolio.positions_pnl && portfolio.positions_pnl.length > 0 ? (
          <TableContainer>
            <Table className="positions-table" size="medium">
              <TableHead>
                <TableRow>
                  <TableCell>Ticker</TableCell>
                  <TableCell align="right">Quantity</TableCell>
                  <TableCell align="right">Purchase Price</TableCell>
                  <TableCell align="right">Purchase Date</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {portfolio.positions_pnl.map((pos, index) => (
                  <TableRow key={index}>
                    <TableCell component="th" scope="row">
                      <Typography variant="body1" fontWeight="medium">
                        {pos.ticker}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">{pos.quantity}</TableCell>
                    <TableCell align="right">${pos.purchase_price?.toFixed(2)}</TableCell>
                    <TableCell align="right">{pos.purchase_date}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        ) : (
          <Typography variant="body1" color="text.secondary">
            No positions yet.
          </Typography>
        )}
      </Paper>

      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Add New Position
        </Typography>
        <StyledFormContainer>
          <form onSubmit={handleAddPosition}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <StyledAutocomplete
                  freeSolo
                  options={searchResults}
                  getOptionLabel={(option) => option.ticker}
                  value={searchResults.find(s => s.ticker === ticker) || null}
                  onChange={(event, newValue) => handleSelectStock(newValue)}
                  onInputChange={(event, newInputValue) => setTicker(newInputValue)}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Search Stock Symbol or Company Name"
                      required
                      fullWidth
                      InputProps={{
                        ...params.InputProps,
                        endAdornment: (
                          <>
                            {searchLoading ? <CircularProgress color="inherit" size={20} /> : null}
                            {params.InputProps.endAdornment}
                          </>
                        ),
                      }}
                    />
                  )}
                  renderOption={(props, option) => (
                    <li {...props}>
                      <Box sx={{ 
                        display: 'flex', 
                        flexDirection: 'column', 
                        width: '100%',
                        py: 1
                      }}>
                        <Box sx={{ 
                          display: 'flex', 
                          justifyContent: 'space-between', 
                          alignItems: 'center',
                          mb: 1
                        }}>
                          <Typography variant="h6" component="span">
                            {option.ticker}
                          </Typography>
                          <Chip 
                            label={option.exchange} 
                            size="small" 
                            color="primary" 
                            variant="outlined"
                            sx={{ ml: 2 }}
                          />
                        </Box>
                        <Typography 
                          variant="body1" 
                          color="text.secondary"
                          sx={{ fontWeight: 'medium' }}
                        >
                          {option.name}
                        </Typography>
                      </Box>
                    </li>
                  )}
                  PopperComponent={({ style, ...props }) => (
                    <Box component="div" {...props} 
                      sx={{ 
                        width: '100% !important',
                        maxWidth: '800px !important',
                        ...style
                      }} 
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  label="Quantity"
                  type="number"
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                  required
                  fullWidth
                  InputProps={{
                    inputProps: { min: 0 }
                  }}
                  sx={{
                    '& .MuiInputBase-root': {
                      height: '56px',
                    },
                  }}
                />
              </Grid>

              <Grid item xs={12}>
                <Paper 
                  variant="outlined" 
                  sx={{ 
                    p: 2,
                    backgroundColor: 'background.default',
                    borderColor: 'divider',
                  }}
                >
                  <FormControlLabel
                    control={
                      <Switch
                        checked={useHistoricalPrice}
                        onChange={handleToggleHistoricalPrice}
                        color="primary"
                      />
                    }
                    label={
                      <Typography variant="body1">
                        Use historical price based on purchase date
                      </Typography>
                    }
                  />
                </Paper>
              </Grid>

              {!useHistoricalPrice && (
                <Grid item xs={12} md={6}>
                  <TextField
                    label="Purchase Price"
                    type="number"
                    step="0.01"
                    value={purchasePrice}
                    onChange={(e) => setPurchasePrice(e.target.value)}
                    required={!useHistoricalPrice}
                    fullWidth
                    InputProps={{
                      startAdornment: <Typography variant="body1" sx={{ mr: 1 }}>$</Typography>,
                      inputProps: { min: 0, step: "0.01" }
                    }}
                    sx={{
                      '& .MuiInputBase-root': {
                        height: '56px',
                      },
                    }}
                  />
                </Grid>
              )}

              <Grid item xs={12} md={6}>
                <TextField
                  label="Purchase Date"
                  type="date"
                  value={purchaseDate}
                  onChange={(e) => setPurchaseDate(e.target.value)}
                  required={useHistoricalPrice}
                  fullWidth
                  InputLabelProps={{
                    shrink: true,
                  }}
                  sx={{
                    '& .MuiInputBase-root': {
                      height: '56px',
                    },
                  }}
                />
              </Grid>

              <Grid item xs={12}>
                <Button 
                  type="submit" 
                  variant="contained" 
                  color="primary"
                  size="large"
                  sx={{ 
                    py: 1.5,
                    px: 4,
                    fontSize: '1.1rem',
                    minHeight: '56px',
                  }}
                >
                  Add Position
                </Button>
              </Grid>
            </Grid>
          </form>
        </StyledFormContainer>
      </Paper>

      <Snackbar 
        open={openSnackbar} 
        autoHideDuration={6000} 
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbarSeverity} 
          sx={{ width: '100%' }}
          variant="filled"
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </StyledPortfolioContainer>
  );
}

export default PortfolioManagement;