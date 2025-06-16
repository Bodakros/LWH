// components/landing/contact-section.jsx
import { Mail, MapPin, Phone } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export function ContactSection() {
    return (
        <section id="contact" className="py-16 md:py-24 bg-white">
            <div className="container px-4 md:px-6">
                <div className="text-center mb-12">
                    <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl text-[#1a4f72]">
                        Зв'яжіться з нами
                    </h2>
                    <p className="mt-4 text-xl text-gray-600 max-w-[800px] mx-auto">
                        Готові розпочати? Наша команда готова допомогти вам оптимізувати вашу логістику
                    </p>
                </div>

                <div className="grid gap-12 lg:grid-cols-2 max-w-6xl mx-auto">
                    {/* Contact Form */}
                    <div className="bg-[#f5f7fa] p-6 rounded-lg">
                        <h3 className="text-2xl font-bold text-[#1a4f72] mb-6">Відправте нам повідомлення</h3>
                        <form className="space-y-4">
                            <div className="grid gap-4 md:grid-cols-2">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Ім'я *
                                    </label>
                                    <Input placeholder="Ваше ім'я" required />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Прізвище *
                                    </label>
                                    <Input placeholder="Ваше прізвище" required />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Email *
                                </label>
                                <Input type="email" placeholder="your@email.com" required />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Телефон
                                </label>
                                <Input type="tel" placeholder="+380 (XX) XXX-XX-XX" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Компанія
                                </label>
                                <Input placeholder="Назва вашої компанії" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Повідомлення *
                                </label>
                                <textarea
                                    className="flex min-h-[120px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                    placeholder="Розкажіть нам про ваші потреби..."
                                    required
                                />
                            </div>
                            <Button className="w-full bg-[#1a4f72] hover:bg-[#164263]">
                                Відправити повідомлення
                            </Button>
                        </form>
                    </div>

                    {/* Contact Information */}
                    <div className="space-y-8">
                        <div>
                            <h3 className="text-2xl font-bold text-[#1a4f72] mb-6">Контактна інформація</h3>
                            <div className="space-y-6">
                                <div className="flex items-start">
                                    <MapPin className="h-6 w-6 text-[#f39c12] mr-3 flex-shrink-0 mt-1" />
                                    <div>
                                        <h4 className="font-medium text-[#1a4f72] mb-1">Адреса</h4>
                                        <p className="text-gray-600">
                                            вул. Хрещатик, 22<br />
                                            Київ, 01001, Україна
                                        </p>
                                    </div>
                                </div>

                                <div className="flex items-start">
                                    <Phone className="h-6 w-6 text-[#f39c12] mr-3 flex-shrink-0 mt-1" />
                                    <div>
                                        <h4 className="font-medium text-[#1a4f72] mb-1">Телефон</h4>
                                        <p className="text-gray-600">+38 (044) 123-45-67</p>
                                        <p className="text-gray-600">+38 (050) 123-45-67</p>
                                    </div>
                                </div>

                                <div className="flex items-start">
                                    <Mail className="h-6 w-6 text-[#f39c12] mr-3 flex-shrink-0 mt-1" />
                                    <div>
                                        <h4 className="font-medium text-[#1a4f72] mb-1">Email</h4>
                                        <p className="text-gray-600">info@lwh.ua</p>
                                        <p className="text-gray-600">support@lwh.ua</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Business Hours */}
                        <div className="bg-[#f5f7fa] p-6 rounded-lg">
                            <h4 className="font-bold text-[#1a4f72] mb-4">Години роботи</h4>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Понеділок - П'ятниця:</span>
                                    <span className="font-medium">9:00 - 18:00</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Субота:</span>
                                    <span className="font-medium">10:00 - 16:00</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Неділя:</span>
                                    <span className="font-medium">Вихідний</span>
                                </div>
                            </div>
                        </div>

                        {/* Quick Demo */}
                        <div className="bg-[#1a4f72] p-6 rounded-lg text-white">
                            <h4 className="font-bold mb-2">Швидка демонстрація</h4>
                            <p className="text-gray-200 text-sm mb-4">
                                Хочете побачити LWH в дії? Замовте персональну демонстрацію прямо зараз.
                            </p>
                            <Button variant="outline" className="bg-transparent text-white border-white hover:bg-white/10">
                                Замовити демо
                            </Button>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    )
}