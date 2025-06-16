import { CheckCircle } from "lucide-react"

export function FeatureCard({ icon, title, description, features = [] }) {
    return (
        <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-lg transition-all duration-300 border border-gray-100 group hover:border-[#f39c12]/20">
            <div className="mb-4 transform group-hover:scale-110 transition-transform duration-300">
                {icon}
            </div>
            <h3 className="text-xl font-semibold text-[#1a4f72] mb-3 group-hover:text-[#f39c12] transition-colors">
                {title}
            </h3>
            <p className="text-gray-600 mb-4 leading-relaxed">
                {description}
            </p>

            {features && features.length > 0 && (
                <ul className="space-y-2">
                    {features.map((feature, index) => (
                        <li key={index} className="flex items-center text-sm text-gray-700">
                            <CheckCircle className="h-4 w-4 text-green-500 mr-2 flex-shrink-0" />
                            <span>{feature}</span>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    )
}