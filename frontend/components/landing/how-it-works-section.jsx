// components/landing/how-it-works-section.tsx
import { ArrowRight, CheckCircle } from "lucide-react"
import { Button } from "@/components/ui/button"

export function HowItWorksSection() {
    return (
        <section className="py-16 md:py-24 bg-white">
            <div className="container px-4 md:px-6">
                <div className="text-center mb-12">
                    <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl text-[#1a4f72]">Як це працює</h2>
                    <p className="mt-4 text-xl text-gray-600 max-w-[800px] mx-auto">
                        LWH створена для двох основних типів користувачів: продавців та власників складів
                    </p>
                </div>

                <div className="grid gap-12 lg:grid-cols-2">
                    <div className="space-y-6">
                        <div className="bg-[#f5f7fa] p-6 rounded-lg">
                            <h3 className="text-2xl font-bold text-[#1a4f72] mb-4">Для продавців</h3>
                            <ul className="space-y-4">
                                <li className="flex items-start">
                                    <CheckCircle className="h-6 w-6 text-[#f39c12] mr-2 flex-shrink-0 mt-0.5" />
                                    <span>Управління каталогом товарів та їх запасами</span>
                                </li>
                                <li className="flex items-start">
                                    <CheckCircle className="h-6 w-6 text-[#f39c12] mr-2 flex-shrink-0 mt-0.5" />
                                    <span>Пошук та оренда складських приміщень</span>
                                </li>
                                <li className="flex items-start">
                                    <CheckCircle className="h-6 w-6 text-[#f39c12] mr-2 flex-shrink-0 mt-0.5" />
                                    <span>Обробка замовлень та відстеження доставок</span>
                                </li>
                                <li className="flex items-start">
                                    <CheckCircle className="h-6 w-6 text-[#f39c12] mr-2 flex-shrink-0 mt-0.5" />
                                    <span>Аналітика продажів та прогнозування попиту</span>
                                </li>
                            </ul>
                            <div className="mt-6">
                                <Button className="bg-[#1a4f72] hover:bg-[#164263]">
                                    Реєстрація для продавців <ArrowRight className="ml-2 h-4 w-4" />
                                </Button>
                            </div>
                        </div>
                    </div>

                    <div className="space-y-6">
                        <div className="bg-[#f5f7fa] p-6 rounded-lg">
                            <h3 className="text-2xl font-bold text-[#1a4f72] mb-4">Для власників складів</h3>
                            <ul className="space-y-4">
                                <li className="flex items-start">
                                    <CheckCircle className="h-6 w-6 text-[#f39c12] mr-2 flex-shrink-0 mt-0.5" />
                                    <span>Управління складськими приміщеннями та секціями</span>
                                </li>
                                <li className="flex items-start">
                                    <CheckCircle className="h-6 w-6 text-[#f39c12] mr-2 flex-shrink-0 mt-0.5" />
                                    <span>Моніторинг зайнятості та оптимізація використання простору</span>
                                </li>
                                <li className="flex items-start">
                                    <CheckCircle className="h-6 w-6 text-[#f39c12] mr-2 flex-shrink-0 mt-0.5" />
                                    <span>Управління клієнтами та договорами оренди</span>
                                </li>
                                <li className="flex items-start">
                                    <CheckCircle className="h-6 w-6 text-[#f39c12] mr-2 flex-shrink-0 mt-0.5" />
                                    <span>Фінансова аналітика та звітність</span>
                                </li>
                            </ul>
                            <div className="mt-6">
                                <Button className="bg-[#1a4f72] hover:bg-[#164263]">
                                    Реєстрація для власників <ArrowRight className="ml-2 h-4 w-4" />
                                </Button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    )
}