import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://mirastela.com',
  trailingSlash: 'ignore',
  devToolbar: { enabled: false },
  i18n: {
    locales: ['pl', 'hr', 'sl', 'ro', 'cs', 'hu', 'en'],
    defaultLocale: 'pl',
    routing: { prefixDefaultLocale: true, redirectToDefaultLocale: false },
  },
  vite: {
    server: { proxy: { '/api': 'http://127.0.0.1:8000' } },
  },
});
