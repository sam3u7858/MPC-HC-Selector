// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },
  
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt'
  ],

  css: [
    '@/assets/css/main.css'
  ],

  app: {
    head: {
      title: 'Clip Marker',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'Professional video clip marking tool' }
      ],
      link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;600;700&display=swap' }
      ]
    }
  },

  runtimeConfig: {
    public: {
      apiBase: process.env.API_BASE || 'http://localhost:5000',
      isElectron: process.env.NUXT_IS_ELECTRON === 'true'
    }
  },

  ssr: false,

  generate: {
    dir: 'dist'
  },

  vite: {
    define: {
      global: 'globalThis'
    }
  }
}) 