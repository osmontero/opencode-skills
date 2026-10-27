#!/usr/bin/env node
// bundle-artifact.cjs — cross-platform (no bash required) replacement for bundle-artifact.sh
// Usage: node scripts/bundle-artifact.cjs   (run from the project root)
// Bundles the React app into a single self-contained bundle.html.

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

function run(cmd, opts = {}) {
  console.log('$ ' + cmd);
  execSync(cmd, { stdio: 'inherit', ...opts });
}

function fail(msg) {
  console.error('❌ ' + msg);
  process.exit(1);
}

if (!fs.existsSync('package.json')) fail('No package.json found. Run this from your project root.');
if (!fs.existsSync('index.html')) {
  fail('No index.html found in project root.\n   This script requires an index.html entry point.');
}

console.log('📦 Installing bundling dependencies...');
run('pnpm add -D parcel @parcel/config-default parcel-resolver-tspaths html-inline');

if (!fs.existsSync('.parcelrc')) {
  console.log('🔧 Creating Parcel configuration with path alias support...');
  fs.writeFileSync('.parcelrc', JSON.stringify({
    extends: "@parcel/config-default",
    resolvers: ["parcel-resolver-tspaths", "..."]
  }, null, 2) + '\n');
}

console.log('🧹 Cleaning previous build...');
fs.rmSync('dist', { recursive: true, force: true });
fs.rmSync('bundle.html', { force: true });

console.log('🔨 Building with Parcel...');
run('pnpm exec parcel build index.html --dist-dir dist --no-source-maps');

console.log('🎯 Inlining all assets into single HTML file...');
const inlined = execSync('pnpm exec html-inline dist/index.html', { encoding: 'utf-8' });
fs.writeFileSync('bundle.html', inlined);

const sizeKb = (fs.statSync('bundle.html').size / 1024).toFixed(1);
console.log('');
console.log('✅ Bundle complete!');
console.log(`📄 Output: bundle.html (${sizeKb} KB)`);
console.log('');
console.log('You can now use this single HTML file as an artifact as a standalone HTML file.');
console.log('To test locally: open bundle.html in your browser');
