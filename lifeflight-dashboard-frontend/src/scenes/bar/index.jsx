import { Box } from "@mui/material";
import Header from "../../components/Header";
import BarChart from "../../components/BarChart";
import HistogramChart from "../../components/HistogramChart";


const Bar = () => {
  return (
    <Box m="20px">
      <Header title="Bar Chart" subtitle="Simple Bar Chart" />
      <Box height="75vh">
        <HistogramChart />
      </Box>
    </Box>
  );
};

export default Bar;
