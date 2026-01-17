# AGENTS.md - Guidelines for AI Coding Agents

## Project Overview
Personal portfolio website for Martin Ghandy Prieto, Infrastructure & DevOps Engineer.
Built with vanilla HTML/CSS/JS, optimized for free GitHub Pages hosting.
Target audience: Insurance/Finance/Enterprise companies seeking infrastructure expertise.

## Tech Stack
- HTML5 semántico
- CSS3 con Custom Properties (no frameworks, no preprocessors)
- JavaScript ES6+ (vanilla)
- Font Awesome CDN para iconos
- Google Fonts (Inter, JetBrains Mono)

## Build/Lint/Test Commands

### Development
```bash
# Servir localmente para testing
npx serve .                    # Con npx serve
python3 -m http.server 8000    # Con Python

# Live reload
npx live-server .
```

### Validation
```bash
# HTML validation
npx htmlhint index.html

# CSS linting
npx stylelint style.css --fix

# JS linting
npx eslint script.js --fix

# Verificar enlaces
npx check-html-links index.html

# Lighthouse CI
npx lhci autorun
```

### Production Build
```bash
# Minificar CSS
npx cleancss -o style.min.css style.css

# Minificar JS
npx terser script.js -o script.min.js -c -m

# Generar favicons
npx favicons --logo=assets/logo.png

# Comprimir imágenes
npx imagemin assets/images/* --out-dir=assets/images optimized/
```

### Testing
```bash
# Test responsive (viewport sizes)
npx cypress open

# Accessibility testing
npx axe-cli index.html

# Performance testing
npx pagespeed --url=https://ghandyp.github.io
```

## Code Style Guidelines

### HTML
- Usar elementos semánticos: <header>, <nav>, <main>, <section>, <article>, <footer>
- Atributos ordenados: class, id, data-*, src/href, alt, aria-*
- Indentación: 4 espacios
- Comentarios: <!-- section-name --> para secciones principales
- Alt text obligatorio para imágenes

### CSS
- Custom Properties (variables CSS) para colores, espaciados, tipografía
- Mobile-first: @media (min-width: 768px) { ... }
- BEM naming: .block__element--modifier
- Unidades: rem para tipografía, px para borders, % para layouts
- Evitar: !important, IDs para styling, magic numbers
- Prefijos: -webkit- para propiedades nuevas si es necesario

### JavaScript
- ES6+: const/let, arrow functions, template literals, destructuring
- Nombres: camelCase para variables, PascalCase para clases
- Funciones pequeñas (max 20-30 líneas)
- Comentarios JSDoc para funciones públicas
- Event delegation para múltiples elementos similares
- Manejo de errores: try/catch con fallback graceful
- No console.log en producción

### Git/Commits
- Conventional commits: feat:, fix:, refactor:, docs:, style:, perf:
- Branch naming: feature/description, fix/issue-number
- PRs requeridos para main branch
- Squash commits antes de merge

## Project Structure

```
/
├── index.html              # Main page (single page application feel)
├── style.css               # Main styles
├── script.js               # Main JS (animations, theme toggle)
├── assets/
│   ├── icons/             # SVG icons inline preferred
│   └── images/            # Optimized images (WebP, AVIF)
├── .github/
│   └── workflows/
│       └── deploy.yml     # GitHub Pages CI/CD
├── robots.txt
└── sitemap.xml
```

## GitHub Pages Specific

### Deployment
- Source: Deploy from main branch
- Build command: N/A (static files)
- Publish directory: / (root)

### Optimizations Required
- CDN links para fuentes (fonts.googleapis.com)
- CDN links para iconos (cdnjs.cloudflare.com)
- Minificar assets antes de commit (CSS < 50KB, JS < 30KB)
- Cache headers: 1 year para assets inmutables
- Compress: gzip via .htaccess

### Allowed External Services
- Font Awesome CDN (iconos)
- Google Fonts (Inter, JetBrains Mono)
- Formspree (formulario de contacto)
- Plausible Analytics (opcional, privacy-first)

## Performance Budget
- First Contentful Paint: < 1.5s
- Lighthouse Score: > 90 en Performance, Accessibility, Best Practices
- CSS bundle: < 50KB
- JS bundle: < 30KB
- Total page weight (sin imágenes): < 100KB

## Accessibility (WCAG 2.1 AA)
- Contrast ratio: 4.5:1 minimum para texto
- Focus indicators: Visibles y claros
- Keyboard navigation: Todos los elementos alcanzables
- ARIA labels: Donde el propósito no sea evidente
- Alt text: Para todas las imágenes
- Reduced motion: Respetar prefers-reduced-motion
- Skip links: Incluir skip to main content

## Design System

### Colors (Anthropic-inspired)
- bg-primary: #FAFAFA (warm white)
- bg_secondary: #F5F5F5
- text_primary: #1A1A1A
- text_secondary: #666666
- accent_primary: #D4A574 (warm terracotta)
- accent_secondary: #6B8E7B (sage green)

### Typography
- Headings: Inter, weight 600-700
- Body: Inter, weight 400-500
- Code: JetBrains Mono, weight 400

### Spacing Scale
- xs: 0.25rem, sm: 0.5rem, md: 1rem, lg: 1.5rem, xl: 2rem, 2xl: 3rem

### Border Radius
- Small: 4px, Medium: 8px, Large: 12px

### Animations
- Transition: 0.2s ease-out
- Fade in: 0.4s ease
- No parallax, no heavy animations

## Content Guidelines

### Tono
- Profesional pero accesible
- Técnico pero no intimidante
- Confiado sin ser arrogante
- Enfoque en resultados y impacto

### Secciones Requeridas
1. Hero (name, title, tagline, CTAs)
2. About (2-3 sentences)
3. Experience (timeline, 3 roles)
4. Core Competencies (6-8 skills)
5. Technical Stack (keywords/tags)
6. Certifications (3-4 cards)
7. Projects (3-4 highlight cards)
8. Contact (email, links, form)

### Información Personal Actual
- Name: Martin Ghandy Prieto Rodriguez
- Email: info@gandyit.com
- Phone: +58 424 334 4545
- Location: Maracay, Venezuela (Available: Remote, Caracas)
- LinkedIn: linkedin.com/in/martin-prieto-564253a9
- GitHub: github.com/GhandyP
