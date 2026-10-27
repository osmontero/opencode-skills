#!/usr/bin/env node
// find-polluter.cjs — cross-platform (no bash required) replacement for find-polluter.sh
// Bisection script to find which test creates unwanted files/state.
// Usage: node find-polluter.cjs <file_or_dir_to_check> <glob_pattern>
// Example: node find-polluter.cjs '.git' 'src/**/*.test.ts'
//
// Runs the project's test command once per matching test file (test command is
// configurable via the TEST_CMD env var, default "npm test") and stops at the
// first file that makes the pollution appear.
//
// Windows note: the "cat <test_file>" hint assumes a POSIX shell. On Windows use
// `Get-Content` (PowerShell) or read the file however the environment provides.

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

function walk(dir, pattern) {
  // Glob matching: ** spans directories, * spans within one segment.
  const out = [];
  const segments = pattern.split('/').filter(Boolean);
  const segRe = (s) =>
    s === '**' ? '.*' : s.replace(/\./g, '\\.').replace(/\*/g, '[^/]*');
  const re = new RegExp('^' + segments.map(segRe).join('/') + '$');
  const stack = [dir];
  while (stack.length) {
    const d = stack.pop();
    let entries;
    try {
      entries = fs.readdirSync(d, { withFileTypes: true });
    } catch {
      continue;
    }
    for (const e of entries) {
      const full = path.join(d, e.name);
      if (e.isDirectory()) {
        if (e.name === 'node_modules' || e.name === '.git') continue;
        stack.push(full);
      } else if (e.isFile()) {
        const rel = path.relative('.', full).split(path.sep).join('/');
        if (re.test(rel)) out.push(rel);
      }
    }
  }
  return out;
}

function describePollution(p) {
  const st = fs.statSync(p);
  if (!st.isDirectory()) return (st.size + ' bytes  ' + p);
  return fs.readdirSync(p).map((e) => {
    const est = fs.statSync(path.join(p, e));
    return (est.isDirectory() ? 'd' : '-') + ' ' + est.size + '  ' + e;
  }).join('\n');
}

function main() {
  const [pollutionCheck, testPattern] = process.argv.slice(2);
  if (!pollutionCheck || !testPattern) {
    console.error('Usage: node find-polluter.cjs <file_to_check> <test_pattern>');
    console.error("Example: node find-polluter.cjs '.git' 'src/**/*.test.ts'");
    process.exit(1);
  }

  const testCmd = process.env.TEST_CMD || 'npm test';
  console.log('🔍 Searching for test that creates: ' + pollutionCheck);
  console.log('Test pattern: ' + testPattern);
  console.log('Test command: ' + testCmd + ' <file>');
  console.log('');

  const testFiles = walk('.', testPattern).sort();
  const total = testFiles.length;
  console.log('Found ' + total + ' test files');
  console.log('');

  for (let i = 0; i < total; i++) {
    const testFile = testFiles[i];

    if (fs.existsSync(pollutionCheck)) {
      console.log('⚠️  Pollution already exists before test ' + (i + 1) + '/' + total);
      console.log('   Skipping: ' + testFile);
      continue;
    }

    console.log('[' + (i + 1) + '/' + total + '] Testing: ' + testFile);

    try {
      // testFile is slash-normalized by walk(); quote it so paths with spaces work.
      execSync(`${testCmd} "${testFile}"`, { stdio: 'ignore' });
    } catch {
      /* test may fail; we only care about the pollution side effect */
    }

    if (fs.existsSync(pollutionCheck)) {
      console.log('');
      console.log('🎯 FOUND POLLUTER!');
      console.log('   Test: ' + testFile);
      console.log('   Created: ' + pollutionCheck);
      console.log('');
      console.log('Pollution details:');
      console.log(describePollution(pollutionCheck));
      console.log('');
      console.log('To investigate:');
      console.log(`  ${testCmd} "${testFile}"    # Run just this test`);
      console.log(`  ${testFile}                 # Review test code`);
      process.exit(1);
    }
  }

  console.log('');
  console.log('✅ No polluter found - all tests clean!');
  process.exit(0);
}

main();
