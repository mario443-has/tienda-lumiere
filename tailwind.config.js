/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html', // Plantillas Django
    './static/js/**/*.js',   // JS personalizados
    './store/templates/**/*.html',
    './static/css/**/*.css',
    './**/templates/**/*.html',

  ],
  safelist: [
    'product-badge',
    'badge-oferta',
    'badge-nuevo',
    'badge-tendencia'
  ],
  theme: {
    extend: {
      fontFamily: {
        inter: ['Inter', 'sans-serif'],
      },
      boxShadow: {
        top: '0 -4px 12px -2px rgba(0, 0, 0, 0.12)',
      },
    },
  },
  plugins: [],
};
