const { spawn } = require('child_process');
const path = require('path');

// Set environment variables to fix host header issue
process.env.DANGEROUSLY_DISABLE_HOST_CHECK = 'true';
process.env.HOST = '0.0.0.0';
process.env.PORT = '3000';
process.env.BROWSER = 'none';
process.env.REACT_APP_API_URL = 'http://localhost:5000';

console.log('Starting React with fixed host configuration...');
console.log('Host: 0.0.0.0:3000');
console.log('Host check: disabled');

// Start react-scripts with proper environment
const reactProcess = spawn('npx', ['react-scripts', 'start'], {
  stdio: 'inherit',
  env: process.env,
  cwd: __dirname
});

reactProcess.on('error', (error) => {
  console.error('Failed to start React:', error);
});

reactProcess.on('close', (code) => {
  console.log(`React process exited with code ${code}`);
});

process.on('SIGINT', () => {
  console.log('Stopping React development server...');
  reactProcess.kill();
});