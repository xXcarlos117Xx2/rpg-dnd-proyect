import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemText,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import { Link as RouterLink } from 'react-router-dom';
import AuthModal from './AuthModal';
import useAuth from '../hooks/useAuth';

const navLinks = [
  { label: 'Home', path: '/' },
  { label: 'About', path: '/about' },
  { label: 'Contact', path: '/contact' },
];

export default function Navbar() {
  const [authMode, setAuthMode] = useState(null);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [drawerOpen, setDrawerOpen] = useState(false);

  const openAuthModal = (mode) => setAuthMode(mode);
  const closeAuthModal = () => setAuthMode(null);

  const toggleDrawer = (open) => () => {
    setDrawerOpen(open);
  };

  const { isLoggedIn, logout } = useAuth();

  const drawer = (
    <Drawer anchor="left" open={drawerOpen} onClose={toggleDrawer(false)}>
      <Box sx={{ width: 250 }} role="presentation" onClick={toggleDrawer(false)}>
        <List>
          {navLinks.map((item) => (
            <ListItem
              button
              key={item.path}
              component={RouterLink}
              to={item.path}
              sx={{ textDecoration: 'none', color: 'inherit' }}
            >
              <ListItemText primary={item.label} />
            </ListItem>
          ))}
          {isLoggedIn ? (
            <>
              <ListItem button component={RouterLink} to="/profile" onClick={() => setDrawerOpen(false)}>
                <ListItemText primary="Profile" />
              </ListItem>
              <ListItem button onClick={() => { logout(); setDrawerOpen(false); }}>
                <ListItemText primary="Logout" />
              </ListItem>
            </>
          ) : (
            <>
              <ListItem button onClick={() => { openAuthModal('login'); setDrawerOpen(false); }}>
                <ListItemText primary="Login" />
              </ListItem>
              <ListItem button onClick={() => { openAuthModal('register'); setDrawerOpen(false); }}>
                <ListItemText primary="Register" />
              </ListItem>
            </>
          )}
        </List>
      </Box>
    </Drawer>
  );

  return (
    <>
      <AppBar position="static" color="primary" enableColorOnDark>
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          <Typography
            variant="h6"
            component={RouterLink}
            to="/"
            sx={{ textDecoration: 'none', color: 'inherit' }}
          >
            MyApp
          </Typography>

          {isMobile ? (
            <>
              <IconButton color="inherit" edge="end" onClick={toggleDrawer(true)}>
                <MenuIcon />
              </IconButton>
              {drawer}
            </>
          ) : (
            <Box>
              {navLinks.map((item) => (
                <Button
                  key={item.path}
                  component={RouterLink}
                  to={item.path}
                  color="inherit"
                >
                  {item.label}
                </Button>
              ))}
              {isLoggedIn ? (
                <>
                  <Button component={RouterLink} to="/profile" color="inherit">Profile</Button>
                  <Button color="inherit" onClick={logout}>Logout</Button>
                </>
              ) : (
                <>
                  <Button color="inherit" onClick={() => openAuthModal('login')}>Login</Button>
                  <Button color="inherit" onClick={() => openAuthModal('register')}>Register</Button>
                </>
              )}
            </Box>
          )}
        </Toolbar>
      </AppBar>
      <AuthModal open={Boolean(authMode)} onClose={closeAuthModal} mode={authMode} />
    </>
  );


}
