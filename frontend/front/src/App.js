import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import LandingPage from './pages/landing/LandingPage';

function App() {
    return (
        <AuthProvider>
            <Routes>
                <Route path="/" element={<LandingPage />} />
                {/* Тут будуть інші маршрути */}
            </Routes>
        </AuthProvider>
    );
}

export default App;