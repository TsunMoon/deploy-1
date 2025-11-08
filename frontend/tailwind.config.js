/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        netflix: {
          red: '#E50914',
          darkRed: '#831010',
          black: '#141414',
          darkGray: '#2F2F2F',
          mediumGray: '#808080',
          lightGray: '#B3B3B3',
          offWhite: '#F5F5F1',
        },
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        }
      }
    },
  },
  plugins: [],
};