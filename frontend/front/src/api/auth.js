import { api } from './utils';

// Авторизація користувача
export const loginUser = async (username, password) => {
    try {
        const response = await api.post('/users/token/', { username, password });
        const { access, refresh } = response.data;

        // Зберігаємо токени
        localStorage.setItem('token', access);
        localStorage.setItem('refreshToken', refresh);

        return { success: true, data: response.data };
    } catch (error) {
        return {
            success: false,
            error: error.response?.data?.detail || 'Помилка під час входу'
        };
    }
};

// Реєстрація користувача
export const registerUser = async (userData) => {
    try {
        const response = await api.post('/users/register/', userData);
        return { success: true, data: response.data };
    } catch (error) {
        return {
            success: false,
            error: error.response?.data || 'Помилка під час реєстрації'
        };
    }
};

// Отримання профілю користувача
export const getUserProfile = async () => {
    try {
        const response = await api.get('/users/profile/');
        return { success: true, data: response.data };
    } catch (error) {
        return {
            success: false,
            error: error.response?.data || 'Помилка отримання профілю'
        };
    }
};

// Вихід з системи
export const logoutUser = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
};