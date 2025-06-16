// components/landing/hero-section.jsx
import Image from "next/image"
import { ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"

export function HeroSection() {
    return (
        <section className="bg-[#1a4f72] text-white py-16 md:py-24">
            <div className="container px-4 md:px-6">
                <div className="grid gap-6 lg:grid-cols-2 lg:gap-12 items-center">
                    <div className="space-y-4">
                        <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
                            Ефективне управління складською логістикою
                        </h1>
                        <p className="max-w-[600px] text-gray-200 md:text-xl">
                            LWH - це сучасна система управління складами, яка з'єднує продавців та власників складів для оптимізації
                            логістичних процесів.
                        </p>
                        <div className="flex flex-col sm:flex-row gap-3 pt-4">
                            <Button size="lg" className="bg-[#f39c12] hover:bg-[#e67e22] text-white">
                                Почати безкоштовно
                            </Button>
                            <Button
                                size="lg"
                                variant="outline"
                                className="bg-transparent text-white border-white hover:bg-white/10"
                            >
                                Дізнатися більше
                            </Button>
                        </div>
                    </div>
                    <div className="relative h-[300px] md:h-[400px] lg:h-[500px]">
                        <Image
                            src="/placeholder.svg?height=500&width=600"
                            alt="LWH Dashboard"
                            fill
                            className="object-contain rounded-lg"
                        />
                    </div>
                </div>
            </div>
        </section>
    )
}