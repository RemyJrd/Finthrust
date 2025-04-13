import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  Filler,
} from 'chart.js';
import 'chartjs-adapter-date-fns';
import zoomPlugin from 'chartjs-plugin-zoom';
import { Paper, CircularProgress, Alert, Box, Typography, ToggleButton, ToggleButtonGroup } from '@mui/material';
import { styled } from '@mui/material/styles';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  TimeScale,
  Title,
  Tooltip,
  Legend,
  Filler,
  zoomPlugin
);

// Predefined color palette for assets
const assetColors = [
  'rgba(75, 192, 192, 0.7)',   // Teal
  'rgba(255, 99, 132, 0.7)',   // Pink
  'rgba(54, 162, 235, 0.7)',   // Blue
  'rgba(255, 206, 86, 0.7)',   // Yellow
  'rgba(153, 102, 255, 0.7)',  // Purple
  'rgba(255, 159, 64, 0.7)',   // Orange
  'rgba(46, 204, 113, 0.7)',   // Green
  'rgba(142, 68, 173, 0.7)',   // Purple
];

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  borderRadius: theme.shape.borderRadius,
  minHeight: '80vh',
  width: '100%',
  display: 'flex',
  flexDirection: 'column',
  '& .chart-container': {
    flex: 1,
    minHeight: '70vh',
    width: '100%',
    position: 'relative',
    '& canvas': {
      maxWidth: '100%',
      height: '100% !important',
    },
  },
}));

const TimeRangeSelector = styled(ToggleButtonGroup)(({ theme }) => ({
  marginBottom: theme.spacing(2),
  '& .MuiToggleButton-root': {
    padding: theme.spacing(1, 3),
    fontSize: '1rem',
  },
}));

