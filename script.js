/** Small, dependency-free enhancements for the portfolio site. */

const THEME_STORAGE_KEY = "theme";

document.documentElement.classList.add("js");

document.addEventListener("DOMContentLoaded", () => {
    initThemeToggle();
    initMobileMenu();
});

function initThemeToggle() {
    const button = document.querySelector("#theme-toggle");
    if (!button) return;

    const root = document.documentElement;
    const icon = button.querySelector(".theme-toggle__icon");
    const savedTheme = readStoredTheme();
    const initialTheme = savedTheme || getSystemTheme();

    applyTheme(initialTheme);
    button.addEventListener("click", () => {
        const nextTheme = root.dataset.theme === "dark" ? "light" : "dark";
        applyTheme(nextTheme);
        storeTheme(nextTheme);
    });

    function applyTheme(theme) {
        root.dataset.theme = theme;
        const isDark = theme === "dark";
        const label = isDark ? "Switch to light mode" : "Switch to dark mode";
        button.setAttribute("aria-label", label);
        button.setAttribute("title", label);
        if (icon) icon.textContent = isDark ? "☀" : "◐";
    }
}

function readStoredTheme() {
    try {
        const theme = localStorage.getItem(THEME_STORAGE_KEY);
        return theme === "dark" || theme === "light" ? theme : null;
    } catch {
        return null;
    }
}

function storeTheme(theme) {
    try {
        localStorage.setItem(THEME_STORAGE_KEY, theme);
    } catch {
        // The toggle remains usable when storage is unavailable.
    }
}

function getSystemTheme() {
    try {
        return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    } catch {
        return "light";
    }
}

function initMobileMenu() {
    const toggle = document.querySelector(".nav__toggle");
    const menu = document.querySelector("#primary-menu");
    if (!toggle || !menu) return;

    setMenuState(false);
    toggle.addEventListener("click", () => {
        const isOpen = toggle.getAttribute("aria-expanded") === "true";
        setMenuState(!isOpen, { focusFirst: !isOpen });
    });
    menu.querySelectorAll("a").forEach(link => link.addEventListener("click", closeMenu));
    document.addEventListener("keydown", handleMenuKeydown);
    document.addEventListener("click", handleOutsideClick);

    function closeMenu() {
        setMenuState(false);
    }

    function handleMenuKeydown(event) {
        if (event.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
            setMenuState(false);
            toggle.focus();
        }
    }

    function handleOutsideClick(event) {
        if (!menu.contains(event.target) && !toggle.contains(event.target)) closeMenu();
    }

    function setMenuState(isOpen, options = {}) {
        menu.classList.toggle("is-open", isOpen);
        toggle.setAttribute("aria-expanded", String(isOpen));
        toggle.setAttribute("aria-label", isOpen ? "Close navigation" : "Open navigation");
        const icon = toggle.querySelector(".nav__toggle-icon");
        const hiddenLabel = toggle.querySelector(".sr-only");
        if (icon) icon.textContent = isOpen ? "×" : "☰";
        if (hiddenLabel) hiddenLabel.textContent = isOpen ? "Close navigation" : "Open navigation";
        if (isOpen && options.focusFirst) menu.querySelector("a")?.focus();
    }
}
