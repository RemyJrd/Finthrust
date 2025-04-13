import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import { Paper, CircularProgress, Alert } from '@mui/material';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

function PortfolioTracking({ username, API_BASE_URL }) {
  const [historyData, setHistoryData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPortfolioHistory = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`${API_BASE_URL}/users/${username}/portfolio/history`);
        if (!response.ok) {
          throw new Error(`Failed to fetch portfolio history: ${response.status}`);
        }
        const data = await response.json();
        setHistoryData(data);
      } catch (err) {
        console.error('Error fetching portfolio history:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (username) {
      fetchPortfolioHistory();
    }
  }, [username, API_BASE_URL]);

  const chartData = historyData
    ? {
        labels: historyData.map((item) => item.date),
        datasets: [
          {
            label: 'Portfolio Value',
            data: historyData.map((item) => item.value),
            borderColor: '#64B5F6',
            tension: 0.1,
          },
        ],
      }
    : null;

  // Chart options
    const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Portfolio Value Over Time',
        font: {
          size: 18,
        },
              },
        },
        scales: {
          x: {
            title: {
              display: true,
              text: 'Date',
            },
          },
          y: {
            title: {
              display: true,
              text: 'Value ($)',
            },
        },
    },
  };

  return (
    <Paper elevation={3} style={{ padding: '20px', borderRadius: '8px' }}>
            {loading ? (
        <CircularProgress />
      ) : error ? (
        <Alert severity="error">{error}</Alert>
      ) : chartData ? (
        <Line data={chartData} options={options} />
      ) : (
        <p>No portfolio history data available.</p>
      )}
          </Paper>
  );
}

export default PortfolioTracking;