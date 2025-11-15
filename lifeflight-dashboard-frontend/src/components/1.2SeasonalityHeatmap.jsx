// 1.2 Seasonality & Day-of-Week/Hour Heatmap
// Chart 1.2: Seasonality Pattern Heatmap - Display weekday × hour emergency medical task demand distribution by month

import { useState, useEffect } from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  Select, 
  MenuItem, 
  FormControl, 
  InputLabel,
  CircularProgress,
  Alert,
  Grid,
  ToggleButton,
  ToggleButtonGroup
} from '@mui/material';
import { useTheme } from '@mui/material';
import { tokens } from '../theme';
import { ResponsiveHeatMap } from '@nivo/heatmap';

const SeasonalityHeatmap = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  
  const [year, setYear] = useState(2023);
  const [locationLevel, setLocationLevel] = useState('system');
  const [locationValue, setLocationValue] = useState(null);
  const [selectedMonth, setSelectedMonth] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [heatmapData, setHeatmapData] = useState(null);
  const [stats, setStats] = useState(null);
  
  const availableYears = [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023];
  
  useEffect(() => {
    fetchHeatmapData();
  }, [year, locationLevel, locationValue]);
  
  const fetchHeatmapData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams({
        year: year.toString(),
        location_level: locationLevel
      });
      
      if (locationValue) {
        params.append('location_value', locationValue);
      }
      
      const response = await fetch(`http://localhost:5001/api/seasonality_heatmap?${params}`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.status === 'success') {
        setHeatmapData(data.data.heatmap_data);
        setStats(data.data.stats);
        if (data.data.heatmap_data && data.data.heatmap_data.length > 0) {
          setSelectedMonth(1);
        }
      } else {
        throw new Error(data.message || 'Failed to fetch heatmap data');
      }
    } catch (err) {
      setError(err.message);
      console.error('Seasonality heatmap request failed:', err);
    } finally {
      setLoading(false);
    }
  };
  
  const prepareChartData = () => {
    if (!heatmapData || heatmapData.length === 0) return [];
    
    const monthData = heatmapData.find(m => m.month === selectedMonth);
    if (!monthData) return [];
    
    const weekdayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    
    const chartData = monthData.heatmap.map((weekdayData, idx) => {
      const dataPoints = weekdayData.values.map(hourData => ({
        x: hourData.hour.toString().padStart(2, '0') + ':00',
        y: hourData.missions_per_1000
      }));
      
      return {
        id: weekdayNames[weekdayData.weekday],
        data: dataPoints
      };
    });
    
    return chartData;
  };
  
  const chartData = prepareChartData();
  
  const getMinMaxValues = () => {
    if (!heatmapData || heatmapData.length === 0) return { min: 0, max: 1 };
    
    let min = Infinity;
    let max = -Infinity;
    
    heatmapData.forEach(monthData => {
      monthData.heatmap.forEach(weekdayData => {
        weekdayData.values.forEach(hourData => {
          const value = hourData.missions_per_1000;
          if (value < min) min = value;
          if (value > max) max = value;
        });
      });
    });
    
    return { min: min === Infinity ? 0 : min, max: max === -Infinity ? 1 : max };
  };
  
  const { min, max } = getMinMaxValues();
  
  return (
    <Box mx="20px" my="20px" mt="0px">
      <Typography variant="h3" sx={{ mb: "10px", color: colors.grey[100] }}>
        1.2 Seasonality & Day-of-Week/Hour Heatmap
      </Typography>
      <Typography variant="h6" sx={{ mb: "10px", color: colors.grey[300] }}>
        Seasonality Pattern Heatmap: Display weekday × hour emergency medical task demand distribution by month
      </Typography>
      <Typography variant="body2" sx={{ mb: "20px", color: colors.grey[400], fontStyle: 'italic' }}>
        This chart aggregates historical operational data (month × weekday × hour) to reveal seasonal patterns and cyclical trends in LifeFlight demand.
        Color intensity represents the average number of missions per 1,000 population, helping to identify seasonal peaks, weekday vs weekend differences, and task distribution across different times of day.
      </Typography>
      
      <Paper sx={{ p: 3, mb: 3, backgroundColor: colors.primary[400] }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel sx={{ color: colors.grey[100] }}>Year</InputLabel>
              <Select
                value={year}
                label="Year"
                onChange={(e) => setYear(e.target.value)}
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
                {availableYears.map(y => (
                  <MenuItem key={y} value={y}>{y}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel sx={{ color: colors.grey[100] }}>Location Level</InputLabel>
              <Select
                value={locationLevel}
                label="Location Level"
                onChange={(e) => {
                  setLocationLevel(e.target.value);
                  setLocationValue(null);
                }}
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
                <MenuItem value="system">System (State-wide)</MenuItem>
                <MenuItem value="state">State</MenuItem>
                <MenuItem value="county">County</MenuItem>
                <MenuItem value="city">City</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Typography variant="body1" sx={{ color: colors.grey[100], mb: 1 }}>
              Select Month:
            </Typography>
            {heatmapData && heatmapData.length > 0 && (
              <ToggleButtonGroup
                value={selectedMonth}
                exclusive
                onChange={(e, newValue) => newValue !== null && setSelectedMonth(newValue)}
                sx={{
                  '& .MuiToggleButton-root': {
                    color: colors.grey[100],
                    borderColor: colors.grey[700],
                    '&.Mui-selected': {
                      backgroundColor: colors.blueAccent[700],
                      color: colors.grey[100],
                      '&:hover': {
                        backgroundColor: colors.blueAccent[600],
                      },
                    },
                  },
                }}
              >
                {heatmapData.map((monthData) => (
                  <ToggleButton key={monthData.month} value={monthData.month} size="small">
                    {monthData.month_name.substring(0, 3)}
                  </ToggleButton>
                ))}
              </ToggleButtonGroup>
            )}
          </Grid>
        </Grid>
      </Paper>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      {loading && (
        <Box display="flex" justifyContent="center" alignItems="center" height="400px">
          <CircularProgress />
        </Box>
      )}
      
      {!loading && chartData && chartData.length > 0 && (
        <Box>
          {stats && (
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} md={3}>
                <Paper sx={{ p: 2, backgroundColor: colors.primary[400], textAlign: 'center' }}>
                  <Typography variant="h6" sx={{ color: colors.grey[100], mb: 1 }}>
                    Total Missions
                  </Typography>
                  <Typography variant="h4" sx={{ color: colors.blueAccent[400], fontWeight: 'bold' }}>
                    {stats.total_missions.toLocaleString()}
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} md={3}>
                <Paper sx={{ p: 2, backgroundColor: colors.primary[400], textAlign: 'center' }}>
                  <Typography variant="h6" sx={{ color: colors.grey[100], mb: 1 }}>
                    Avg per 1,000
                  </Typography>
                  <Typography variant="h4" sx={{ color: colors.greenAccent[400], fontWeight: 'bold' }}>
                    {stats.avg_missions_per_1000.toFixed(4)}
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} md={3}>
                <Paper sx={{ p: 2, backgroundColor: colors.primary[400], textAlign: 'center' }}>
                  <Typography variant="h6" sx={{ color: colors.grey[100], mb: 1 }}>
                    Peak Intensity
                  </Typography>
                  <Typography variant="h4" sx={{ color: colors.redAccent[400], fontWeight: 'bold' }}>
                    {stats.max_missions_per_1000.toFixed(4)}
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} md={3}>
                <Paper sx={{ p: 2, backgroundColor: colors.primary[400], textAlign: 'center' }}>
                  <Typography variant="h6" sx={{ color: colors.grey[100], mb: 1 }}>
                    Peak Time
                  </Typography>
                  {stats.peak_time && (
                    <Typography variant="body1" sx={{ color: colors.grey[300] }}>
                      {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][stats.peak_time.month - 1]}, {' '}
                      {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][stats.peak_time.weekday]}, {' '}
                      {stats.peak_time.hour.toString().padStart(2, '0')}:00
                    </Typography>
                  )}
                </Paper>
              </Grid>
            </Grid>
          )}
          
          <Paper sx={{ p: 3, backgroundColor: colors.primary[400], height: "700px", width: "100%", minWidth: "1200px" }}>
            <Typography variant="h5" sx={{ mb: 2, color: colors.grey[100] }}>
              {heatmapData && heatmapData.find(m => m.month === selectedMonth)
                ? `${heatmapData.find(m => m.month === selectedMonth).month_name} ${year} - Hour × Weekday Heatmap`
                : 'Seasonality Heatmap'}
            </Typography>
            <Typography variant="body2" sx={{ mb: 2, color: colors.grey[300] }}>
              Color intensity represents missions per 1,000 population
            </Typography>
            <Box height="600px" width="100%" sx={{ overflowX: 'auto' }}>
              <ResponsiveHeatMap
                data={chartData}
                margin={{ top: 60, right: 90, bottom: 160, left: 90 }}
                valueFormat=" >-.4f"
                axisTop={{
                  tickSize: 5,
                  tickPadding: 5,
                  tickRotation: -90,
                  legend: '',
                  legendOffset: 46
                }}
                axisRight={{
                  tickSize: 5,
                  tickPadding: 5,
                  tickRotation: 0,
                  legend: 'Weekday',
                  legendPosition: 'middle',
                  legendOffset: 70
                }}
                axisLeft={{
                  tickSize: 5,
                  tickPadding: 5,
                  tickRotation: 0,
                  legend: 'Weekday',
                  legendPosition: 'middle',
                  legendOffset: -72
                }}
                axisBottom={{
                  tickSize: 5,
                  tickPadding: 5,
                  tickRotation: -90,
                  legend: 'Hour',
                  legendPosition: 'middle',
                  legendOffset: 50
                }}
                colors={{
                  type: 'sequential',
                  scheme: 'reds',
                  minValue: min,
                  maxValue: max,
                }}
                emptyColor="#555555"
                legends={[
                  {
                    anchor: 'bottom',
                    translateX: 0,
                    translateY: 100,
                    length: 400,
                    thickness: 8,
                    direction: 'row',
                    tickPosition: 'after',
                    tickSize: 3,
                    tickSpacing: 4,
                    tickOverlap: false,
                    tickFormat: ' >-.4f',
                    title: 'Missions per 1,000 Population →',
                    titleAlign: 'start',
                    titleOffset: 4
                  }
                ]}
                theme={{
                  axis: {
                    domain: {
                      line: {
                        stroke: colors.grey[100],
                        strokeWidth: 1
                      }
                    },
                    legend: {
                      text: {
                        fill: colors.grey[100]
                      }
                    },
                    ticks: {
                      line: {
                        stroke: colors.grey[100],
                        strokeWidth: 1
                      },
                      text: {
                        fill: colors.grey[100]
                      }
                    }
                  },
                  tooltip: {
                    container: {
                      background: colors.primary[500],
                      color: colors.grey[100]
                    }
                  }
                }}
              />
            </Box>
          </Paper>
        </Box>
      )}
    </Box>
  );
};

export default SeasonalityHeatmap;
