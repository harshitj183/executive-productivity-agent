/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: '#12141a',
          50: '#f4f5f6',
          100: '#e6e8eb',
          200: '#c8ccd2',
          300: '#9aa0a8',
          400: '#6f7680',
          500: '#4a5058',
          600: '#2e333b',
          700: '#22262e',
          800: '#1a1e26',
          900: '#12141a',
          950: '#0c0e12',
        },
        brass: {
          50: '#faf6f0',
          100: '#f0e6d6',
          200: '#e0c9a8',
          300: '#d0ad7e',
          400: '#c49a62',
          500: '#b8956c',
          600: '#9a7a54',
          700: '#7a6042',
          800: '#5c4834',
          900: '#3d3024',
        },
        surface: {
          DEFAULT: '#12141a',
          1: '#16191f',
          2: '#1c2028',
          3: '#242933',
        },
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'monospace'],
      },
      borderRadius: {
        DEFAULT: '0.5rem',
        lg: '0.625rem',
        xl: '0.75rem',
      },
      boxShadow: {
        soft: '0 1px 2px rgba(0,0,0,0.24), 0 4px 12px rgba(0,0,0,0.18)',
        lift: '0 -1px 0 rgba(255,255,255,0.04), 0 -8px 24px rgba(0,0,0,0.35)',
      },
      transitionTimingFunction: {
        smooth: 'cubic-bezier(0.22, 1, 0.36, 1)',
      },
    },
  },
  plugins: [],
}
