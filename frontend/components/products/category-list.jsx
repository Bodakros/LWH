// components/products/category-list.jsx
import Link from "next/link";
import Image from "next/image";
import { ChevronRight } from "lucide-react";

export function CategoryList({ categories, loading, activeCategory, onCategorySelect }) {
    if (loading) {
        return (
            <div className="space-y-2">
                {Array.from({ length: 6 }).map((_, index) => (
                    <div
                        key={index}
                        className="bg-gray-100 animate-pulse rounded-md h-10"
                    />
                ))}
            </div>
        );
    }

    if (!categories || categories.length === 0) {
        return (
            <div className="py-4 text-center text-gray-500">
                No categories available
            </div>
        );
    }

    return (
        <div className="space-y-1">
            <div
                className={`flex items-center justify-between p-2 rounded-md cursor-pointer transition-colors ${
                    !activeCategory ? "bg-accent text-accent-foreground" : "hover:bg-muted"
                }`}
                onClick={() => onCategorySelect(null)}
            >
                <span className="font-medium">All Categories</span>
                {!activeCategory && <ChevronRight className="h-4 w-4" />}
            </div>

            {categories.map((category) => (
                <div
                    key={category.id}
                    className={`flex items-center justify-between p-2 rounded-md cursor-pointer transition-colors ${
                        activeCategory === category.id ? "bg-accent text-accent-foreground" : "hover:bg-muted"
                    }`}
                    onClick={() => onCategorySelect(category.id)}
                >
                    <div className="flex items-center">
                        {category.image && (
                            <div className="relative w-6 h-6 mr-2">
                                <Image
                                    src={category.image}
                                    alt={category.name}
                                    fill
                                    className="object-contain"
                                />
                            </div>
                        )}
                        <span>{category.name}</span>
                        {category.product_count && (
                            <span className="ml-1 text-xs text-gray-500">
                ({category.product_count})
              </span>
                        )}
                    </div>
                    {activeCategory === category.id && <ChevronRight className="h-4 w-4" />}
                </div>
            ))}
        </div>
    );
}

export default CategoryList;