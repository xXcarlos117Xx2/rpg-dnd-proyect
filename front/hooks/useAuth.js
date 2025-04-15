import { useCallback, useEffect, useState } from 'react';
import { logoutUser } from '../services/callsToBackend';

export default function useAuth() {
    const [accessToken, setAccessToken] = useState(localStorage.getItem('access_token'));
    const [userId, setUserId] = useState(localStorage.getItem('user_id'));

    const isLoggedIn = !!accessToken;
    const login = (token, userId) => {
        localStorage.setItem('access_token', token);
        localStorage.setItem('user_id', userId);
        setAccessToken(token);
        setUserId(userId);
    };
    
    const logout = useCallback(async () => {
        const token = localStorage.getItem('access_token');
        

        if (token) {
            try {
                await logoutUser(token); // ⬅️ llamada al backend
            } catch (err) {
                console.warn('No se pudo notificar al backend:', err.message);
            }
        }

        localStorage.removeItem('access_token');
        localStorage.removeItem('user_id');
        setAccessToken(null);
        setUserId(null);
        window.location.reload(); // 🔄 refresca navbar y UI
    }, []);

    useEffect(() => {
        const token = localStorage.getItem('access_token');
        const uid = localStorage.getItem('user_id');
        setAccessToken(token);
        setUserId(uid);
    }, []);

    return {
        isLoggedIn,
        accessToken,
        userId,
        login,
        logout,
    };
}
