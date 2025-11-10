/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#fef5ee',
          100: '#fce8d6',
          200: '#f8cdac',
          300: '#f3aa77',
          400: '#ed7c40',
          500: '#e8591a',
          600: '#d94210',
          700: '#b43210',
          800: '#902a15',
          900: '#742514',
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
