import { Box } from "@mui/material";
import Header from "../../components/Header";
import HeatMap from "../../components/HeatMap";
export default function ScenarioModeling() {
  return (
    <Box m="20px">
      <Header title="Scenario Modeling" subtitle="Scenario Modeling" />
      <h1>Pick up cities HeatMap</h1>
      <Box height="75vh">
        <HeatMap />
      </Box>
    </Box>
  );
}