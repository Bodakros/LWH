// components/landing/pricing-section.jsx
import { CheckCircle } from "lucide-react"
import { Button } from "@/components/ui/button"

export function PricingSection() {
    return (
        <section id="pricing" className="py-16 md:py-24 bg-[#f5f7fa]">
            <div className="container px-4 md:px-6">
                <div className="text-center mb-12">
                    <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl text-[#1a4f72]">
                        Тарифні плани
                    </h2>
                    <p className="mt-4 text-xl text-gray-600 max-w-[800px] mx-auto">
                        Оберіть оптимальний план для вашого бізнесу
                    </p>
                </div>

                <div className="grid gap-8 md:grid-cols-3 max-w-5xl mx-auto">
                    {/* Basic Plan */}
                    <div className="bg-white rounded-lg shadow-lg p-6">
                        <h3 className="text-xl font-bold text-[#1a4f72] mb-2">Базовий</h3>
                        <div className="mb-4">
                            <span className="text-3xl font-bold text-[#1a4f72]">₴2,999</span>
                            <span className="text-gray-600">/місяць</span>
                        </div>
                        <ul className="space-y-3 mb-6">
                            <li className="flex items-center">
                                <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                                <span>До 1000 товарів</span>
                            </li>
                            <li className="flex items-center">
                                <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                                <span>1 склад</span>
                            </li>
                            <li className="flex items-center">
                                <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                                <span>Базова аналітика</span>
                            </li>
                            <li className="flex items-center">
                                <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                                <span>Email підтримка</span>
                            </li>
                        </ul>
                        <Button className="w-full bg-[#1a4f72] hover:bg-[#164263]">
                            Обрати план
                        </Button>
                    </div>

                    {/* Professional Plan */}
                    <div className="bg-white rounded-lg shadow-lg p-6 border-2 border-[#f39c12] relative">
                        <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                            <span className="bg-[#f39c12] text-white px-4 py-1 rounded-full text-sm font-medium">
                                Популярний
                            </span>
                        </div>
                        <h3 className="text-xl font-bold text-[#1a4f72] mb-2">Професійний</h3>
                        <div className="mb-4">
                            <span className="text-3xl font-bold text-[#1a4f72]">₴5,999</span>
                            <span className="text-gray-600">/місяць</span>
                        </div>
                        <ul className="space-y-3 mb-6">
                            <li className="flex items-center">
                                <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                                <span>До 10,000 товарів</span>
                            </li>
                            <li className="flex items-center">
                                <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                                <span>До 5 складів</span>
                            </li>
                            <li className="flex items-center">
                                <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                                <span>Розширена аналітика</span>
                            </li>
                            <li className="flex items-center">
                                <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                                <span>API інтеграція</span>
                            </li>
                            <li className="flex items-center">
                                <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                                <span>Пріоритетна підтримка</span>
                            </li>
                        </ul>
                        <Button className="w-full bg-[#f39c12] hover:bg-[#e67e22]">
                            Обрати план
                        </Button>
                    </div>

                    {/* Enterprise Plan */}
                    <div className="bg-white rounded-lg shadow-lg p-6">
                        <h3 className="text-xl font-bold text-[#1a4f72] mb-2">Корпоративний</h3>
                        <div className="mb-4">
                            <span className="text-3xl font-bold text-[#1a4f72]">Індивідуально</span>
                        </div>
                        <ul className="space-y-3 mb-6">
                            <li className="flex items-center">
                                <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                                <span>Необмежена кількість товарів</span>
                            </li>
                            <li className="flex items-center">
                                <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                                <span>Необмежена кількість складів</span>
                            </li>
                            <li className="flex items-center">
                                <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                                <span>Повна аналітика</span>
                            </li>
                            <li className="flex items-center">
                                <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                                <span>Персональний менеджер</span>
                            </li>
                            <li className="flex items-center">
                                <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                                <span>24/7 підтримка</span>
                            </li>
                        </ul>
                        <Button variant="outline" className="w-full border-[#1a4f72] text-[#1a4f72]">
                            Зв'язатися з нами
                        </Button>
                    </div>
                </div>
            </div>
        </section>
    )
}