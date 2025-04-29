import axios from 'axios';

const API_URL = '/api/v1';

// Створюємо екземпляр axios з базовими налаштуваннями
export const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Додаємо інтерцептор для додавання токену авторизації
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Інтерцептор для обробки помилок відповіді
api.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        // Обробка помилки автентифікації
        if (error.response && error.response.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);