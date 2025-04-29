import React, { createContext, useState, useEffect, useContext } from 'react';
import { getUserProfile, loginUser, logoutUser, registerUser } from '../api/auth';

// Створюємо контекст
const AuthContext = createContext(null);

// Провайдер контексту
export const AuthProvider = ({ children }) => {
    const [currentUser, setCurrentUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Отримуємо інформацію про користувача при завантаженні
    useEffect(() => {
        const fetchUserData = async () => {
            const token = localStorage.getItem('token');

            if (token) {
                const { success, data, error } = await getUserProfile();

                if (success) {
                    setCurrentUser(data);
                } else {
                    setError(error);
                    localStorage.removeItem('token');
                    localStorage.removeItem('refreshToken');
                }
            }

            setLoading(false);
        };

        fetchUserData();
    }, []);

    // Функція входу
    const login = async (username, password) => {
        setLoading(true);
        setError(null);

        const { success, data, error } = await loginUser(username, password);

        if (success) {
            const profileResult = await getUserProfile();
            if (profileResult.success) {
                setCurrentUser(profileResult.data);
            } else {
                setError(profileResult.error);
            }
        } else {
            setError(error);
        }

        setLoading(false);
        return { success, error };
    };

    // Функція реєстрації
    const register = async (userData) => {
        setLoading(true);
        setError(null);

        const result = await registerUser(userData);
        setLoading(false);

        if (result.success) {
            return { success: true };
        } else {
            setError(result.error);
            return { success: false, error: result.error };
        }
    };

    // Функція виходу
    const logout = () => {
        logoutUser();
        setCurrentUser(null);
    };

    // Перевірка ролі користувача
    const isSeller = currentUser?.is_seller || false;
    const isOwner = currentUser?.is_owner || false;

    const value = {
        currentUser,
        loading,
        error,
        login,
        register,
        logout,
        isSeller,
        isOwner,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Хук для використання контексту
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth має використовуватися всередині AuthProvider');
    }
    return context;
};