// components/landing/cta-section.tsx
import { Button } from "@/components/ui/button"

export function CtaSection() {
    return (
        <section className="py-16 md:py-24 bg-[#1a4f72] text-white">
            <div className="container px-4 md:px-6 text-center">
                <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
                    Готові оптимізувати вашу логістику?
                </h2>
                <p className="mt-4 text-xl text-gray-200 max-w-[800px] mx-auto">
                    Приєднуйтесь до LWH сьогодні та відкрийте нові можливості для вашого бізнесу
                </p>
                <div className="flex flex-col sm:flex-row justify-center gap-4 mt-8">
                    <Button size="lg" className="bg-[#f39c12] hover:bg-[#e67e22] text-white">
                        Створити обліковий запис
                    </Button>
                    <Button size="lg" variant="outline" className="bg-transparent text-white border-white hover:bg-white/10">
                        Замовити демонстрацію
                    </Button>
                </div>
            </div>
        </section>
    )
}