// components/landing/feature-card.jsx
export function FeatureCard({ icon, title, description }) {
    return (
        <div className="bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition-shadow">
            <div className="mb-4">{icon}</div>
            <h3 className="text-xl font-semibold text-[#1a4f72] mb-2">{title}</h3>
            <p className="text-gray-600">{description}</p>
        </div>
    )
}