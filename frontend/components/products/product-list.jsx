// components/products/product-list.jsx
import Image from "next/image";
import Link from "next/link";
import { Heart, ShoppingCart, Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export function ProductList({ products, loading }) {
    const formatPrice = (price) => {
        return new Intl.NumberFormat("uk-UA", {
            style: "currency",
            currency: "UAH",
            minimumFractionDigits: 0,
        }).format(price);
    };

    if (loading) {
        // Skeleton loading state
        return (
            <div className="space-y-4">
                {Array.from({ length: 5 }).map((_, index) => (
                    <div
                        key={index}
                        className="bg-gray-100 animate-pulse rounded-lg h-32"
                    />
                ))}
            </div>
        );
    }

    if (products.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center py-12">
                <h3 className="text-xl font-semibold text-gray-700 mb-2">No products found</h3>
                <p className="text-gray-500">Try changing your filter settings</p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {products.map((product) => (
                <div
                    key={product.id}
                    className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow p-4 flex"
                >
                    <div className="relative h-32 w-32 flex-shrink-0">
                        <Image
                            src={product.image || "/placeholder.svg"}
                            alt={product.name}
                            fill
                            className="object-contain"
                        />
                    </div>

                    <div className="ml-4 flex-1">
                        <div className="flex justify-between">
                            <div>
                                <Link href={`/product/${product.id}`}>
                                    <h3 className="font-medium text-lg text-[#1a4f72] hover:text-[#f39c12] transition-colors">
                                        {product.name}
                                    </h3>
                                </Link>
                                <div className="flex items-center mt-1">
                                    <div className="flex items-center text-yellow-400 mr-1">
                                        <Star className="h-4 w-4 fill-current" />
                                    </div>
                                    <span className="text-sm font-medium">{product.rating}</span>
                                    <span className="text-sm text-gray-500 ml-2">({product.review_count || 0} reviews)</span>
                                </div>
                            </div>
                            <div className="text-right">
                                <div className="font-bold text-xl">{formatPrice(product.price)}</div>
                                {product.old_price && (
                                    <div className="text-gray-500 line-through text-sm">
                                        {formatPrice(product.old_price)}
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="mt-2">
                            <p className="text-sm text-gray-600 line-clamp-2">
                                {product.description || "No description available"}
                            </p>
                        </div>

                        <div className="mt-3 flex items-center justify-between">
                            <div className="flex items-center space-x-2">
                                {product.inStock ? (
                                    <Badge className="bg-green-500">In Stock</Badge>
                                ) : (
                                    <Badge variant="outline" className="text-red-500 border-red-500">Out of Stock</Badge>
                                )}
                                {product.category && (
                                    <Badge variant="outline">{product.category}</Badge>
                                )}
                            </div>

                            <div className="flex items-center space-x-2">
                                <Button variant="outline" size="sm" className="rounded-full h-8 w-8 p-0">
                                    <Heart className="h-4 w-4" />
                                </Button>
                                <Button
                                    className="bg-[#1a4f72] hover:bg-[#164263]"
                                    size="sm"
                                    disabled={!product.inStock}
                                >
                                    <ShoppingCart className="h-4 w-4 mr-1" />
                                    Add to Cart
                                </Button>
                            </div>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
}

export default ProductList;