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

const navLinks = [
  { label: 'Home', path: '/' },
  { label: 'About', path: '/about' },
  { label: 'Contact', path: '/contact' },
];

export default function Navbar() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [drawerOpen, setDrawerOpen] = useState(false);

  const toggleDrawer = (open) => () => {
    setDrawerOpen(open);
  };

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
          <ListItem button onClick={() => console.log("Abrir login")}>
            <ListItemText primary="Login" />
          </ListItem>
          <ListItem button onClick={() => console.log("Abrir register")}>
            <ListItemText primary="Register" />
          </ListItem>
        </List>
      </Box>
    </Drawer>
  );

  return (
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
            <Button color="inherit" onClick={() => console.log('Abrir login')}>Login</Button>
            <Button color="inherit" onClick={() => console.log('Abrir register')}>Register</Button>
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
}
