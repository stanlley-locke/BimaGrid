/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        bima: {
          green: '#5A8855', // Primary button color
          darkGreen: '#3A5A40', // Text color
          lightGreen: '#C8E6C9', // Badges
          yellow: '#EAD35B', // Accent color
          lightYellow: '#F9F1C7', // Secondary badge
          cream: '#F4F1ED', // Body background
          offWhite: '#FAF9F6', // Cards
        },
      },
      fontFamily: {
        sans: ['Outfit', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        '2xl': '1.5rem',
        '3xl': '2rem',
      },
    },
  },
  plugins: [],
};
