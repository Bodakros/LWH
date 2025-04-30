// components/products/product-sort.jsx
import { useState } from "react";
import { ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export function ProductSort({ currentSort, onSortChange }) {
    const [open, setOpen] = useState(false);

    const sortOptions = [
        { value: "name", label: "Name: A-Z" },
        { value: "-name", label: "Name: Z-A" },
        { value: "price", label: "Price: Low to High" },
        { value: "-price", label: "Price: High to Low" },
        { value: "-rating", label: "Rating: High to Low" },
        { value: "rating", label: "Rating: Low to High" },
        { value: "-created_at", label: "Newest First" },
        { value: "created_at", label: "Oldest First" },
    ];

    const getCurrentSortLabel = () => {
        const option = sortOptions.find(option => option.value === currentSort);
        return option ? option.label : "Sort By";
    };

    const handleSelect = (value) => {
        onSortChange(value);
        setOpen(false);
    };

    return (
        <DropdownMenu open={open} onOpenChange={setOpen}>
            <DropdownMenuTrigger asChild>
                <Button variant="outline" className="flex items-center gap-1">
                    {getCurrentSortLabel()}
                    <ChevronDown className="h-4 w-4" />
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
                {sortOptions.map((option) => (
                    <DropdownMenuItem
                        key={option.value}
                        onClick={() => handleSelect(option.value)}
                        className={currentSort === option.value ? "bg-accent text-accent-foreground" : ""}
                    >
                        {option.label}
                    </DropdownMenuItem>
                ))}
            </DropdownMenuContent>
        </DropdownMenu>
    );
}

export default ProductSort;