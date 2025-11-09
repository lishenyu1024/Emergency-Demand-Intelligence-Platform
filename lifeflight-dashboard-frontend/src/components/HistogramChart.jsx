import { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Chart } from 'react-chartjs-2';
import { useTheme } from "@mui/material";
import { tokens } from "../theme";
import { Box, Typography, ToggleButton, ToggleButtonGroup } from "@mui/material";

// 注册 Chart.js 组件
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const HistogramChart = ({ isDashboard = false }) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [data, setData] = useState({ overall: [], by_season: {} });
  const [viewMode, setViewMode] = useState('overall'); // 'overall' or 'by_season'
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:5001/api/hourly_departure');
        const result = await response.json();
        setData(result.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching hourly departure data:', error);
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return <Box>Loading...</Box>;
  }

  // 准备图表数据
  const getChartData = () => {
    if (viewMode === 'overall') {
      const hours = data.overall.map(item => item.hour);
      const counts = data.overall.map(item => item.count);
      const densities = data.overall.map(item => item.density);
      
      return {
        labels: hours,
        datasets: [
          {
            type: 'bar',
            label: 'Count',
            data: counts,
            backgroundColor: colors.blueAccent[500] + '80', // 80 = 50% opacity
            borderColor: colors.blueAccent[500],
            borderWidth: 1,
            yAxisID: 'y',
          },
          {
            type: 'line',
            label: 'Density',
            data: densities,
            borderColor: colors.greenAccent[500],
            backgroundColor: colors.greenAccent[500] + '40',
            borderWidth: 2,
            fill: true,
            tension: 0.4,
            yAxisID: 'y1',
            pointRadius: 0,
          },
        ],
      };
    } else {
      // 按季节分组
      const hours = data.overall.map(item => item.hour);
      const seasons = ['Spring', 'Summer', 'Autumn', 'Winter'];
      const seasonColors = [
        colors.greenAccent[500],
        colors.blueAccent[500],
        colors.redAccent[500],
        colors.blueAccent[500],
      ];
      
      const datasets = [];
      
      // 添加每个季节的密度曲线
      seasons.forEach((season, index) => {
        if (data.by_season[season]) {
          const densities = data.by_season[season].map(item => item.density);
          datasets.push({
            type: 'line',
            label: season,
            data: densities,
            borderColor: seasonColors[index],
            backgroundColor: seasonColors[index] + '40',
            borderWidth: 2,
            fill: false,
            tension: 0.4,
            pointRadius: 0,
            yAxisID: 'y1',
          });
        }
      });
      
      return {
        labels: hours,
        datasets: datasets,
      };
    }
  };

  const chartData = getChartData();

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: colors.grey[100],
        },
      },
      title: {
        display: true,
        text: viewMode === 'overall' 
          ? 'Hourly Departure Density (Overall)' 
          : 'Hourly Departure Density by Season',
        color: colors.grey[100],
        font: {
          size: 16,
        },
      },
      tooltip: {
        mode: 'index',
        intersect: false,
      },
    },
    scales: {
      x: {
        ticks: {
          color: colors.grey[100],
          stepSize: 1,
        },
        grid: {
          color: colors.grey[800],
        },
        title: {
          display: true,
          text: 'Hour of Day',
          color: colors.grey[100],
        },
      },
      y: {
        type: 'linear',
        display: viewMode === 'overall',
        position: 'left',
        ticks: {
          color: colors.grey[100],
        },
        grid: {
          color: colors.grey[800],
        },
        title: {
          display: true,
          text: 'Count',
          color: colors.grey[100],
        },
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        ticks: {
          color: colors.grey[100],
        },
        grid: {
          drawOnChartArea: false,
        },
        title: {
          display: true,
          text: 'Density',
          color: colors.grey[100],
        },
      },
    },
  };

  return (
    <Box height={isDashboard ? "250px" : "400px"} width="100%">
      {!isDashboard && (
        <Box mb={2} display="flex" justifyContent="center">
          <ToggleButtonGroup
            value={viewMode}
            exclusive
            onChange={(e, newMode) => {
              if (newMode !== null) setViewMode(newMode);
            }}
            aria-label="view mode"
            sx={{
              '& .MuiToggleButton-root': {
                color: colors.grey[100],
                borderColor: colors.grey[700],
                '&.Mui-selected': {
                  backgroundColor: colors.blueAccent[700],
                  color: colors.grey[100],
                },
              },
            }}
          >
            <ToggleButton value="overall" aria-label="overall">
              Overall
            </ToggleButton>
            <ToggleButton value="by_season" aria-label="by season">
              By Season
            </ToggleButton>
          </ToggleButtonGroup>
        </Box>
      )}
      <Chart type="bar" data={chartData} options={options} />
    </Box>
  );
};

export default HistogramChart;