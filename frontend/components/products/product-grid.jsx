// components/products/product-grid.jsx
import { ProductCard } from "@/components/product-card";
import { Skeleton } from "@/components/ui/skeleton";

export function ProductGrid({ products, loading }) {
    if (loading) {
        return (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {Array.from({ length: 8 }).map((_, index) => (
                    <div key={index} className="h-[360px] bg-white rounded-lg shadow-sm p-4">
                        <Skeleton className="h-[180px] w-full mb-4" />
                        <Skeleton className="h-5 w-2/3 mb-2" />
                        <Skeleton className="h-4 w-1/2 mb-2" />
                        <Skeleton className="h-4 w-3/4 mb-4" />
                        <div className="flex justify-between mt-auto">
                            <Skeleton className="h-6 w-1/3" />
                            <Skeleton className="h-8 w-1/3 rounded-md" />
                        </div>
                    </div>
                ))}
            </div>
        );
    }

    if (products.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center py-12">
                <h3 className="text-xl font-semibold text-gray-700 mb-2">No products found</h3>
                <p className="text-gray-500">Try adjusting your filter settings</p>
            </div>
        );
    }

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {products.map((product) => (
                <ProductCard key={product.id} product={product} />
            ))}
        </div>
    );
}

export default ProductGrid;