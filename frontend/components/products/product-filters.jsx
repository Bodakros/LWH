// components/products/product-filters.jsx
import { useState, useEffect } from "react";
import { Checkbox } from "@/components/ui/checkbox";
import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import { Star, X } from "lucide-react";

export function ProductFilters({
                                   categories = [],
                                   activeFilters,
                                   onFilterChange,
                                   onClearFilter,
                                   onClearAllFilters
                               }) {
    const [localPriceRange, setLocalPriceRange] = useState(activeFilters.price_range || [0, 50000]);

    // Синхронізація локального стану з пропсами
    useEffect(() => {
        if (activeFilters.price_range) {
            setLocalPriceRange(activeFilters.price_range);
        }
    }, [activeFilters.price_range]);

    // Оновлення цінового діапазону з затримкою
    const handlePriceChange = (value) => {
        setLocalPriceRange(value);
        // Затримка оновлення фільтра, щоб не надсилати багато запитів під час руху слайдера
        const handler = setTimeout(() => {
            onFilterChange('price_range', value);
        }, 300);

        return () => clearTimeout(handler);
    };

    // Обробка зміни категорії
    const handleCategoryChange = (categoryId, checked) => {
        onFilterChange('category', checked ? categoryId : null);
    };

    // Обробка зміни наявності товару
    const handleStockChange = (inStock, checked) => {
        onFilterChange('in_stock', checked ? inStock : null);
    };

    // Обробка зміни рейтингу
    const handleRatingChange = (rating, checked) => {
        onFilterChange('min_rating', checked ? rating : null);
    };

    // Обробка зміни бренду
    const handleBrandChange = (brand, checked) => {
        const currentBrands = activeFilters.brands || [];
        if (checked) {
            onFilterChange('brands', [...currentBrands, brand]);
        } else {
            onFilterChange('brands', currentBrands.filter(b => b !== brand));
        }
    };

    return (
        <div className="space-y-6">
            {/* Кнопка очищення всіх фільтрів */}
            {Object.values(activeFilters).some(val =>
                val !== null &&
                (Array.isArray(val) ? val.length > 0 : true)
            ) && (
                <Button
                    variant="ghost"
                    size="sm"
                    className="text-sm text-red-500 hover:text-red-700"
                    onClick={onClearAllFilters}
                >
                    <X className="h-4 w-4 mr-1" /> Очистити всі фільтри
                </Button>
            )}

            {/* Категорії */}
            <div>
                <div className="flex justify-between items-center mb-3">
                    <h3 className="font-medium text-lg text-[#1a4f72]">Категорії</h3>
                    {activeFilters.category && (
                        <Button
                            variant="ghost"
                            size="sm"
                            className="text-xs text-gray-500"
                            onClick={() => onClearFilter('category')}
                        >
                            <X className="h-3 w-3 mr-1" /> Очистити
                        </Button>
                    )}
                </div>
                <div className="space-y-2">
                    {categories.map((category) => (
                        <div key={category.id} className="flex items-center">
                            <Checkbox
                                id={`category-${category.id}`}
                                checked={activeFilters.category === category.id}
                                onCheckedChange={(checked) => handleCategoryChange(category.id, checked)}
                            />
                            <label
                                htmlFor={`category-${category.id}`}
                                className="ml-2 text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                            >
                                {category.name} ({category.product_count || 0})
                            </label>
                        </div>
                    ))}
                </div>
            </div>

            {/* Ціновий діапазон */}
            <div>
                <div className="flex justify-between items-center mb-3">
                    <h3 className="font-medium text-lg text-[#1a4f72]">Ціна</h3>
                    {(activeFilters.price_range &&
                        (activeFilters.price_range[0] !== 0 ||
                            activeFilters.price_range[1] !== 50000)) && (
                        <Button
                            variant="ghost"
                            size="sm"
                            className="text-xs text-gray-500"
                            onClick={() => onClearFilter('price_range')}
                        >
                            <X className="h-3 w-3 mr-1" /> Очистити
                        </Button>
                    )}
                </div>
                <Slider
                    value={localPriceRange}
                    max={50000}
                    step={1000}
                    onValueChange={handlePriceChange}
                    className="mb-6"
                />
                <div className="flex items-center justify-between">
                    <div className="bg-white px-2 py-1 rounded text-sm">{localPriceRange[0]} ₴</div>
                    <div className="bg-white px-2 py-1 rounded text-sm">{localPriceRange[1]} ₴</div>
                </div>
            </div>

            {/* Наявність */}
            <div>
                <div className="flex justify-between items-center mb-3">
                    <h3 className="font-medium text-lg text-[#1a4f72]">Наявність</h3>
                    {activeFilters.in_stock !== null && (
                        <Button
                            variant="ghost"
                            size="sm"
                            className="text-xs text-gray-500"
                            onClick={() => onClearFilter('in_stock')}
                        >
                            <X className="h-3 w-3 mr-1" /> Очистити
                        </Button>
                    )}
                </div>
                <div className="space-y-2">
                    <div className="flex items-center">
                        <Checkbox
                            id="in-stock"
                            checked={activeFilters.in_stock === true}
                            onCheckedChange={(checked) => handleStockChange(true, checked)}
                        />
                        <label
                            htmlFor="in-stock"
                            className="ml-2 text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                        >
                            В наявності
                        </label>
                    </div>
                    <div className="flex items-center">
                        <Checkbox
                            id="out-of-stock"
                            checked={activeFilters.in_stock === false}
                            onCheckedChange={(checked) => handleStockChange(false, checked)}
                        />
                        <label
                            htmlFor="out-of-stock"
                            className="ml-2 text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                        >
                            Немає в наявності
                        </label>
                    </div>
                </div>
            </div>

            {/* Рейтинг */}
            <div>
                <div className="flex justify-between items-center mb-3">
                    <h3 className="font-medium text-lg text-[#1a4f72]">Рейтинг</h3>
                    {activeFilters.min_rating !== null && (
                        <Button
                            variant="ghost"
                            size="sm"
                            className="text-xs text-gray-500"
                            onClick={() => onClearFilter('min_rating')}
                        >
                            <X className="h-3 w-3 mr-1" /> Очистити
                        </Button>
                    )}
                </div>
                <div className="space-y-2">
                    {[5, 4, 3, 2, 1].map((rating) => (
                        <div key={rating} className="flex items-center">
                            <Checkbox
                                id={`rating-${rating}`}
                                checked={activeFilters.min_rating === rating}
                                onCheckedChange={(checked) => handleRatingChange(rating, checked)}
                            />
                            <label
                                htmlFor={`rating-${rating}`}
                                className="ml-2 flex items-center text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                            >
                                {Array.from({ length: rating }).map((_, i) => (
                                    <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                                ))}
                                {Array.from({ length: 5 - rating }).map((_, i) => (
                                    <Star key={i} className="h-4 w-4 text-gray-300" />
                                ))}
                                <span className="ml-1">і вище</span>
                            </label>
                        </div>
                    ))}
                </div>
            </div>

            {/* Бренди - можемо додати їх динамічно з API, але поки використовуємо статичні */}
            <div>
                <div className="flex justify-between items-center mb-3">
                    <h3 className="font-medium text-lg text-[#1a4f72]">Бренди</h3>
                    {activeFilters.brands && activeFilters.brands.length > 0 && (
                        <Button
                            variant="ghost"
                            size="sm"
                            className="text-xs text-gray-500"
                            onClick={() => onClearFilter('brands')}
                        >
                            <X className="h-3 w-3 mr-1" /> Очистити
                        </Button>
                    )}
                </div>
                <div className="space-y-2">
                    {["Samsung", "Apple", "Xiaomi", "Philips", "LG"].map((brand) => (
                        <div key={brand} className="flex items-center">
                            <Checkbox
                                id={`brand-${brand}`}
                                checked={activeFilters.brands && activeFilters.brands.includes(brand)}
                                onCheckedChange={(checked) => handleBrandChange(brand, checked)}
                            />
                            <label
                                htmlFor={`brand-${brand}`}
                                className="ml-2 text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                            >
                                {brand}
                            </label>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

export default ProductFilters;