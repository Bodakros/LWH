// services/product-service.js
import api from '../lib/api/client';
import { endpoints } from '../lib/api/endpoints';

export const productService = {
    /**
     * Отримання списку продуктів з можливістю фільтрації та пагінації
     * @param {Object} params - параметри запиту
     * @param {string} params.search - пошуковий запит
     * @param {number} params.category - ID категорії
     * @param {number} params.page - номер сторінки
     * @param {number} params.page_size - кількість елементів на сторінці
     * @param {string} params.sort - поле для сортування
     * @param {[number, number]} params.price_range - діапазон цін [min, max]
     * @param {boolean} params.in_stock - фільтр по наявності
     * @param {number} params.min_rating - мінімальний рейтинг
     * @param {string} params.seller - ID продавця
     * @returns {Promise} - проміс з результатами запиту
     */
    getProducts: async (params = {}) => {
        const queryParams = new URLSearchParams();

        // Додавання параметрів до запиту
        if (params.search) queryParams.append('search', params.search);
        if (params.category) queryParams.append('category', params.category);
        if (params.page) queryParams.append('page', params.page);
        if (params.page_size) queryParams.append('page_size', params.page_size);
        if (params.sort) queryParams.append('sort', params.sort);
        if (params.in_stock !== undefined) queryParams.append('in_stock', params.in_stock);
        if (params.min_rating) queryParams.append('min_rating', params.min_rating);
        if (params.seller) queryParams.append('seller', params.seller);

        // Обробка діапазону цін
        if (params.price_range && params.price_range.length === 2) {
            queryParams.append('min_price', params.price_range[0]);
            queryParams.append('max_price', params.price_range[1]);
        }

        return api.get(`${endpoints.search.products}?${queryParams.toString()}`);
    },

    /**
     * Отримання списку категорій продуктів
     * @param {Object} params - параметри запиту
     * @param {number} params.parent - ID батьківської категорії
     * @returns {Promise} - проміс з результатами запиту
     */
    getCategories: async (params = {}) => {
        const queryParams = new URLSearchParams();

        if (params.parent) queryParams.append('parent', params.parent);

        return api.get(`${endpoints.products.categories}?${queryParams.toString()}`);
    },

    /**
     * Отримання деталей продукту за ID
     * @param {number} id - ID продукту
     * @returns {Promise} - проміс з результатами запиту
     */
    getProductById: async (id) => {
        return api.get(`${endpoints.products.details.replace(':id', id)}`);
    },

    /**
     * Отримання рекомендованих продуктів
     * @param {number} limit - кількість рекомендацій
     * @returns {Promise} - проміс з результатами запиту
     */
    getRecommendedProducts: async (limit = 4) => {
        return api.get(`${endpoints.products.recommended}?limit=${limit}`);
    }
};

export default productService;