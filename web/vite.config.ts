import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/api': {
        target: 'http://192.168.50.82:8000',
        changeOrigin: true,
      },
      '/syyb': {
        target: 'http://192.168.50.82:8000',
        changeOrigin: true,
      },
      '/susers': {
        target: 'http://192.168.50.82:8000',
        changeOrigin: true,
      },
      '/media': {
        target: 'http://192.168.50.82:8000',
        changeOrigin: true,
      },
      '/users': {
        target: 'http://192.168.50.82:8000',
        changeOrigin: true,
        rewrite: (path) => '/susers' + path
      }
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
          const info = assetInfo.name.split('.')
          const ext = info[info.length - 1]
          if (/\.(png|jpe?g|gif|svg|webp|ico)$/i.test(assetInfo.name)) {
            return 'img/[name]-[hash][extname]'
          }
          if (/\.(woff2?|eot|ttf|otf)$/i.test(assetInfo.name)) {
            return 'fonts/[name]-[hash][extname]'
          }
          return '[ext]/[name]-[hash][extname]'
        }
      }
    }
  }
})
