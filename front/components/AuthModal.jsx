import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Stack,
  Typography,
  Checkbox,
  FormControlLabel,
} from '@mui/material';
import { loginUser, registerUser } from '../services/callsToBackend';
import useAuth from '../hooks/useAuth';

export default function AuthModal({ open, onClose, mode = 'login' }) {
  const isLogin = mode === 'login';

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [pass1, setPass1] = useState('');
  const [pass2, setPass2] = useState('');
  const [keepLogged, setKeepLogged] = useState(false);

  const [touched, setTouched] = useState(false);
  const { login } = useAuth();

  const handleClose = () => {
    document.activeElement?.blur();
    onClose();
    resetFields();
  };

  const resetFields = () => {
    setName('');
    setEmail('');
    setPass1('');
    setPass2('');
    setTouched(false);
  };

  const validatePassword = (password) => {
    const regex = /^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+[\]{};':"\\|,.<>/?]).{8,}$/;
    return regex.test(password);
  };

  const passwordIsValid = validatePassword(pass1);
  const passwordsMatch = pass1 === pass2;

  const handleSubmit = async () => {
    setTouched(true);
  
    if (isLogin) {
      try {
        const data = await loginUser(email, pass1, keepLogged);
        login(data.access_token, data.user_id);
        handleClose();
        window.location.reload();
      } catch (err) {
        alert(err.message);
      }
    } else {
      if (!passwordIsValid || !passwordsMatch) return;
  
      try {
        const data = await registerUser(name, email, pass1);
        alert('Registro completado. Ahora puedes iniciar sesión.');
        handleClose();
      } catch (err) {
        alert(err.message);
      }
    }
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
            <TextField
              label="Nombre"
              variant="outlined"
              fullWidth
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          )}

          <TextField
            label="Email"
            variant="outlined"
            type="email"
            fullWidth
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <TextField
            label="Contraseña"
            variant="outlined"
            type="password"
            fullWidth
            value={pass1}
            onChange={(e) => setPass1(e.target.value)}
            error={!isLogin && touched && !passwordIsValid}
            helperText={
              !isLogin && touched && !passwordIsValid
                ? 'La contraseña debe tener al menos 8 caracteres, una mayúscula, un número y un símbolo.'
                : ''
            }
          />

          {!isLogin && (
            <TextField
              label="Repetir contraseña"
              variant="outlined"
              type="password"
              fullWidth
              value={pass2}
              onChange={(e) => setPass2(e.target.value)}
              error={touched && !passwordsMatch}
              helperText={
                touched && !passwordsMatch ? 'Las contraseñas no coinciden.' : ''
              }
            />
          )}
          {isLogin && (
            <FormControlLabel
              control={<Checkbox checked={keepLogged} onChange={(e) => setKeepLogged(e.target.checked)} />}
              label="Mantener sesión iniciada"
            />
          )}
          {!isLogin && (
            <Typography variant="caption" color="text.secondary">
              Al registrarte, aceptas nuestros términos y condiciones.
            </Typography>
          )}
        </Stack>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose}>Cancelar</Button>
        <Button variant="contained" onClick={handleSubmit}>
          {isLogin ? 'Entrar' : 'Registrarse'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
