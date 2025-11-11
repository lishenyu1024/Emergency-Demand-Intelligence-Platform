import { Box } from "@mui/material";
import Header from "../../components/Header";
import BarChart from "../../components/BarChart";
import HistogramChart from "../../components/HistogramChart";


const Bar = () => {
  return (
    <Box m="20px">
<<<<<<< HEAD
      <Header title="Histogram Chart" subtitle="Overall statistics of hourly departure frequency and statistics by season" />
=======
      <Header title="Bar Chart" subtitle="Simple Bar Chart" />
>>>>>>> refs/remotes/origin/main
      <Box height="75vh">
        <HistogramChart />
      </Box>
    </Box>
  );
};

export default Bar;
