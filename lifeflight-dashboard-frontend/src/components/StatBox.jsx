import { Box, Typography, useTheme } from "@mui/material";
import { tokens } from "../theme";
import ProgressCircle from "./ProgressCircle";

const StatBox = ({ title, subtitle, icon, progress, increase }) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

  return (
    <Box width="100%" m="0 30px">
      <Box display="flex" alignItems="center" mb="8px">
        {icon && (
          <Box
            sx={{
              mr: "8px",
              display: "flex",
              alignItems: "center",
            }}
          >
            {icon}
          </Box>
        )}
        <Typography
          variant="h5"
          fontWeight="600"
          sx={{ 
            color: colors.grey[100],
            fontSize: "1.5rem"
          }}
        >
          {subtitle}
        </Typography>
      </Box>
      <Typography 
        variant="body1" 
        sx={{ 
          color: colors.grey[400],
          fontWeight: 400,
          fontSize: "0.875rem"
        }}
      >
        {title}
      </Typography>
    </Box>
  );
};

export default StatBox;
