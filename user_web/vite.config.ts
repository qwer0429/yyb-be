import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

const SERVICE_HOST = process.env.SERVICE_HOST || 'localhost'
const BACKEND_PORT = process.env.BACKEND_PORT || '8000'
const USER_PORT = process.env.USER_PORT || '3001'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: parseInt(USER_PORT),
    host: true,
    proxy: {
      '/api': {
        target: `http://${SERVICE_HOST}:${BACKEND_PORT}`,
        changeOrigin: true
      },
      '/syyb': {
        target: `http://${SERVICE_HOST}:${BACKEND_PORT}`,
        changeOrigin: true
      }
    }
  }
})