function PortfolioTracking({ username, API_BASE_URL }) {
  const [historyData, setHistoryData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('3M'); // Default to 3 months
  const [assetVisibility, setAssetVisibility] = useState({});

  useEffect(() => {
    const fetchPortfolioHistory = async () => {
      setLoading(true);
      setError(null);
      try {
        // Fetch overall portfolio history
        const portfolioResponse = await fetch(`${API_BASE_URL}/users/${username}/portfolio/history`);
        if (!portfolioResponse.ok) {
          throw new Error(`Failed to fetch portfolio history: ${portfolioResponse.status}`);
        }
        const portfolioData = await portfolioResponse.json();

        // Fetch individual asset histories
        const positionsResponse = await fetch(`${API_BASE_URL}/users/${username}/portfolio`);
        if (!positionsResponse.ok) {
          throw new Error(`Failed to fetch positions: ${positionsResponse.status}`);
        }
        const positionsData = await positionsResponse.json();

        // Initialize asset visibility
        const newAssetVisibility = {};
        positionsData.positions_pnl.forEach((position) => {
          newAssetVisibility[position.ticker] = true;
        });
        setAssetVisibility(newAssetVisibility);

        setHistoryData({
          portfolio: portfolioData,
          assets: positionsData.positions_pnl,
        });
      } catch (err) {
        console.error('Error fetching data:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (username) {
      fetchPortfolioHistory();
    }
  }, [username, API_BASE_URL]);

  const handleTimeRangeChange = (event, newRange) => {
    if (newRange !== null) {
      setTimeRange(newRange);
    }
  };

  const toggleAssetVisibility = (ticker) => {
    setAssetVisibility(prev => ({
      ...prev,
      [ticker]: !prev[ticker]
    }));
  };

  const filterDataByTimeRange = (data) => {
    if (!data) return data;
    
    const now = new Date();
    const ranges = {
      '1W': 7,
      '1M': 30,
      '3M': 90,
      '6M': 180,
      '1Y': 365,
      'ALL': Number.MAX_SAFE_INTEGER
    };
    
    const daysToShow = ranges[timeRange];
    const cutoffDate = new Date(now.setDate(now.getDate() - daysToShow));
    
    return data.filter(item => new Date(item.date) >= cutoffDate);
  };

  const chartData = historyData ? {
    labels: filterDataByTimeRange(historyData.portfolio).map(item => item.date),
    datasets: [
      {
        label: 'Total Portfolio Value',
        data: filterDataByTimeRange(historyData.portfolio).map(item => item.value),
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
      },
      ...historyData.assets
        .filter(asset => assetVisibility[asset.ticker])
        .map((asset, index) => ({
          label: `${asset.ticker} (${asset.quantity} shares)`,
          data: filterDataByTimeRange(historyData.portfolio).map(item => 
            asset.quantity * (asset.current_price || 0)
          ),
          borderColor: assetColors[index % assetColors.length],
          backgroundColor: assetColors[index % assetColors.length].replace('0.7', '0.1'),
          borderWidth: 2,
          fill: true,
          tension: 0.4,
        })),
    ],
  } : null;

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top',
        labels: {
          font: {
            size: 14,
          },
          padding: 20,
        },
        onClick: (e, legendItem) => {
          if (legendItem.text !== 'Total Portfolio Value') {
            const ticker = legendItem.text.split(' ')[0];
            toggleAssetVisibility(ticker);
          }
        },
      },
      title: {
        display: true,
        text: 'Portfolio Performance',
        font: {
          size: 24,
          weight: 'bold',
        },
        padding: {
          top: 10,
          bottom: 30,
        },
      },
      zoom: {
        pan: {
          enabled: true,
          mode: 'x',
        },
        zoom: {
          wheel: {
            enabled: true,
          },
          pinch: {
            enabled: true,
          },
          mode: 'x',
          scaleMode: 'x',
        },
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const label = context.dataset.label || '';
            const value = context.parsed.y;
            return `${label}: $${value.toFixed(2)}`;
          },
        },
        titleFont: {
          size: 14,
        },
        bodyFont: {
          size: 13,
        },
        padding: 12,
      },
    },
    scales: {
      x: {
        type: 'time',
        time: {
          unit: timeRange === '1W' ? 'day' : 'month',
          displayFormats: {
            day: 'MMM d',
            month: 'MMM yyyy',
          },
        },
        title: {
          display: true,
          text: 'Date',
          font: {
            size: 14,
          },
        },
        ticks: {
          font: {
            size: 12,
          },
        },
      },
      y: {
        title: {
          display: true,
          text: 'Value ($)',
          font: {
            size: 14,
          },
        },
        ticks: {
          font: {
            size: 12,
          },
          callback: (value) => `$${value.toLocaleString()}`,
        },
        beginAtZero: true,
      },
    },
  };

  return (
    <StyledPaper elevation={3}>
      <Box sx={{ 
        mb: 3,
        display: 'flex',
        flexDirection: 'column',
        gap: 2,
      }}>
        <Typography variant="h4" gutterBottom>
          Portfolio Performance
        </Typography>
        <TimeRangeSelector
          value={timeRange}
          exclusive
          onChange={handleTimeRangeChange}
          aria-label="time range"
          sx={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: 1,
            '& .MuiToggleButton-root': {
              flex: '1 1 auto',
              minWidth: '80px',
            },
          }}
        >
          {['1W', '1M', '3M', '6M', '1Y', 'ALL'].map((range) => (
            <ToggleButton 
              key={range} 
              value={range}
              sx={{
                fontSize: '1rem',
                py: 1,
                px: 2,
              }}
            >
              {range}
            </ToggleButton>
          ))}
        </TimeRangeSelector>
      </Box>
      <Box className="chart-container">
        {loading ? (
          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            height: '100%',
            minHeight: '60vh',
          }}>
            <CircularProgress size={60} />
          </Box>
        ) : error ? (
          <Alert 
            severity="error"
            sx={{ 
              fontSize: '1.1rem',
              py: 2,
            }}
          >
            {error}
          </Alert>
        ) : chartData ? (
          <Line data={chartData} options={options} />
        ) : (
          <Typography 
            variant="h6" 
            color="text.secondary"
            sx={{ 
              textAlign: 'center',
              py: 4,
            }}
          >
            No portfolio history data available.
          </Typography>
        )}
      </Box>
    </StyledPaper>
  );
}

export default PortfolioTracking;