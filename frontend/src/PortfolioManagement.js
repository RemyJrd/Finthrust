import React, { useState } from 'react';
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
} from '@mui/material';

function PortfolioManagement({ portfolio, username, fetchPortfolio, API_BASE_URL }) {
  const [ticker, setTicker] = useState('');
  const [quantity, setQuantity] = useState('');
  const [purchasePrice, setPurchasePrice] = useState('');
  const [purchaseDate, setPurchaseDate] = useState(''); // New state for purchase date
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('success'); // 'success', 'error', 'info', 'warning'

  const handleAddPosition = async (e) => {
    e.preventDefault();
    if (!username) {
      setSnackbarMessage('Please login first');
      setSnackbarSeverity('warning');
      setOpenSnackbar(true);
      return;
    }
    try {
      const positionData = {
        ticker: ticker.toUpperCase(),
        quantity: parseFloat(quantity),
        purchase_price: parseFloat(purchasePrice),
        purchase_date: purchaseDate, // Include purchase date
      };
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

  if (!portfolio) {
    return <CircularProgress />; // Loading indicator
  }

  return (
    <div className="portfolio-management">
      <h3>Your Portfolio</h3>
      <div className="portfolio-summary">
        <p>Total Value: ${portfolio.total_value?.toFixed(2)}</p>
        <p>
          Total P&L:{' '}
          <span style={{ color: portfolio.total_pnl >= 0 ? 'lightgreen' : '#FFCCCB' }}>
            ${portfolio.total_pnl?.toFixed(2)} ({portfolio.total_pnl_percent?.toFixed(2)}%)
          </span>
        </p>
      </div>

      {portfolio.positions_pnl && portfolio.positions_pnl.length > 0 ? (
        <TableContainer component={Paper}>
          <Table className="positions-table">
            <TableHead>
              <TableRow>
                <TableCell>Ticker</TableCell>
                <TableCell align="right">Quantity</TableCell>
                <TableCell align="right">Purchase Price</TableCell>
                {/* Add more columns if needed, e.g., Purchase Date */}
              </TableRow>
            </TableHead>
            <TableBody>
              {portfolio.positions_pnl.map((pos, index) => (
                <TableRow key={index}>
                  <TableCell component="th" scope="row">
                    {pos.ticker}
                  </TableCell>
                  <TableCell align="right">{pos.quantity}</TableCell>
                  <TableCell align="right">${pos.purchase_price?.toFixed(2)}</TableCell>
                  {/* Add more cells if needed, e.g., pos.purchase_date */}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      ) : (
        <p>No positions yet.</p>
      )}

      <div className="form-container">
        <h3>Add New Position</h3>
        <form onSubmit={handleAddPosition}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={3}>
              <TextField
                label="Ticker"
                value={ticker}
                onChange={(e) => setTicker(e.target.value)}
                required
                fullWidth
              />
            </Grid>
            <Grid item xs={12} sm={3}> {/* Adjusted sm size */}
              <TextField
                label="Quantity"
                type="number"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                required
                fullWidth
              />
            </Grid>
            <Grid item xs={12} sm={3}> {/* Adjusted sm size */}
              <TextField
                label="Purchase Price"
                type="number"
                step="0.01"
                value={purchasePrice}
                onChange={(e) => setPurchasePrice(e.target.value)}
                required
                fullWidth
              />
            </Grid>
            <Grid item xs={12} sm={3}> {/* Adjusted sm size */}
              <TextField
                label="Purchase Date"
                type="date"
                value={purchaseDate}
                onChange={(e) => setPurchaseDate(e.target.value)}
                required
                fullWidth
                InputLabelProps={{
                  shrink: true,
                }}
              />
            </Grid> {/* Corrected closing tag placement */}
            <Grid item xs={12}>
              <Button type="submit" variant="contained" color="primary">
                Add Position
              </Button>
            </Grid>
          </Grid>
        </form>
      </div>

      <Snackbar open={openSnackbar} autoHideDuration={6000} onClose={handleCloseSnackbar}>
        <Alert onClose={handleCloseSnackbar} severity={snackbarSeverity} sx={{ width: '100%' }}>
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </div>
  );
}

export default PortfolioManagement;