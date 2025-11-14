import { Box } from "@mui/material";
import Header from "../../components/Header";
import HistogramChart from "../../components/HistogramChart";
import PredTest from "../../components/PredTest";

const Bar = () => {
  return (
    <Box m="20px">
      <Header title="Histogram Chart" subtitle="Overall statistics of hourly departure frequency and statistics by season" />
      <Box height="75vh">
        <HistogramChart />
        <PredTest />
      </Box>
    </Box>
  );
};

export default Bar;
