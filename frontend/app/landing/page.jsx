// app/landing/page.tsx
import { LandingHeader } from "@/components/landing-header"
import { LandingFooter } from "@/components/landing-footer"
import { HeroSection } from "@/components/landing/hero-section"
import { FeaturesSection } from "@/components/landing/features-section"
import { HowItWorksSection } from "@/components/landing/how-it-works-section"
import { TestimonialsSection } from "@/components/landing/testimonials-section"
import { CtaSection } from "@/components/landing/cta-section"
import { ClientsSection } from "@/components/landing/clients-section"

export default function LandingPage() {
    return (
        <div className="min-h-screen flex flex-col bg-[#f5f7fa]">
            <LandingHeader />
            <HeroSection />
            <FeaturesSection />
            <HowItWorksSection />
            <TestimonialsSection />
            <CtaSection />
            <ClientsSection />
            <LandingFooter />
        </div>
    )
}