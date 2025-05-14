// vite.config.js
import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    host: true,
    port: process.env.PORT || 3000,
    allowedHosts: ['carnival-oruro-astro.onrender.com'],
  },
});
