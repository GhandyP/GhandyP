/** Small, dependency-free enhancements for the portfolio site. */

document.documentElement.classList.add('js');

document.addEventListener('DOMContentLoaded', () => {
    initThemeToggle();
    initMobileMenu();
});

function initThemeToggle() {
    const button = document.querySelector('#theme-toggle');
    if (!button) return;
    const root = document.documentElement;
    let savedTheme = null;
    try { savedTheme = localStorage.getItem('theme'); } catch (error) { /* Storage may be unavailable. */ }
    const initialTheme = savedTheme || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    applyTheme(initialTheme);

    button.addEventListener('click', () => {
        const nextTheme = root.dataset.theme === 'dark' ? 'light' : 'dark';
        applyTheme(nextTheme);
        try { localStorage.setItem('theme', nextTheme); } catch (error) { /* Keep the toggle usable without storage. */ }
    });

    function applyTheme(theme) {
        root.dataset.theme = theme;
        button.textContent = theme === 'dark' ? '☀' : '◐';
        button.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
    }
}

function initMobileMenu() {
    const toggle = document.querySelector('.nav__toggle');
    const menu = document.querySelector('#primary-menu');
    if (!toggle || !menu) return;

    const closeMenu = () => {
        menu.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
    };
    toggle.addEventListener('click', () => {
        const isOpen = menu.classList.toggle('is-open');
        toggle.setAttribute('aria-expanded', String(isOpen));
    });
    menu.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
    document.addEventListener('keydown', event => {
        if (event.key === 'Escape' && menu.classList.contains('is-open')) {
            closeMenu();
            toggle.focus();
        }
    });
    document.addEventListener('click', event => {
        if (!menu.contains(event.target) && !toggle.contains(event.target)) closeMenu();
    });
}
