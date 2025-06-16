"use client"

import { useState, useEffect } from "react"
import { Filter, Grid3X3, List, SlidersHorizontal } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { LandingHeader } from "@/components/landing-header"
import { LandingFooter } from "@/components/landing-footer"
import { Pagination, PaginationContent, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious } from "@/components/ui/pagination"
import { ProductFilters } from "@/components/products/product-filters"
import { ProductSort } from "@/components/products/product-sort"
import { ProductGrid } from "@/components/products/product-grid"
import { ProductList } from "@/components/products/product-list"
import { CategoryList } from "@/components/products/category-list"
import { useProducts } from "@/hooks/products/use-products"
import { useProductFilters } from "@/hooks/products/use-product-filters"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { Badge } from "@/components/ui/badge"
import { useSearchParams, useRouter } from "next/navigation"

export default function CatalogPage() {
    // View mode state (grid or list)
    const [viewMode, setViewMode] = useState("grid")

    // Mobile filters state
    const [filtersOpen, setFiltersOpen] = useState(false)

    // Search input state
    const [searchInput, setSearchInput] = useState("")

    // URL and router
    const searchParams = useSearchParams()
    const router = useRouter()

    // Get initial params from URL
    const initialParams = {
        search: searchParams.get("search") || "",
        category: searchParams.get("category") ? parseInt(searchParams.get("category")) : null,
        sort: searchParams.get("sort") || "-created_at",
        page: searchParams.get("page") ? parseInt(searchParams.get("page")) : 1,
        page_size: 12
    }

    // Initialize products hook with URL params
    const {
        products,
        loading,
        pagination,
        params,
        updateParams,
        goToPage,
        updateSort,
        updateSearch
    } = useProducts(initialParams)

    // Handle filter changes
    const onFilterChange = (newFilters) => {
        updateParams(newFilters)
        // Update URL as well
        updateUrl({...params, ...newFilters})
    }

    // Initialize filters hook
    const {
        categories,
        loadingCategories,
        activeFilters,
        updateFilter,
        clearAllFilters,
        clearFilter
    } = useProductFilters(onFilterChange)

    // Update URL with current parameters
    const updateUrl = (currentParams) => {
        const newParams = new URLSearchParams()

        if (currentParams.search) newParams.set("search", currentParams.search)
        if (currentParams.category) newParams.set("category", currentParams.category)
        if (currentParams.sort) newParams.set("sort", currentParams.sort)
        if (currentParams.page && currentParams.page > 1) newParams.set("page", currentParams.page)

        // Add price range
        if (currentParams.price_range &&
            (currentParams.price_range[0] > 0 || currentParams.price_range[1] < 50000)) {
            newParams.set("min_price", currentParams.price_range[0])
            newParams.set("max_price", currentParams.price_range[1])
        }

        // Add in_stock filter
        if (currentParams.in_stock !== null) {
            newParams.set("in_stock", currentParams.in_stock)
        }

        // Add rating filter
        if (currentParams.min_rating) {
            newParams.set("min_rating", currentParams.min_rating)
        }

        // Add brands filter
        if (currentParams.brands && currentParams.brands.length > 0) {
            currentParams.brands.forEach((brand, index) => {
                newParams.append("brand", brand)
            })
        }

        // Update the URL
        router.push(`/catalog?${newParams.toString()}`)
    }

    // Handle search submission
    const handleSearch = (e) => {
        e.preventDefault()
        updateSearch(searchInput)
        updateUrl({...params, search: searchInput})
    }

    // Handle sort change
    const handleSortChange = (sortValue) => {
        updateSort(sortValue)
        updateUrl({...params, sort: sortValue})
    }

    // Handle category selection
    const handleCategorySelect = (categoryId) => {
        updateFilter('category', categoryId)
        updateUrl({...params, category: categoryId, page: 1})
    }

    // Get active filters count
    const getActiveFiltersCount = () => {
        let count = 0
        if (activeFilters.category) count++
        if (activeFilters.in_stock !== null) count++
        if (activeFilters.min_rating) count++
        if (activeFilters.price_range &&
            (activeFilters.price_range[0] > 0 || activeFilters.price_range[1] < 50000)) count++
        if (activeFilters.brands && activeFilters.brands.length > 0) count += activeFilters.brands.length

        return count
    }

    // Initialize search input from URL params
    useEffect(() => {
        if (params.search) {
            setSearchInput(params.search)
        }
    }, [params.search])

    return (
        <div className="min-h-screen flex flex-col bg-[#f5f7fa]">
            <LandingHeader />

            {/* Hero Banner */}
            <div className="bg-[#1a4f72] text-white py-8">
                <div className="container px-4 md:px-6">
                    <h1 className="text-2xl md:text-3xl font-bold">Каталог товарів</h1>
                    <p className="mt-2">Знайдіть все необхідне для вашого дому та офісу</p>
                </div>
            </div>

            {/* Main Content */}
            <div className="container px-4 md:px-6 py-8 flex-1">
                <div className="flex flex-col md:flex-row gap-6">
                    {/* Mobile Filters Toggle */}
                    <div className="md:hidden mb-4">
                        <Sheet open={filtersOpen} onOpenChange={setFiltersOpen}>
                            <SheetTrigger asChild>
                                <Button variant="outline" className="w-full flex items-center justify-center">
                                    <Filter className="mr-2 h-4 w-4" />
                                    Фільтри
                                    {getActiveFiltersCount() > 0 && (
                                        <Badge className="ml-2 bg-[#1a4f72]">{getActiveFiltersCount()}</Badge>
                                    )}
                                </Button>
                            </SheetTrigger>
                            <SheetContent side="left" className="w-[300px] sm:w-[350px] overflow-y-auto">
                                <h2 className="text-xl font-semibold mb-4">Фільтри</h2>
                                <CategoryList
                                    categories={categories}
                                    loading={loadingCategories}
                                    activeCategory={activeFilters.category}
                                    onCategorySelect={handleCategorySelect}
                                />
                                <div className="mt-6">
                                    <ProductFilters
                                        categories={categories}
                                        activeFilters={activeFilters}
                                        onFilterChange={updateFilter}
                                        onClearFilter={clearFilter}
                                        onClearAllFilters={clearAllFilters}
                                    />
                                </div>
                            </SheetContent>
                        </Sheet>
                    </div>

                    {/* Sidebar Filters - Desktop */}
                    <div className="hidden md:block w-64 flex-shrink-0">
                        <div className="bg-white rounded-lg shadow p-4 mb-4">
                            <h3 className="font-semibold text-lg mb-3 text-[#1a4f72]">Категорії</h3>
                            <CategoryList
                                categories={categories}
                                loading={loadingCategories}
                                activeCategory={activeFilters.category}
                                onCategorySelect={handleCategorySelect}
                            />
                        </div>
                        <div className="bg-white rounded-lg shadow p-4">
                            <ProductFilters
                                categories={categories}
                                activeFilters={activeFilters}
                                onFilterChange={updateFilter}
                                onClearFilter={clearFilter}
                                onClearAllFilters={clearAllFilters}
                            />
                        </div>
                    </div>

                    {/* Product Grid */}
                    <div className="flex-1">
                        {/* Search and Sort Controls */}
                        <div className="bg-white rounded-lg shadow p-4 mb-6">
                            <div className="flex flex-col sm:flex-row gap-4">
                                <form onSubmit={handleSearch} className="relative flex-1">
                                    <Input
                                        type="search"
                                        placeholder="Пошук товарів..."
                                        value={searchInput}
                                        onChange={(e) => setSearchInput(e.target.value)}
                                        className="pl-9 bg-white"
                                    />
                                    <Button type="submit" variant="ghost" size="icon" className="absolute left-0 top-0 h-10 w-10">
                                        <svg
                                            xmlns="http://www.w3.org/2000/svg"
                                            width="24"
                                            height="24"
                                            viewBox="0 0 24 24"
                                            fill="none"
                                            stroke="currentColor"
                                            strokeWidth="2"
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            className="h-4 w-4 opacity-50"
                                        >
                                            <circle cx="11" cy="11" r="8" />
                                            <path d="m21 21-4.3-4.3" />
                                        </svg>
                                    </Button>
                                </form>
                                <div className="flex items-center gap-2">
                                    <Button
                                        variant={viewMode === "grid" ? "default" : "outline"}
                                        size="icon"
                                        className="h-10 w-10"
                                        onClick={() => setViewMode("grid")}
                                    >
                                        <Grid3X3 className="h-4 w-4" />
                                    </Button>
                                    <Button
                                        variant={viewMode === "list" ? "default" : "outline"}
                                        size="icon"
                                        className="h-10 w-10"
                                        onClick={() => setViewMode("list")}
                                    >
                                        <List className="h-4 w-4" />
                                    </Button>
                                    <ProductSort currentSort={params.sort} onSortChange={handleSortChange} />
                                </div>
                            </div>
                        </div>

                        {/* Product Count and Active Filters */}
                        {(getActiveFiltersCount() > 0 || params.search) && (
                            <div className="bg-white rounded-lg shadow p-4 mb-4">
                                <div className="flex flex-wrap items-center justify-between gap-2">
                                    <p className="text-sm text-gray-600">
                                        Знайдено <span className="font-medium">{pagination.total_items}</span> товарів
                                    </p>
                                    <div className="flex flex-wrap gap-2">
                                        {params.search && (
                                            <Badge variant="outline" className="px-3 py-1 rounded-full flex items-center">
                                                Пошук: {params.search}
                                                <button
                                                    className="ml-2 text-gray-400 hover:text-gray-600"
                                                    onClick={() => {
                                                        setSearchInput("")
                                                        updateSearch("")
                                                        updateUrl({...params, search: ""})
                                                    }}
                                                >
                                                    ×
                                                </button>
                                            </Badge>
                                        )}
                                        {activeFilters.category && (
                                            <Badge variant="outline" className="px-3 py-1 rounded-full flex items-center">
                                                {categories.find(c => c.id === activeFilters.category)?.name || "Категорія"}
                                                <button
                                                    className="ml-2 text-gray-400 hover:text-gray-600"
                                                    onClick={() => clearFilter('category')}
                                                >
                                                    ×
                                                </button>
                                            </Badge>
                                        )}
                                        {activeFilters.in_stock !== null && (
                                            <Badge variant="outline" className="px-3 py-1 rounded-full flex items-center">
                                                {activeFilters.in_stock ? "В наявності" : "Немає в наявності"}
                                                <button
                                                    className="ml-2 text-gray-400 hover:text-gray-600"
                                                    onClick={() => clearFilter('in_stock')}
                                                >
                                                    ×
                                                </button>
                                            </Badge>
                                        )}
                                        {getActiveFiltersCount() > 0 && (
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                className="text-red-500 hover:text-red-700"
                                                onClick={clearAllFilters}
                                            >
                                                Очистити всі
                                            </Button>
                                        )}
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Products Display */}
                        <div className="bg-white rounded-lg shadow p-4">
                            {viewMode === "grid" ? (
                                <ProductGrid products={products} loading={loading} />
                            ) : (
                                <ProductList products={products} loading={loading} />
                            )}

                            {/* Pagination */}
                            {pagination.total_pages > 1 && (
                                <div className="mt-8">
                                    <Pagination>
                                        <PaginationContent>
                                            <PaginationItem>
                                                <PaginationPrevious
                                                    href="#"
                                                    onClick={(e) => {
                                                        e.preventDefault();
                                                        if (pagination.page > 1) goToPage(pagination.page - 1);
                                                    }}
                                                    className={pagination.page <= 1 ? "pointer-events-none opacity-50" : ""}
                                                />
                                            </PaginationItem>

                                            {Array.from({ length: Math.min(5, pagination.total_pages) }).map((_, i) => {
                                                // Logic to display pagination items centered around current page
                                                let pageNum;
                                                if (pagination.total_pages <= 5) {
                                                    pageNum = i + 1;
                                                } else if (pagination.page <= 3) {
                                                    pageNum = i + 1;
                                                } else if (pagination.page >= pagination.total_pages - 2) {
                                                    pageNum = pagination.total_pages - 4 + i;
                                                } else {
                                                    pageNum = pagination.page - 2 + i;
                                                }

                                                return (
                                                    <PaginationItem key={pageNum}>
                                                        <PaginationLink
                                                            href="#"
                                                            onClick={(e) => {
                                                                e.preventDefault();
                                                                goToPage(pageNum);
                                                            }}
                                                            isActive={pagination.page === pageNum}
                                                        >
                                                            {pageNum}
                                                        </PaginationLink>
                                                    </PaginationItem>
                                                );
                                            })}

                                            <PaginationItem>
                                                <PaginationNext
                                                    href="#"
                                                    onClick={(e) => {
                                                        e.preventDefault();
                                                        if (pagination.page < pagination.total_pages) goToPage(pagination.page + 1);
                                                    }}
                                                    className={pagination.page >= pagination.total_pages ? "pointer-events-none opacity-50" : ""}
                                                />
                                            </PaginationItem>
                                        </PaginationContent>
                                    </Pagination>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Newsletter */}
            <section className="py-12 bg-[#1a4f72] text-white mt-12">
                <div className="container px-4 md:px-6 text-center">
                    <h2 className="text-2xl font-bold mb-2">Підпишіться на новини та акції</h2>
                    <p className="mb-6 max-w-md mx-auto">Отримуйте інформацію про нові товари та спеціальні пропозиції</p>
                    <div className="flex flex-col sm:flex-row gap-2 max-w-md mx-auto">
                        <Input placeholder="Ваш email" className="bg-white text-black" />
                        <Button className="bg-[#f39c12] hover:bg-[#e67e22] text-white">Підписатися</Button>
                    </div>
                </div>
            </section>

            <LandingFooter />
        </div>
    )
}