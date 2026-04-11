import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          50:  '#e7e9f0',
          100: '#c3c8db',
          200: '#9ba4c4',
          300: '#7280ac',
          400: '#54639a',
          500: '#364789',
          600: '#2e3d7a',
          700: '#243167',
          800: '#1a2554',
          900: '#0d1535',
          950: '#080d22',
        },
        brand: {
          blue:    '#2563eb',
          indigo:  '#4f46e5',
          purple:  '#7c3aed',
          cyan:    '#06b6d4',
          teal:    '#0d9488',
        },
        surface: {
          DEFAULT: '#111827',
          card:    '#1f2937',
          border:  '#374151',
          hover:   '#374151',
          input:   '#1f2937',
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic':
          'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'gradient-brand':
          'linear-gradient(135deg, #2563eb 0%, #4f46e5 50%, #7c3aed 100%)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow':  'spin 3s linear infinite',
        'fade-in':    'fadeIn 0.3s ease-in-out',
        'slide-up':   'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%':   { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%':   { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)',    opacity: '1' },
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        card:  '0 4px 6px -1px rgba(0,0,0,0.3), 0 2px 4px -2px rgba(0,0,0,0.3)',
        glow:  '0 0 20px rgba(37,99,235,0.3)',
        'glow-purple': '0 0 20px rgba(124,58,237,0.3)',
      },
    },
  },
  plugins: [],
}
export default config
