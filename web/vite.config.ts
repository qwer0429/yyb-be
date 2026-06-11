import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

const SERVICE_HOST = process.env.SERVICE_HOST || 'localhost'
const BACKEND_PORT = process.env.BACKEND_PORT || '8000'
const ADMIN_PORT = process.env.ADMIN_PORT || '5173'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: parseInt(ADMIN_PORT),
    host: true,
    proxy: {
      '/api': {
        target: `http://${SERVICE_HOST}:${BACKEND_PORT}`,
        changeOrigin: true,
      },
      '/syyb': {
        target: `http://${SERVICE_HOST}:${BACKEND_PORT}`,
        changeOrigin: true,
      },
      '/susers': {
        target: `http://${SERVICE_HOST}:${BACKEND_PORT}`,
        changeOrigin: true,
      },
      '/media': {
        target: `http://${SERVICE_HOST}:${BACKEND_PORT}`,
        changeOrigin: true,
      },
      // '/users' 代理已移除，前端统一使用 '/susers' 路径
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    rollupOptions: {
      output: {
        chunkFileNames: 'js/[name]-[hash].js',
        entryFileNames: 'js/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          const name = assetInfo.name || ''
          const info = name.split('.')
          const ext = info[info.length - 1]
          if (/\.(png|jpe?g|gif|svg|webp|ico)$/i.test(name)) {
            return 'img/[name]-[hash][extname]'
          }
          if (/\.(woff2?|eot|ttf|otf)$/i.test(name)) {
            return 'fonts/[name]-[hash][extname]'
          }
          return '[ext]/[name]-[hash][extname]'
        }
      }
    }
  }
})
