import Header from "../../components/Header";
import { Box } from "@mui/material";
import HistogramChart from "../../components/HistogramChart";
import PredTest from "../../components/PredTest";
import LineChart from "../../components/LineChart";



export default function DemandForecasting() { 
  return (
    <Box m="20px">
      <Header title="Demand Forecasting" subtitle="Demand Forecasting" />

      <Box height="75vh">
        <HistogramChart />
      </Box>

      <Box height="25vh">
        <PredTest />
      </Box>

      <Box height="75vh">
        <LineChart />
      </Box>
    </Box>
  );
}