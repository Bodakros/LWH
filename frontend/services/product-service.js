import api from '../lib/api/client';
import { endpoints, getUrlWithParams } from '../lib/api/endpoints';

/**
 * Service for interacting with the products API
 */
const productService = {
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
     * Get category details by ID
     * @param {number} id - category ID
     * @returns {Promise} - promise with request results
     */
    getCategoryById: async (id) => {
        return api.get(getUrlWithParams(endpoints.products.categoryDetail, { pk: id }));
    },

    /**
     * Get product details by ID
     * @param {number} id - product ID
     * @returns {Promise} - promise with request results
     */
    getProductById: async (id) => {
        return api.get(getUrlWithParams(endpoints.products.details, { pk: id }));
    },

    /**
     * Get product images
     * @param {number} productId - product ID
     * @returns {Promise} - promise with request results
     */
    getProductImages: async (productId) => {
        return api.get(getUrlWithParams(endpoints.products.productImages, { product_id: productId }));
    },

    /**
     * Get product attributes
     * @param {number} productId - product ID
     * @returns {Promise} - promise with request results
     */
    getProductAttributes: async (productId) => {
        return api.get(getUrlWithParams(endpoints.products.productAttributes, { product_id: productId }));
    },

    /**
     * Create a product
     * @param {Object} productData - Product data to create
     * @returns {Promise} - promise with request results
     */
    createProduct: async (productData) => {
        return api.post(endpoints.products.list, productData);
    },

    /**
     * Update a product
     * @param {number} id - product ID
     * @param {Object} productData - Product data to update
     * @returns {Promise} - promise with request results
     */
    updateProduct: async (id, productData) => {
        return api.put(getUrlWithParams(endpoints.products.details, { pk: id }), productData);
    },

    /**
     * Delete a product
     * @param {number} id - product ID
     * @returns {Promise} - promise with request results
     */
    deleteProduct: async (id) => {
        return api.delete(getUrlWithParams(endpoints.products.details, { pk: id }));
    },

    /**
     * Upload product image
     * @param {number} productId - product ID
     * @param {FormData} formData - Form data with image file
     * @param {Function} onProgress - Progress callback
     * @returns {Promise} - promise with request results
     */
    uploadProductImage: async (productId, formData, onProgress = () => {}) => {
        return api.upload(
            getUrlWithParams(endpoints.products.productImages, { product_id: productId }),
            formData,
            onProgress
        );
    },

    /**
     * Reorder product images
     * @param {number} productId - product ID
     * @param {Array} imageOrders - Array of { image_id, order } objects
     * @returns {Promise} - promise with request results
     */
    reorderProductImages: async (productId, imageOrders) => {
        return api.post(
            getUrlWithParams(endpoints.products.reorderProductImages, { product_id: productId }),
            { image_orders: imageOrders }
        );
    },

    /**
     * Calculate product taxes
     * @param {number} id - product ID
     * @param {Object} params - Tax calculation parameters
     * @param {number} params.quantity - Product quantity
     * @param {boolean} params.breakdown - Whether to include detailed breakdown
     * @returns {Promise} - promise with request results
     */
    calculateProductTaxes: async (id, params = {}) => {
        const queryParams = new URLSearchParams();

        if (params.quantity) queryParams.append('quantity', params.quantity);
        if (params.breakdown !== undefined) queryParams.append('breakdown', params.breakdown);

        return api.get(`${getUrlWithParams(endpoints.products.taxes, { pk: id })}?${queryParams.toString()}`);
    },

    /**
     * Get tax types
     * @returns {Promise} - promise with request results
     */
    getTaxTypes: async () => {
        return api.get(endpoints.products.taxTypes);
    },

    /**
     * Get tax rates
     * @param {Object} params - request parameters
     * @param {number} params.tax_type - tax type ID
     * @returns {Promise} - promise with request results
     */
    getTaxRates: async (params = {}) => {
        const queryParams = new URLSearchParams();

        if (params.tax_type) queryParams.append('tax_type', params.tax_type);

        return api.get(`${endpoints.products.taxRates}?${queryParams.toString()}`);
    },

    /**
     * Get attributes
     * @returns {Promise} - promise with request results
     */
    getAttributes: async () => {
        return api.get(endpoints.products.attributes);
    },

    /**
     * Get attribute details
     * @param {number} id - attribute ID
     * @returns {Promise} - promise with request results
     */
    getAttributeById: async (id) => {
        return api.get(getUrlWithParams(endpoints.products.attributeDetail, { pk: id }));
    },

    /**
     * Get attribute options
     * @param {number} attributeId - attribute ID
     * @returns {Promise} - promise with request results
     */
    getAttributeOptions: async (attributeId) => {
        return api.get(getUrlWithParams(endpoints.products.attributeOptions, { attribute_id: attributeId }));
    }
};

export default productService;