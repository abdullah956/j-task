// Validation script for frontend
import fs from 'fs';

console.log('='.repeat(80));
console.log('FRONTEND VALIDATION');
console.log('='.repeat(80));
console.log();

const requiredFiles = [
  'src/hooks/useWebSocket.js',
  'src/components/ChatWidget.jsx',
  'src/App.jsx',
  'src/main.jsx',
  'index.html',
  'package.json',
  'vite.config.js'
];

let allValid = true;

// Check all required files exist
console.log('Checking required files:');
console.log('-'.repeat(80));
requiredFiles.forEach(file => {
  const exists = fs.existsSync(file);
  console.log(`${exists ? '✅' : '❌'} ${file}`);
  if (!exists) allValid = false;
});

console.log();

// Check dependencies
console.log('Checking dependencies:');
console.log('-'.repeat(80));
const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
const requiredDeps = ['react', 'react-dom'];
const requiredDevDeps = ['vite', '@vitejs/plugin-react'];

requiredDeps.forEach(dep => {
  const exists = packageJson.dependencies && packageJson.dependencies[dep];
  console.log(`${exists ? '✅' : '❌'} ${dep} (dependency)`);
  if (!exists) allValid = false;
});

requiredDevDeps.forEach(dep => {
  const exists = packageJson.devDependencies && packageJson.devDependencies[dep];
  console.log(`${exists ? '✅' : '❌'} ${dep} (devDependency)`);
  if (!exists) allValid = false;
});

console.log();

// Check package.json scripts
console.log('Checking npm scripts:');
console.log('-'.repeat(80));
const requiredScripts = ['dev', 'build', 'preview'];
requiredScripts.forEach(script => {
  const exists = packageJson.scripts && packageJson.scripts[script];
  console.log(`${exists ? '✅' : '❌'} ${script}`);
  if (!exists) allValid = false;
});

console.log();
console.log('='.repeat(80));

if (allValid) {
  console.log('✅ ALL FRONTEND VALIDATION CHECKS PASSED!');
  console.log('='.repeat(80));
  console.log();
  console.log('To start the frontend development server:');
  console.log('  cd ai-support-agent/frontend');
  console.log('  npm run dev');
  console.log();
  console.log('The app will be available at: http://localhost:5173');
  console.log('='.repeat(80));
} else {
  console.log('❌ Some validation checks failed');
  process.exit(1);
}
