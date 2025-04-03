import { createTheme } from '@mui/material/styles';

// Theme provicer MUI
export const themes = {
  light: createTheme({
    palette: {
      mode: 'light',
      primary: { main: '#1976d2' },
      secondary: { main: '#f50057' },
      background: { default: '#f4f6f8', paper: '#ffffff' },
    },
  }),
  dark: createTheme({
    palette: {
      mode: 'dark',
      primary: { main: '#90caf9' },
      secondary: { main: '#f48fb1' },
      background: { default: '#121212', paper: '#1e1e1e' },
    },
  }),
  forest: createTheme({
    palette: {
      mode: 'dark',
      primary: { main: '#4caf50' },
      background: { default: '#1b2e1b', paper: '#2e4230' },
    },
  }),
};
