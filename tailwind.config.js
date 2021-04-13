const defaultTheme = require('tailwindcss/defaultTheme');

module.exports = {
  purge: ['./src/**/*.html', './src/**/*.md'],
  darkMode: false,
  theme: {
    extend: {
      // fontFamily: {
      //   sans: [...defaultTheme.fontFamily.sans],
      // },
    },
  },
  variants: {},
  plugins: [require('@tailwindcss/typography')],
};