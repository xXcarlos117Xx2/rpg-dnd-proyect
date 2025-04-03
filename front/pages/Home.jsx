import React from 'react';
import { Typography, FormControl, InputLabel, Select, MenuItem, Box } from '@mui/material';
import useAppTheme from '../hooks/useAppTheme';

const themeOptions = ['light', 'dark', 'forest'];

export default function Home() {
  const { themeName, setThemeName } = useAppTheme();

  const handleChange = (event) => {
    setThemeName(event.target.value);
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h4" gutterBottom>
        Welcome to the Home Page
      </Typography>

      <FormControl fullWidth sx={{ maxWidth: 300 }}>
        <InputLabel id="theme-select-label">Select Theme</InputLabel>
        <Select
          labelId="theme-select-label"
          value={themeName}
          label="Select Theme"
          onChange={handleChange}
        >
          {themeOptions.map((name) => (
            <MenuItem key={name} value={name}>
              {name.charAt(0).toUpperCase() + name.slice(1)}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </Box>
  );
}
