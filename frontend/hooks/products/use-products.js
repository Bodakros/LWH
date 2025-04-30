// hooks/products/use-products.js
import { useState, useEffect, useCallback } from 'react';
import productService from '../../services/product-service';

/**
 * Hook for fetching and managing product list
 * @param {Object} initialParams - initial request parameters
 * @returns {Object} - data and methods for working with product list
 */
export const useProducts = (initialParams = {}) => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [pagination, setPagination] = useState({
        page: 1,
        total_pages: 1,
        total_items: 0,
        page_size: 20
    });
    const [params, setParams] = useState({
        page: 1,
        page_size: 20,
        ...initialParams
    });

    /**
     * Function to load products from API
     */
    const fetchProducts = useCallback(async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await productService.getProducts(params);
            setProducts(response.results || []);

            // Handle pagination
            setPagination({
                page: response.page || 1,
                total_pages: response.total_pages || 1,
                total_items: response.count || 0,
                page_size: params.page_size
            });
        } catch (err) {
            setError(err.message || 'Error loading products');
            console.error('Error fetching products:', err);
        } finally {
            setLoading(false);
        }
    }, [params]);

    // Load products when parameters change
    useEffect(() => {
        fetchProducts();
    }, [fetchProducts]);

    /**
     * Function to update request parameters
     * @param {Object} newParams - new parameters
     */
    const updateParams = useCallback((newParams) => {
        setParams(prevParams => ({
            ...prevParams,
            ...newParams,
            // When filters change, return to the first page
            page: newParams.hasOwnProperty('page') ? newParams.page : 1
        }));
    }, []);

    /**
     * Function to navigate to a specific page
     * @param {number} pageNumber - page number
     */
    const goToPage = useCallback((pageNumber) => {
        updateParams({ page: pageNumber });
    }, [updateParams]);

    /**
     * Function to change page size
     * @param {number} size - page size
     */
    const changePageSize = useCallback((size) => {
        updateParams({ page_size: size, page: 1 });
    }, [updateParams]);

    /**
     * Function to update sort parameters
     * @param {string} sortField - field to sort by
     */

    const updateSort = useCallback((sortField) => {
        updateParams({ sort: sortField });
    }, [updateParams]);

    /**
     * Function to update search parameters
     * @param {string} searchQuery - search query
     */
    const updateSearch = useCallback((searchQuery) => {
        updateParams({ search: searchQuery });
    }, [updateParams]);

    return {
        products,
        loading,
        error,
        pagination,
        params,
        updateParams,
        goToPage,
        changePageSize,
        updateSort,
        updateSearch,
        refresh: fetchProducts
    };
};

export default useProducts;