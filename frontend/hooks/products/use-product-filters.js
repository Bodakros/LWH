// hooks/products/use-product-filters.js
import { useState, useEffect, useCallback } from 'react';
import productService from '../../services/product-service';

/**
 * Хук для управління фільтрами продуктів
 * @param {Function} onFilterChange - функція, яка викликається при зміні фільтрів
 * @returns {Object} - дані та методи для роботи з фільтрами
 */
export const useProductFilters = (onFilterChange) => {
    // Стан для категорій
    const [categories, setCategories] = useState([]);
    const [loadingCategories, setLoadingCategories] = useState(false);

    // Стан для активних фільтрів
    const [activeFilters, setActiveFilters] = useState({
        category: null,
        price_range: [0, 50000],
        in_stock: null,
        min_rating: null,
        brands: []
    });

    // Завантаження категорій
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

    // Завантаження категорій при ініціалізації
    useEffect(() => {
        fetchCategories();
    }, [fetchCategories]);

    // Оновлення активних фільтрів
    const updateFilter = useCallback((filterName, value) => {
        setActiveFilters(prev => {
            const newFilters = { ...prev, [filterName]: value };

            // Викликаємо callback, якщо він існує
            if (onFilterChange) {
                onFilterChange(newFilters);
            }

            return newFilters;
        });
    }, [onFilterChange]);

    // Методи для окремих фільтрів
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

    // Очищення всіх фільтрів
    const clearAllFilters = useCallback(() => {
        setActiveFilters({
            category: null,
            price_range: [0, 50000],
            in_stock: null,
            min_rating: null,
            brands: []
        });

        if (onFilterChange) {
            onFilterChange({});
        }
    }, [onFilterChange]);

    // Очищення конкретного фільтра
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

export default useProductFilters;