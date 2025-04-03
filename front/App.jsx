import { ThemeProvider, CssBaseline } from '@mui/material';
import { BrowserRouter } from 'react-router-dom';
import { StoreProvider } from './hooks/useGlobalReducer';
import RoutesApp from './routes';
import useAppTheme from './hooks/useAppTheme';

export default function App() {
  return (
    <StoreProvider>
      <AppWithTheme />
    </StoreProvider>
  );
}

function AppWithTheme() {
  const { theme } = useAppTheme();

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <RoutesApp />
      </BrowserRouter>
    </ThemeProvider>
  );
}
