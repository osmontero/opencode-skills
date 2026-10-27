#!/usr/bin/env node
// init-artifact.cjs — cross-platform (no bash required) replacement for init-artifact.sh
// Usage: node scripts/init-artifact.cjs <project-name>
// Creates a React + Vite project with Tailwind + shadcn/ui preconfigured.
// Requires: node >= 18, and either pnpm (auto-installs via npm if missing).

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

const project = process.argv[2];
if (!project) fail('Usage: node scripts/init-artifact.cjs <project-name>');

const nodeMajor = parseInt(process.versions.node.split('.')[0], 10);
console.log('🔍 Detected Node.js version: ' + nodeMajor);
if (nodeMajor < 18) fail('Node.js 18 or higher is required (current: ' + process.versions.node + ')');

const viteVersion = nodeMajor >= 20 ? 'latest' : '5.4.11';
console.log('✅ Using Vite ' + viteVersion + (nodeMajor >= 20 ? ' (Node 20+)' : ' (Node 18 compatible)'));

// pnpm presence
try {
  execSync('pnpm --version', { stdio: 'ignore' });
} catch {
  console.log('📦 pnpm not found. Installing pnpm...');
  run('npm install -g pnpm');
}

const scriptDir = __dirname;
const componentsTarball = path.join(scriptDir, 'shadcn-components.tar.gz');
if (!fs.existsSync(componentsTarball)) {
  fail('shadcn-components.tar.gz not found in script directory.\n   Expected: ' + componentsTarball);
}

console.log('🚀 Creating new React + Vite project: ' + project);
run(`pnpm create vite ${project} --template react-ts`);

process.chdir(project);

// --- index.html tweaks (replaces sed) ---
console.log('🧹 Cleaning up Vite template...');
const indexHtml = path.resolve('index.html');
let html = fs.readFileSync(indexHtml, 'utf-8');
html = html.split('\n').filter((l) => !/<link rel="icon"[^>]*vite\.svg/.test(l)).join('\n');
html = html.replace(/<title>.*<\/title>/, `<title>${project}</title>`);
fs.writeFileSync(indexHtml, html);

console.log('📦 Installing base dependencies...');
run('pnpm install');

if (nodeMajor < 20) {
  console.log('📌 Pinning Vite to ' + viteVersion + ' for Node 18 compatibility...');
  run(`pnpm add -D vite@${viteVersion}`);
}

console.log('📦 Installing Tailwind CSS and dependencies...');
run('pnpm install -D tailwindcss@3.4.1 postcss autoprefixer @types/node tailwindcss-animate');
run('pnpm install class-variance-authority clsx tailwind-merge lucide-react next-themes');

console.log('⚙️  Creating Tailwind and PostCSS configuration...');
fs.writeFileSync('postcss.config.js', `export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
`);

console.log('📝 Configuring Tailwind with shadcn theme...');
fs.writeFileSync('tailwind.config.js', `/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
`);

console.log('🎨 Adding Tailwind directives and CSS variables...');
fs.writeFileSync('src/index.css', `@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 0 0% 3.9%;
    --card: 0 0% 100%;
    --card-foreground: 0 0% 3.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 0 0% 3.9%;
    --primary: 0 0% 9%;
    --primary-foreground: 0 0% 98%;
    --secondary: 0 0% 96.1%;
    --secondary-foreground: 0 0% 9%;
    --muted: 0 0% 96.1%;
    --muted-foreground: 0 0% 45.1%;
    --accent: 0 0% 96.1%;
    --accent-foreground: 0 0% 9%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 0 0% 98%;
    --border: 0 0% 89.8%;
    --input: 0 0% 89.8%;
    --ring: 0 0% 3.9%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 0 0% 3.9%;
    --foreground: 0 0% 98%;
    --card: 0 0% 3.9%;
    --card-foreground: 0 0% 98%;
    --popover: 0 0% 3.9%;
    --popover-foreground: 0 0% 98%;
    --primary: 0 0% 98%;
    --primary-foreground: 0 0% 9%;
    --secondary: 0 0% 14.9%;
    --secondary-foreground: 0 0% 98%;
    --muted: 0 0% 14.9%;
    --muted-foreground: 0 0% 63.9%;
    --accent: 0 0% 14.9%;
    --accent-foreground: 0 0% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 0 0% 98%;
    --border: 0 0% 14.9%;
    --input: 0 0% 14.9%;
    --ring: 0 0% 83.1%;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
`);

