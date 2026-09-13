import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// dev 서버는 5173, /api 요청은 백엔드(8000)로 프록시
// 이렇게 하면 프론트 코드에서 `fetch('/api/...')` 식으로 짧게 호출 가능
// + CORS 이슈도 dev 환경에서 우회됨
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
});
