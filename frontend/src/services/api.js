import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL ? `${process.env.REACT_APP_BACKEND_URL}/api` : 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_URL,
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Interceptor para manejar errores 401 (no autenticado)
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            // No redirigir automáticamente para evitar bucles, 
            // dejar que el componente o AuthContext maneje el estado
            console.warn('Sesión expirada o invalida');
        }
        return Promise.reject(error);
    }
);

export default api;
