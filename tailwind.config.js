/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './app/templates/**/*.html',
    './app/static/**/*.js'
  ],
  theme: {
    extend: {
      colors: {
        'error-container': '#93000a',
        'secondary': '#fbb79a',
        'surface-container-low': '#181c23',
        'tertiary': '#72d2fb',
        'surface-tint': '#ffb596',
        'on-primary-container': '#4d1900',
        'on-error-container': '#ffdad6',
        'error': '#ffb4ab',
        'primary': '#ffb596',
        'surface': '#0f131b',
        'on-tertiary-container': '#002e3d',
        'inverse-primary': '#a0410e',
        'surface-container': '#1c2027',
        'on-surface': '#dfe2ec',
        'surface-container-highest': '#31353d',
        'outline-variant': '#56423a',
        'on-surface-variant': '#ddc1b6',
        'primary-container': '#e1713d',
        'surface-variant': '#31353d',
        'on-error': '#690005',
        'surface-bright': '#353941',
        'on-primary-fixed-variant': '#7d2d00',
        'inverse-on-surface': '#2d3038',
        'secondary-fixed': '#ffdbcd',
        'on-tertiary-fixed': '#001f2a',
        'surface-dim': '#0f131b',
        'on-secondary-container': '#e8a68a',
        'on-primary': '#581e00',
        'secondary-container': '#693a25',
        'on-primary-fixed': '#360f00',
        'tertiary-fixed-dim': '#72d2fb',
        'on-tertiary-fixed-variant': '#004d64',
        'background': '#0f131b',
        'tertiary-container': '#319bc2',
        'on-secondary-fixed-variant': '#693a25',
        'tertiary-fixed': '#bee9ff',
        'surface-container-high': '#262a32',
        'primary-fixed-dim': '#ffb596',
        'on-tertiary': '#003546',
        'outline': '#a58b81',
        'on-secondary': '#4e2511',
        'inverse-surface': '#dfe2ec',
        'on-secondary-fixed': '#341102',
        'on-background': '#dfe2ec',
        'surface-container-lowest': '#0a0e15',
        'primary-fixed': '#ffdbcd',
        'secondary-fixed-dim': '#fbb79a'
      },
      fontFamily: {
        'headline': ['Inter', 'sans-serif'],
        'body': ['Inter', 'sans-serif'],
        'label': ['Inter', 'sans-serif']
      },
      borderRadius: {
        'DEFAULT': '0.125rem',
        'lg': '0.25rem',
        'xl': '0.5rem',
        'full': '0.75rem'
      }
    }
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/container-queries')
  ]
}
