import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Stack,
  Typography,
} from '@mui/material';

export default function AuthModal({ open, onClose, mode = 'login' }) {
  const isLogin = mode === 'login';

  const handleClose = () => {
    document.activeElement?.blur();
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      fullWidth
      maxWidth="sm"
      disableEnforceFocus
    >
      <DialogTitle>{isLogin ? 'Iniciar sesión' : 'Registrarse'}</DialogTitle>

      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1 }}>
          {!isLogin && (
            <TextField label="Nombre" variant="outlined" fullWidth />
          )}
          <TextField label="Email" variant="outlined" type="email" fullWidth />
          <TextField label="Contraseña" variant="outlined" type="password" fullWidth />
          {!isLogin && (
            <Typography variant="caption" color="text.secondary">
              Al registrarte, aceptas nuestros términos y condiciones.
            </Typography>
          )}
        </Stack>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose}>Cancelar</Button>
        <Button variant="contained" onClick={() => console.log(`${mode} enviado`)}>
          {isLogin ? 'Entrar' : 'Registrarse'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
