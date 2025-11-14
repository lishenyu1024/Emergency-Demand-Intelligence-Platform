// lifeflight-dashboard-frontend/src/components/PredTest.jsx
import { useState } from 'react';
import { 
  Box, 
  Button, 
  TextField, 
  Typography, 
  Select, 
  MenuItem, 
  FormControl, 
  InputLabel,
  CircularProgress,
  Alert,
  Paper,
  Grid
} from '@mui/material';
import { useTheme } from '@mui/material';
import { tokens } from '../theme';
import { ResponsiveLine } from "@nivo/line";

const PredTest = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  
  // State management
  const [modelName, setModelName] = useState('prophet');
  const [years, setYears] = useState(3);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  
  // Fetch prediction data
  const fetchPrediction = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    
    try {
      const response = await fetch('http://localhost:5001/api/predict_demand', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model_name: modelName,
          years: years
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.status === 'success') {
        setResult(data.data);
      } else {
        throw new Error(data.message || 'Prediction failed');
      }
    } catch (err) {
      setError(err.message);
      console.error('Prediction request failed:', err);
    } finally {
      setLoading(false);
    }
  };
  
  // Prepare chart data (Nivo Line Chart format)
  const prepareChartData = () => {
    if (!result) return [];
    
    // Historical data
    const historicalData = result.historical_data.map(item => ({
      x: item.date,
      y: item.count
    }));
    
    // Forecast data
    const forecastData = result.forecast_data.map(item => ({
      x: item.date,
      y: item.predicted_count
    }));
    
    // Upper confidence interval
    const upperBoundData = result.forecast_data.map(item => ({
      x: item.date,
      y: item.upper_bound
    }));
    
    // Lower confidence interval
    const lowerBoundData = result.forecast_data.map(item => ({
      x: item.date,
      y: item.lower_bound
    }));
    
    return [
      {
        id: 'Historical Data',
        data: historicalData,
        color: colors.blueAccent[500]
      },
      {
        id: 'Forecast',
        data: forecastData,
        color: colors.greenAccent[500]
      },
      {
        id: 'Upper Bound',
        data: upperBoundData,
        color: colors.redAccent[300]
      },
      {
        id: 'Lower Bound',
        data: lowerBoundData,
        color: colors.redAccent[300]
      }
    ];
  };
  
  const chartData = prepareChartData();
  
  return (
    <Box m="20px">
      <Typography variant="h2" sx={{ mb: "20px", color: colors.grey[100] }}>
        Demand Prediction
      </Typography>
      
      {/* Parameter selection area */}
      <Paper sx={{ p: 3, mb: 3, backgroundColor: colors.primary[400] }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel sx={{ color: colors.grey[100] }}>Model Type</InputLabel>
              <Select
                value={modelName}
                label="Model Type"
                onChange={(e) => setModelName(e.target.value)}
                sx={{
                  color: colors.grey[100],
                  '& .MuiOutlinedInput-notchedOutline': {
                    borderColor: colors.grey[100],
                  },
                  '&:hover .MuiOutlinedInput-notchedOutline': {
                    borderColor: colors.grey[100],
                  },
                  '& .MuiSvgIcon-root': {
                    color: colors.grey[100],
                  },
                }}
              >
                <MenuItem value="prophet">Prophet</MenuItem>
                <MenuItem value="arima">ARIMA</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              type="number"
              label="Forecast Years"
              value={years}
              onChange={(e) => setYears(parseInt(e.target.value) || 1)}
              inputProps={{ min: 1, max: 10 }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  color: colors.grey[100],
                  '& fieldset': {
                    borderColor: colors.grey[100],
                  },
                  '&:hover fieldset': {
                    borderColor: colors.grey[100],
                  },
                },
                '& .MuiInputLabel-root': {
                  color: colors.grey[100],
                },
              }}
            />
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Button
              fullWidth
              variant="contained"
              onClick={fetchPrediction}
              disabled={loading}
              sx={{
                backgroundColor: colors.blueAccent[700],
                color: colors.grey[100],
                fontSize: "16px",
                fontWeight: "bold",
                padding: "12px 24px",
                '&:hover': {
                  backgroundColor: colors.blueAccent[600],
                },
              }}
            >
              {loading ? <CircularProgress size={24} /> : 'Start Prediction'}
            </Button>
          </Grid>
        </Grid>
      </Paper>
      
      {/* Error message */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      {/* Results display */}
      {result && (
        <Box>
          {/* Statistics */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, backgroundColor: colors.primary[400], textAlign: 'center' }}>
                <Typography variant="h6" sx={{ color: colors.grey[100], mb: 1 }}>
                  Model Type
                </Typography>
                <Typography variant="h4" sx={{ color: colors.greenAccent[400], fontWeight: 'bold' }}>
                  {result.model_type.toUpperCase()}
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, backgroundColor: colors.primary[400], textAlign: 'center' }}>
                <Typography variant="h6" sx={{ color: colors.grey[100], mb: 1 }}>
                  Historical Data Points
                </Typography>
                <Typography variant="h4" sx={{ color: colors.blueAccent[400], fontWeight: 'bold' }}>
                  {result.historical_data.length}
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, backgroundColor: colors.primary[400], textAlign: 'center' }}>
                <Typography variant="h6" sx={{ color: colors.grey[100], mb: 1 }}>
                  Forecast Data Points
                </Typography>
                <Typography variant="h4" sx={{ color: colors.greenAccent[400], fontWeight: 'bold' }}>
                  {result.forecast_data.length}
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, backgroundColor: colors.primary[400], textAlign: 'center' }}>
                <Typography variant="h6" sx={{ color: colors.grey[100], mb: 1 }}>
                  Total Months
                </Typography>
                <Typography variant="h4" sx={{ color: colors.redAccent[400], fontWeight: 'bold' }}>
                  {result.total_months}
                </Typography>
              </Paper>
            </Grid>
          </Grid>
          
          {/* Chart */}
          <Paper sx={{ p: 3, backgroundColor: colors.primary[400], height: "500px" }}>
            <Typography variant="h5" sx={{ mb: 2, color: colors.grey[100] }}>
              Historical Data and Forecast Trend
            </Typography>
            <ResponsiveLine
              data={chartData}
              theme={{
                axis: {
                  domain: {
                    line: {
                      stroke: colors.grey[100],
                    },
                  },
                  legend: {
                    text: {
                      fill: colors.grey[100],
                    },
                  },
                  ticks: {
                    line: {
                      stroke: colors.grey[100],
                      strokeWidth: 1,
                    },
                    text: {
                      fill: colors.grey[100],
                    },
                  },
                },
                legends: {
                  text: {
                    fill: colors.grey[100],
                  },
                },
                tooltip: {
                  container: {
                    color: colors.primary[500],
                  },
                },
              }}
              colors={{ scheme: "nivo" }}
              margin={{ top: 50, right: 110, bottom: 50, left: 60 }}
              xScale={{ type: "point" }}
              yScale={{
                type: "linear",
                min: "auto",
                max: "auto",
                stacked: false,
                reverse: false,
              }}
              yFormat=" >-.0f"
              curve="catmullRom"
              axisTop={null}
              axisRight={null}
              axisBottom={{
                orient: "bottom",
                tickSize: 5,
                tickPadding: 5,
                tickRotation: -45,
                legend: "Date",
                legendOffset: 50,
                legendPosition: "middle",
              }}
              axisLeft={{
                orient: "left",
                tickSize: 5,
                tickPadding: 5,
                tickRotation: 0,
                legend: "Task Count",
                legendOffset: -50,
                legendPosition: "middle",
              }}
              enableGridX={false}
              enableGridY={true}
              pointSize={6}
              pointColor={{ theme: "background" }}
              pointBorderWidth={2}
              pointBorderColor={{ from: "serieColor" }}
              pointLabelYOffset={-12}
              useMesh={true}
              legends={[
                {
                  anchor: "bottom-right",
                  direction: "column",
                  justify: false,
                  translateX: 100,
                  translateY: 0,
                  itemsSpacing: 0,
                  itemDirection: "left-to-right",
                  itemWidth: 80,
                  itemHeight: 20,
                  itemOpacity: 0.75,
                  symbolSize: 12,
                  symbolShape: "circle",
                  symbolBorderColor: "rgba(0, 0, 0, .5)",
                },
              ]}
            />
          </Paper>
          
          {/* Forecast data table (optional) */}
          <Paper sx={{ p: 3, mt: 3, backgroundColor: colors.primary[400] }}>
            <Typography variant="h5" sx={{ mb: 2, color: colors.grey[100] }}>
              Forecast Results Details (First 12 Months)
            </Typography>
            <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
              <table style={{ width: '100%', color: colors.grey[100] }}>
                <thead>
                  <tr style={{ borderBottom: `1px solid ${colors.grey[700]}` }}>
                    <th style={{ padding: '10px', textAlign: 'left' }}>Date</th>
                    <th style={{ padding: '10px', textAlign: 'right' }}>Forecast</th>
                    <th style={{ padding: '10px', textAlign: 'right' }}>Lower Bound</th>
                    <th style={{ padding: '10px', textAlign: 'right' }}>Upper Bound</th>
                  </tr>
                </thead>
                <tbody>
                  {result.forecast_data.slice(0, 12).map((item, index) => (
                    <tr key={index} style={{ borderBottom: `1px solid ${colors.grey[800]}` }}>
                      <td style={{ padding: '10px' }}>{item.date}</td>
                      <td style={{ padding: '10px', textAlign: 'right', fontWeight: 'bold' }}>
                        {item.predicted_count}
                      </td>
                      <td style={{ padding: '10px', textAlign: 'right' }}>{item.lower_bound}</td>
                      <td style={{ padding: '10px', textAlign: 'right' }}>{item.upper_bound}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Box>
          </Paper>
        </Box>
      )}
    </Box>
  );
};

export default PredTest;