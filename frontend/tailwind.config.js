/** @type {import('tailwindcss').Config} */
export default {
    content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
    theme: {
        extend: {
            colors: {
                // Deep blues from the design
                'midnight': '#003366',
                'navy': '#000080',
                'prussian': '#003153',
                // Charcoal blacks from the design
                'charcoal': {
                    DEFAULT: '#36454F',
                    'dark': '#2A2A2A',
                    'jet': '#343434'
                },
                // Metallic silvers from the design
                'silver': {
                    DEFAULT: '#C0C0C0',
                    'light': '#E8E8E8',
                    'metallic': '#AAA9AD'
                }
            },
            backgroundImage: {
                'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
                'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
            }
        },
    },
    plugins: [],
};