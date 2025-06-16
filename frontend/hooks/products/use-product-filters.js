// hooks/products/use-product-filters.js
import { useState, useEffect, useCallback } from 'react';
import productService from '../../services/product-service';

/**
 * Hook for managing product filters
 * @param {Function} onFilterChange - callback function called when filters change
 * @returns {Object} - data and methods for working with filters
 */
export const useProductFilters = (onFilterChange) => {
    // State for categories
    const [categories, setCategories] = useState([]);
    const [loadingCategories, setLoadingCategories] = useState(false);

    // State for active filters
    const [activeFilters, setActiveFilters] = useState({
        category: null,
        price_range: [0, 50000],
        in_stock: null,
        min_rating: null,
        brands: []
    });

    // Fetch categories
    const fetchCategories = useCallback(async () => {
        setLoadingCategories(true);
        try {
            const response = await productService.getCategories();
            setCategories(response.results || []);
        } catch (error) {
            console.error('Error fetching categories:', error);
        } finally {
            setLoadingCategories(false);
        }
    }, []);

    // Initialize categories on mount
    useEffect(() => {
        fetchCategories();
    }, [fetchCategories]);

    // Update active filters
    const updateFilter = useCallback((filterName, value) => {
        setActiveFilters(prev => {
            const newFilters = { ...prev, [filterName]: value };

            // Call callback if provided
            if (onFilterChange) {
                onFilterChange(newFilters);
            }

            return newFilters;
        });
    }, [onFilterChange]);

    // Specific filter update methods
    const setCategoryFilter = useCallback((categoryId) => {
        updateFilter('category', categoryId);
    }, [updateFilter]);

    const setPriceRangeFilter = useCallback((range) => {
        updateFilter('price_range', range);
    }, [updateFilter]);

    const setStockFilter = useCallback((inStock) => {
        updateFilter('in_stock', inStock);
    }, [updateFilter]);

    const setRatingFilter = useCallback((rating) => {
        updateFilter('min_rating', rating);
    }, [updateFilter]);

    const setBrandsFilter = useCallback((brands) => {
        updateFilter('brands', brands);
    }, [updateFilter]);

    // Clear all filters
    const clearAllFilters = useCallback(() => {
        setActiveFilters({
            category: null,
            price_range: [0, 50000],
            in_stock: null,
            min_rating: null,
            brands: []
        });

        if (onFilterChange) {
            onFilterChange({
                category: null,
                price_range: [0, 50000],
                in_stock: null,
                min_rating: null,
                brands: []
            });
        }
    }, [onFilterChange]);

    // Clear specific filter
    const clearFilter = useCallback((filterName) => {
        const defaultValues = {
            category: null,
            price_range: [0, 50000],
            in_stock: null,
            min_rating: null,
            brands: []
        };

        updateFilter(filterName, defaultValues[filterName]);
    }, [updateFilter]);

    return {
        categories,
        loadingCategories,
        activeFilters,
        updateFilter,
        setCategoryFilter,
        setPriceRangeFilter,
        setStockFilter,
        setRatingFilter,
        setBrandsFilter,
        clearAllFilters,
        clearFilter
    };
};