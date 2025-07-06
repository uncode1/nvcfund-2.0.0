/**
 * Webpack Development Server Configuration Override
 * Completely disables error overlays and compilation error exposure
 */

const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Proxy API requests to backend
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:5000',
      changeOrigin: true,
      secure: false,
      logLevel: 'silent'
    })
  );

  // Override webpack dev server configuration
  if (process.env.NODE_ENV === 'development') {
    // Disable error overlay completely
    const originalBefore = app.use;
    app.use = function(path, ...args) {
      if (typeof path === 'string' && path.includes('sockjs-node')) {
        return; // Block webpack dev server error overlay
      }
      return originalBefore.apply(this, arguments);
    };
  }
};