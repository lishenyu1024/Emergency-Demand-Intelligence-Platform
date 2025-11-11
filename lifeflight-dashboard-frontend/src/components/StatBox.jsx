import { Box, Typography, useTheme } from "@mui/material";
import { tokens } from "../theme";
import ProgressCircle from "./ProgressCircle";

const StatBox = ({ title, subtitle, icon, progress, increase }) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

  return (
    <Box width="100%" m="0 30px">
<<<<<<< HEAD
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
=======
      <Box display="flex" justifyContent="space-between">
        <Box>
          {icon}
          <Typography
            variant="h4"
            fontWeight="bold"
            sx={{ color: colors.grey[100] }}
          >
            {title}
          </Typography>
        </Box>
        <Box>
          <ProgressCircle progress={progress} />
        </Box>
      </Box>
      <Box display="flex" justifyContent="space-between" mt="2px">
        <Typography variant="h5" sx={{ color: colors.greenAccent[500] }}>
          {subtitle}
        </Typography>
        <Typography
          variant="h5"
          fontStyle="italic"
          sx={{ color: colors.greenAccent[600] }}
        >
          {increase}
        </Typography>
      </Box>
>>>>>>> refs/remotes/origin/main
    </Box>
  );
};

export default StatBox;
