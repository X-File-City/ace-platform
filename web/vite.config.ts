import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Proxy configuration for API routes
// Only proxy XHR/fetch requests, not browser navigation requests
const apiProxyConfig = {
  target: 'http://localhost:8000',
  changeOrigin: true,
  // Bypass proxy for document requests (browser navigation/refresh)
  // These should be handled by the SPA, not forwarded to the API
  bypass: (req: { headers: { accept?: string } }) => {
    // If the request accepts HTML, it's a browser navigation - let Vite handle it
    if (req.headers.accept?.includes('text/html')) {
      return '/index.html'
    }
    // Otherwise, proxy to the API
    return null
  },
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/auth': apiProxyConfig,
      '/playbooks': apiProxyConfig,
      '/usage': apiProxyConfig,
      '/billing': apiProxyConfig,
      '/health': apiProxyConfig,
      '/ready': apiProxyConfig,
    },
  },
})
