// components/landing/clients-section.tsx
import Image from "next/image"

export function ClientsSection() {
    return (
        <section className="py-12 md:py-16 bg-white">
            <div className="container px-4 md:px-6">
                <div className="text-center mb-8">
                    <h2 className="text-2xl font-semibold text-[#1a4f72]">Нам довіряють</h2>
                </div>
                <div className="flex flex-wrap justify-center items-center gap-8 md:gap-12">
                    {[1, 2, 3, 4, 5, 6].map((i) => (
                        <div
                            key={i}
                            className="w-24 h-12 md:w-32 md:h-16 relative grayscale opacity-70 hover:grayscale-0 hover:opacity-100 transition-all"
                        >
                            <Image
                                src={`/placeholder.svg?height=64&width=128&text=Логотип ${i}`}
                                alt={`Клієнт ${i}`}
                                fill
                                className="object-contain"
                            />
                        </div>
                    ))}
                </div>
            </div>
        </section>
    )
}