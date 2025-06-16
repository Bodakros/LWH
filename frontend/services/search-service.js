import api from '../lib/api/client';
import { endpoints } from '../lib/api/endpoints';

/**
 * Service for search functionality
 */
const searchService = {
    /**
     * Search products with multiple filters
     * @param {Object} params - search parameters
     * @param {string} params.search - search query
     * @param {number} params.category - category ID filter
     * @param {number} params.page - page number
     * @param {number} params.page_size - items per page
     * @param {string} params.sort - sort field
     * @param {number} params.min_price - minimum price filter
     * @param {number} params.max_price - maximum price filter
     * @param {boolean} params.in_stock - in stock filter
     * @param {number} params.min_rating - minimum rating filter
     * @param {Array<string>} params.brands - list of brands to filter by
     * @param {string} params.seller - seller ID filter
     * @returns {Promise} - promise with search results
     */
    searchProducts: async (params = {}) => {
        const queryParams = new URLSearchParams();

        // Add parameters to the request
        if (params.search) queryParams.append('search', params.search);
        if (params.category) queryParams.append('category', params.category);
        if (params.page) queryParams.append('page', params.page);
        if (params.page_size) queryParams.append('page_size', params.page_size);
        if (params.sort) queryParams.append('sort', params.sort);
        if (params.min_price) queryParams.append('min_price', params.min_price);
        if (params.max_price) queryParams.append('max_price', params.max_price);
        if (params.in_stock !== undefined) queryParams.append('in_stock', params.in_stock);
        if (params.min_rating) queryParams.append('min_rating', params.min_rating);
        if (params.seller) queryParams.append('seller', params.seller);

        // Handle brands
        if (params.brands && params.brands.length > 0) {
            params.brands.forEach(brand => {
                queryParams.append('brand', brand);
            });
        }

        return api.get(`${endpoints.search.products}?${queryParams.toString()}`);
    }
};

export default searchService;