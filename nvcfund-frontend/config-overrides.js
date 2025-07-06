module.exports = function override(config, env) {
  // Override webpack dev server config to disable host checking
  return {
    ...config,
    devServer: {
      ...config.devServer,
      allowedHosts: 'all',
      host: '0.0.0.0',
      port: 3000,
      disableHostCheck: true
    }
  };
};