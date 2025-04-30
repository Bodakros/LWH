// services/product-service.js
import api from '../lib/api/client';
import { endpoints } from '../lib/api/endpoints';

/**
 * Service for interacting with the products API
 */
export const productService = {
    /**
     * Get products list with filtering and pagination
     * @param {Object} params - request parameters
     * @param {string} params.search - search query
     * @param {number} params.category - category ID
     * @param {number} params.page - page number
     * @param {number} params.page_size - items per page
     * @param {string} params.sort - sort field
     * @param {[number, number]} params.price_range - price range [min, max]
     * @param {boolean} params.in_stock - in stock filter
     * @param {number} params.min_rating - minimum rating
     * @param {Array<string>} params.brands - list of brands
     * @param {string} params.seller - seller ID
     * @returns {Promise} - promise with request results
     */
    getProducts: async (params = {}) => {
        const queryParams = new URLSearchParams();

        // Add parameters to the request
        if (params.search) queryParams.append('search', params.search);
        if (params.category) queryParams.append('category', params.category);
        if (params.page) queryParams.append('page', params.page);
        if (params.page_size) queryParams.append('page_size', params.page_size);
        if (params.sort) queryParams.append('sort', params.sort);
        if (params.in_stock !== undefined) queryParams.append('in_stock', params.in_stock);
        if (params.min_rating) queryParams.append('min_rating', params.min_rating);
        if (params.seller) queryParams.append('seller', params.seller);

        // Handle price range
        if (params.price_range && params.price_range.length === 2) {
            queryParams.append('min_price', params.price_range[0]);
            queryParams.append('max_price', params.price_range[1]);
        }

        // Handle brands
        if (params.brands && params.brands.length > 0) {
            params.brands.forEach(brand => {
                queryParams.append('brand', brand);
            });
        }

        return api.get(`${endpoints.search.products}?${queryParams.toString()}`);
    },

    /**
     * Get product categories list
     * @param {Object} params - request parameters
     * @param {number} params.parent - parent category ID
     * @returns {Promise} - promise with request results
     */
    getCategories: async (params = {}) => {
        const queryParams = new URLSearchParams();

        if (params.parent) queryParams.append('parent', params.parent);

        return api.get(`${endpoints.products.categories}?${queryParams.toString()}`);
    },

    /**
     * Get product details by ID
     * @param {number} id - product ID
     * @returns {Promise} - promise with request results
     */
    getProductById: async (id) => {
        return api.get(`${endpoints.products.details.replace(':id', id)}`);
    },

    /**
     * Get recommended products
     * @param {number} productId - product ID to get recommendations for
     * @param {number} limit - number of recommendations
     * @returns {Promise} - promise with request results
     */
    getRecommendedProducts: async (productId = null, limit = 4) => {
        const queryParams = new URLSearchParams();

        if (productId) queryParams.append('product_id', productId);
        if (limit) queryParams.append('limit', limit);

        return api.get(`${endpoints.products.recommended}?${queryParams.toString()}`);
    },

    /**
     * Get popular products
     * @param {number} limit - number of products
     * @returns {Promise} - promise with request results
     */
    getPopularProducts: async (limit = 4) => {
        return api.get(`${endpoints.products.popular}?limit=${limit}`);
    },

    /**
     * Get product attributes
     * @param {number} productId - product ID
     * @returns {Promise} - promise with request results
     */
    getProductAttributes: async (productId) => {
        return api.get(`${endpoints.products.attributes.replace(':id', productId)}`);
    },

    /**
     * Get related products
     * @param {number} productId - product ID
     * @param {number} limit - number of products
     * @returns {Promise} - promise with request results
     */
    getRelatedProducts: async (productId, limit = 4) => {
        return api.get(`${endpoints.products.related.replace(':id', productId)}?limit=${limit}`);
    }
};

export default productService;