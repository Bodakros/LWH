module.exports = {
    content: [
        "./index.html",
        "./src/**/*.{js,jsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: {
                    DEFAULT: "#1a4f72",
                    foreground: "#ffffff",
                },
                secondary: {
                    DEFAULT: "#f39c12",
                    foreground: "#ffffff",
                },
                background: "#f5f7fa",
                foreground: "#333333",
                border: "#e2e8f0",
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
            },
        },
    },
    plugins: [],
}