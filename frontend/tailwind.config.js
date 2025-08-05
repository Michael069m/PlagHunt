/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        black: '#000000',
        yellow: {
          400: '#FBBF24',
          500: '#F59E0B',
          600: '#D97706',
        },
        red: {
          400: '#F87171',
          500: '#EF4444',
          600: '#DC2626',
        },
        gray: {
          800: '#1F2937',
          900: '#111827',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