console.log('🔧 Adding path aliases to tsconfig.json...');
for (const tsconfig of ['tsconfig.json', 'tsconfig.app.json']) {
  if (!fs.existsSync(tsconfig)) continue;
  let raw = fs.readFileSync(tsconfig, 'utf-8');
  if (tsconfig === 'tsconfig.app.json') {
    raw = raw
      .split('\n')
      .filter((l) => !l.trim().startsWith('//'))
      .join('\n')
      .replace(/\/\*[\s\S]*?\*\//g, '')
      .replace(/,(\s*[}\]])/g, '$1');
  }
  const cfg = JSON.parse(raw);
  cfg.compilerOptions = cfg.compilerOptions || {};
  cfg.compilerOptions.baseUrl = '.';
  cfg.compilerOptions.paths = { '@/*': ['./src/*'] };
  fs.writeFileSync(tsconfig, JSON.stringify(cfg, null, 2));
}

console.log('⚙️  Updating Vite configuration...');
fs.writeFileSync('vite.config.ts', `import path from "path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
`);

console.log('📦 Installing shadcn/ui dependencies...');
run('pnpm install @radix-ui/react-accordion @radix-ui/react-aspect-ratio @radix-ui/react-avatar @radix-ui/react-checkbox @radix-ui/react-collapsible @radix-ui/react-context-menu @radix-ui/react-dialog @radix-ui/react-dropdown-menu @radix-ui/react-hover-card @radix-ui/react-label @radix-ui/react-menubar @radix-ui/react-navigation-menu @radix-ui/react-popover @radix-ui/react-progress @radix-ui/react-radio-group @radix-ui/react-scroll-area @radix-ui/react-select @radix-ui/react-separator @radix-ui/react-slider @radix-ui/react-slot @radix-ui/react-switch @radix-ui/react-tabs @radix-ui/react-toast @radix-ui/react-toggle @radix-ui/react-toggle-group @radix-ui/react-tooltip');
run('pnpm install sonner cmdk vaul embla-carousel-react react-day-picker react-resizable-panels date-fns react-hook-form @hookform/resolvers zod');

console.log('📦 Extracting shadcn/ui components...');
fs.mkdirSync('src', { recursive: true });
run(`tar -xzf "${componentsTarball}" -C src`);

console.log('📝 Creating components.json config...');
fs.writeFileSync('components.json', JSON.stringify({
  $schema: "https://ui.shadcn.com/schema.json",
  style: "default",
  rsc: false,
  tsx: true,
  tailwind: {
    config: "tailwind.config.js",
    css: "src/index.css",
    baseColor: "slate",
    cssVariables: true,
    prefix: ""
  },
  aliases: {
    components: "@/components",
    utils: "@/lib/utils",
    ui: "@/components/ui",
    lib: "@/lib",
    hooks: "@/hooks"
  }
}, null, 2));

console.log('✅ Setup complete! You can now use Tailwind CSS and shadcn/ui in your project.');
console.log('');
console.log('📦 Included components (40+ total):');
console.log('  - accordion, alert, aspect-ratio, avatar, badge, breadcrumb');
console.log('  - button, calendar, card, carousel, checkbox, collapsible');
console.log('  - command, context-menu, dialog, drawer, dropdown-menu');
console.log('  - form, hover-card, input, label, menubar, navigation-menu');
console.log('  - popover, progress, radio-group, resizable, scroll-area');
console.log('  - select, separator, sheet, skeleton, slider, sonner');
console.log('  - switch, table, tabs, textarea, toast, toggle, toggle-group, tooltip');
console.log('');
console.log('To start developing:');
console.log(`  cd ${project}`);
console.log('  pnpm dev');
console.log('');
console.log('📚 Import components like:');
console.log("  import { Button } from '@/components/ui/button'");
