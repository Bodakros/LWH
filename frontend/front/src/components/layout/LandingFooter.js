import React from 'react';
import { Link } from 'react-router-dom';
import { Facebook, Instagram, Linkedin, Mail, MapPin, Phone, Twitter } from 'lucide-react';

export default function LandingFooter() {
    return (
        <footer className="bg-primary text-white">
            <div className="container px-4 md:px-6 py-12 md:py-16">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                    <div>
                        <div className="flex items-center mb-4">
                            <div className="w-8 h-8 bg-white rounded flex items-center justify-center mr-2">
                                <span className="text-primary font-bold">LWH</span>
                            </div>
                            <span className="font-bold text-lg">Logistics Warehouse Hub</span>
                        </div>
                        <p className="text-gray-300 mb-4">
                            Сучасна система управління складами, яка з'єднує продавців та власників складів для оптимізації
                            логістичних процесів.
                        </p>
                        <div className="flex space-x-4">
                            <Link to="#" className="text-gray-300 hover:text-white">
                                <Facebook className="h-5 w-5" />
                                <span className="sr-only">Facebook</span>
                            </Link>
                            <Link to="#" className="text-gray-300 hover:text-white">
                                <Twitter className="h-5 w-5" />
                                <span className="sr-only">Twitter</span>
                            </Link>
                            <Link to="#" className="text-gray-300 hover:text-white">
                                <Instagram className="h-5 w-5" />
                                <span className="sr-only">Instagram</span>
                            </Link>
                            <Link to="#" className="text-gray-300 hover:text-white">
                                <Linkedin className="h-5 w-5" />
                                <span className="sr-only">LinkedIn</span>
                            </Link>
                        </div>
                    </div>

                    <div>
                        <h3 className="font-semibold text-lg mb-4">Компанія</h3>
                        <ul className="space-y-2">
                            <li>
                                <Link to="#" className="text-gray-300 hover:text-white">
                                    Про нас
                                </Link>
                            </li>
                            <li>
                                <Link to="#" className="text-gray-300 hover:text-white">
                                    Команда
                                </Link>
                            </li>
                            <li>
                                <Link to="#" className="text-gray-300 hover:text-white">
                                    Кар'єра
                                </Link>
                            </li>
                            <li>
                                <Link to="#" className="text-gray-300 hover:text-white">
                                    Блог
                                </Link>
                            </li>
                            <li>
                                <Link to="#" className="text-gray-300 hover:text-white">
                                    Партнерська програма
                                </Link>
                            </li>
                        </ul>
                    </div>

                    <div>
                        <h3 className="font-semibold text-lg mb-4">Продукт</h3>
                        <ul className="space-y-2">
                            <li>
                                <Link to="#" className="text-gray-300 hover:text-white">
                                    Можливості
                                </Link>
                            </li>
                            <li>
                                <Link to="#" className="text-gray-300 hover:text-white">
                                    Тарифи
                                </Link>
                            </li>
                            <li>
                                <Link to="#" className="text-gray-300 hover:text-white">
                                    Безпека
                                </Link>
                            </li>
                            <li>
                                <Link to="#" className="text-gray-300 hover:text-white">
                                    Документація
                                </Link>
                            </li>
                            <li>
                                <Link to="#" className="text-gray-300 hover:text-white">
                                    API
                                </Link>
                            </li>
                        </ul>
                    </div>

                    <div>
                        <h3 className="font-semibold text-lg mb-4">Контакти</h3>
                        <ul className="space-y-4">
                            <li className="flex">
                                <MapPin className="h-5 w-5 mr-2 flex-shrink-0" />
                                <span>вул. Хрещатик, 22, Київ, 01001, Україна</span>
                            </li>
                            <li className="flex">
                                <Phone className="h-5 w-5 mr-2 flex-shrink-0" />
                                <span>+38 (044) 123-45-67</span>
                            </li>
                            <li className="flex">
                                <Mail className="h-5 w-5 mr-2 flex-shrink-0" />
                                <span>info@lwh.ua</span>
                            </li>
                        </ul>
                    </div>
                </div>

                <div className="border-t border-gray-700 mt-12 pt-8 flex flex-col md:flex-row justify-between items-center">
                    <p className="text-gray-300">© 2025 LWH. Всі права захищені.</p>
                    <div className="flex space-x-6 mt-4 md:mt-0">
                        <Link to="#" className="text-gray-300 hover:text-white text-sm">
                            Умови використання
                        </Link>
                        <Link to="#" className="text-gray-300 hover:text-white text-sm">
                            Політика конфіденційності
                        </Link>
                        <Link to="#" className="text-gray-300 hover:text-white text-sm">
                            Правові положення
                        </Link>
                    </div>
                </div>
            </div>
        </footer>
    );
}