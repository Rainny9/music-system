import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    allowedHosts: [
      '20833af0.r25.cpolar.top',  // 前端 cpolar 地址
      '.cpolar.top'               // 允许所有 cpolar 子域名
    ]
  }
})
