/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        axon: {
          dark: '#0a0a0f',
          card: '#0d0d14',
          border: '#1e1e2e',
          purple: '#7c3aed',
          cyan: '#06b6d4',
        },
      },
    },
  },
  plugins: [],
}
