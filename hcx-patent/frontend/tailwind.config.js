/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      colors: {
        navy: {
          50: '#f0f3f9',
          100: '#dae1ef',
          200: '#b8c5de',
          300: '#8ea3c7',
          400: '#6680ac',
          500: '#4b6491',
          600: '#3b4f76',
          700: '#334060',
          800: '#1e293b',
          900: '#172033',
          950: '#0f172a',
        },
      },
    },
  },
  plugins: [],
};
