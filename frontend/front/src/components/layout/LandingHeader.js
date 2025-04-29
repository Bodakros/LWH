import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

export default function LandingHeader() {
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const { currentUser, logout } = useAuth();

    return (
        <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
            <div className="container mx-auto px-4 md:px-6">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <Link to="/" className="flex items-center">
                        <div className="w-8 h-8 bg-primary rounded flex items-center justify-center mr-2">
                            <span className="text-white font-bold">LWH</span>
                        </div>
                        <span className="font-bold text-lg text-primary">Logistics Warehouse Hub</span>
                    </Link>

                    {/* Desktop Navigation */}
                    <nav className="hidden md:flex items-center space-x-6">
                        <Link to="/#features" className="text-gray-600 hover:text-primary">
                            Можливості
                        </Link>
                        <Link to="/#how-it-works" className="text-gray-600 hover:text-primary">
                            Як це працює
                        </Link>
                        <Link to="/#pricing" className="text-gray-600 hover:text-primary">
                            Тарифи
                        </Link>
                        <Link to="/#contact" className="text-gray-600 hover:text-primary">
                            Контакти
                        </Link>
                    </nav>

                    {/* Desktop CTA */}
                    <div className="hidden md:flex items-center space-x-4">
                        {currentUser ? (
                            <>
                                <Link to="/dashboard">
                                    <button className="btn btn-outline">Мій кабінет</button>
                                </Link>
                                <button onClick={logout} className="btn btn-primary">
                                    Вийти
                                </button>
                            </>
                        ) : (
                            <>
                                <Link to="/login">
                                    <button className="btn btn-outline">Увійти</button>
                                </Link>
                                <Link to="/register">
                                    <button className="btn btn-primary">Реєстрація</button>
                                </Link>
                            </>
                        )}
                    </div>

                    {/* Mobile Menu Button */}
                    <button
                        className="md:hidden text-gray-600"
                        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                        aria-label={mobileMenuOpen ? "Закрити меню" : "Відкрити меню"}
                    >
                        {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
                    </button>
                </div>
            </div>

            {/* Mobile Menu */}
            {mobileMenuOpen && (
                <div className="md:hidden bg-white border-b border-gray-200">
                    <div className="container mx-auto px-4 py-4 space-y-4">
                        <nav className="flex flex-col space-y-4">
                            <Link
                                to="/#features"
                                className="text-gray-600 hover:text-primary"
                                onClick={() => setMobileMenuOpen(false)}
                            >
                                Можливості
                            </Link>
                            <Link
                                to="/#how-it-works"
                                className="text-gray-600 hover:text-primary"
                                onClick={() => setMobileMenuOpen(false)}
                            >
                                Як це працює
                            </Link>
                            <Link
                                to="/#pricing"
                                className="text-gray-600 hover:text-primary"
                                onClick={() => setMobileMenuOpen(false)}
                            >
                                Тарифи
                            </Link>
                            <Link
                                to="/#contact"
                                className="text-gray-600 hover:text-primary"
                                onClick={() => setMobileMenuOpen(false)}
                            >
                                Контакти
                            </Link>
                        </nav>
                        <div className="flex flex-col space-y-2">
                            {currentUser ? (
                                <>
                                    <Link to="/dashboard" onClick={() => setMobileMenuOpen(false)}>
                                        <button className="btn btn-outline w-full">Мій кабінет</button>
                                    </Link>
                                    <button
                                        onClick={() => {
                                            logout();
                                            setMobileMenuOpen(false);
                                        }}
                                        className="btn btn-primary w-full"
                                    >
                                        Вийти
                                    </button>
                                </>
                            ) : (
                                <>
                                    <Link to="/login" onClick={() => setMobileMenuOpen(false)}>
                                        <button className="btn btn-outline w-full">Увійти</button>
                                    </Link>
                                    <Link to="/register" onClick={() => setMobileMenuOpen(false)}>
                                        <button className="btn btn-primary w-full">Реєстрація</button>
                                    </Link>
                                </>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </header>
    );
}