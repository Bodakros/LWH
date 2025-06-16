// components/landing/testimonials-section.tsx

function TestimonialCard({ quote, author, company, role }) {
    return (
        <div className="bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition-shadow">
            <div className="mb-4 text-[#f39c12]">
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
                >
                    <path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1z" />
                    <path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3c0 1 0 1 1 1z" />
                </svg>
            </div>
            <p className="text-gray-700 mb-4">{quote}</p>
            <div>
                <p className="font-semibold text-[#1a4f72]">{author}</p>
                <p className="text-sm text-gray-600">
                    {role}, {company}
                </p>
            </div>
        </div>
    )
}

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