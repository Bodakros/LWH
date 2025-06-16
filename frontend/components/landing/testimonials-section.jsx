// components/landing/testimonials-section.jsx
import { TestimonialCard } from "./testimonial-card"

export function TestimonialsSection() {
    return (
        <section className="py-16 md:py-24">
            <div className="container px-4 md:px-6">
                <div className="text-center mb-12">
                    <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl text-[#1a4f72]">
                        Відгуки клієнтів
                    </h2>
                    <p className="mt-4 text-xl text-gray-600 max-w-[800px] mx-auto">
                        Дізнайтеся, що кажуть наші клієнти про роботу з LWH
                    </p>
                </div>

                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    <TestimonialCard
                        quote="LWH повністю змінила наш підхід до управління запасами. Тепер ми маємо повний контроль над товарами та їх розташуванням."
                        author="Олександр Петренко"
                        company="ТехноМаркет"
                        role="Директор з логістики"
                    />
                    <TestimonialCard
                        quote="Завдяки LWH ми змогли оптимізувати використання наших складських приміщень та збільшити прибуток на 25%."
                        author="Марія Коваленко"
                        company="СкладПро"
                        role="Власник"
                    />
                    <TestimonialCard
                        quote="Інтуїтивний інтерфейс та потужна аналітика роблять LWH незамінним інструментом для нашого бізнесу."
                        author="Іван Сидоренко"
                        company="МегаТрейд"
                        role="CEO"
                    />
                </div>
            </div>
        </section>
    )
}