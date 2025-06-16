// components/landing/features-section.tsx
import { BarChart3, Box, Package, Shield, Truck, Warehouse } from "lucide-react"

function FeatureCard({ icon, title, description }) {
    return (
        <div className="bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition-shadow">
            <div className="mb-4">{icon}</div>
            <h3 className="text-xl font-semibold text-[#1a4f72] mb-2">{title}</h3>
            <p className="text-gray-600">{description}</p>
        </div>
    )
}

export function FeaturesSection() {
    return (
        <section className="py-16 md:py-24">
            <div className="container px-4 md:px-6">
                <div className="text-center mb-12">
                    <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl text-[#1a4f72]">
                        Ключові можливості
                    </h2>
                    <p className="mt-4 text-xl text-gray-600 max-w-[800px] mx-auto">
                        LWH пропонує повний набір інструментів для ефективного управління складською логістикою
                    </p>
                </div>

                <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                    <FeatureCard
                        icon={<Package className="h-10 w-10 text-[#f39c12]" />}
                        title="Управління товарами"
                        description="Зручний каталог товарів з детальною інформацією про запаси та розташування на складах."
                    />
                    <FeatureCard
                        icon={<Warehouse className="h-10 w-10 text-[#f39c12]" />}
                        title="Управління складами"
                        description="Повний контроль над складськими приміщеннями, секціями та їх зайнятістю."
                    />
                    <FeatureCard
                        icon={<Truck className="h-10 w-10 text-[#f39c12]" />}
                        title="Обробка замовлень"
                        description="Автоматизація процесів обробки замовлень від створення до доставки."
                    />
                    <FeatureCard
                        icon={<BarChart3 className="h-10 w-10 text-[#f39c12]" />}
                        title="Аналітика та звіти"
                        description="Детальна аналітика продажів, запасів та ефективності використання складських приміщень."
                    />
                    <FeatureCard
                        icon={<Box className="h-10 w-10 text-[#f39c12]" />}
                        title="Інвентаризація"
                        description="Зручні інструменти для проведення інвентаризації та контролю запасів."
                    />
                    <FeatureCard
                        icon={<Shield className="h-10 w-10 text-[#f39c12]" />}
                        title="Безпека даних"
                        description="Надійний захист даних та розмежування прав доступу для різних ролей користувачів."
                    />
                </div>
            </div>
        </section>
    )
}