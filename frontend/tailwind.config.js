/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Roboto Condensed"', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        heading: ['"Roboto Condensed"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        logistics: {
          black: '#080808',
          charcoal: '#171717',
          dark: '#1e1e1e',
          soft: '#F4F4F2',
          muted: '#777777',
          border: 'rgba(255, 255, 255, 0.15)',
        },
        lime: {
          DEFAULT: '#B7FF2A',
          400: '#B7FF2A',
          500: '#A4F51B',
          600: '#8CE00A',
          accent: '#B7FF2A',
        },
        navy: {
          50: '#f0f4f8',
          100: '#d9e2ec',
          200: '#bcccdc',
          300: '#9fb3c8',
          400: '#829ab1',
          500: '#627d98',
          600: '#486581',
          700: '#334e68',
          800: '#243b53',
          900: '#102a43',
          950: '#071626',
        },
      },
    },
  },
  plugins: [],
}
