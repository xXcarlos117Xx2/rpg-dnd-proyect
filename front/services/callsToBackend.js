const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000/api';

export async function registerUser(username, email, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password }),
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Error al registrarse');
        return data;
    } catch (err) {
        throw err;
    }
}

export async function loginUser(user, password, no_expire = false) {
    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user, password, no_expire }),
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Error al iniciar sesión');
        return data;
    } catch (err) {
        throw err;
    }
}

export async function logoutUser(token) {
    try {
      const response = await fetch(`${API_BASE_URL}/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
  
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Error al cerrar sesión');
      return data;
    } catch (err) {
      throw err;
    }
  }
  