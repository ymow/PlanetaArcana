/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        tarot: {
          primary: '#4A148C',    // 深紫色
          secondary: '#7B1FA2',  // 紫色
          accent: '#CE93D8',     // 淺紫色
          dark: '#1A1A2E',       // 深色背景
          light: '#F5F5F5',      // 淺色背景
          gold: '#FFD700',       // 金色
        }
      },
      fontFamily: {
        serif: ['Georgia', 'serif'],
        mystical: ['Cinzel', 'serif'],
      }
    },
  },
  plugins: [],
}
