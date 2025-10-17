// script.js - Funcionalidades adicionales para la página

document.addEventListener('DOMContentLoaded', function() {
    // Funcionalidad del menú hamburguesa
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');

    if (hamburger && navMenu) {
        hamburger.addEventListener('click', function() {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
        });

        // Cerrar el menú al hacer clic en un enlace
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                hamburger.classList.remove('active');
                navMenu.classList.remove('active');
            });
        });
    }

    // Funcionalidad de anclaje suave para navegación
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80, // Compensar el header fijo
                    behavior: 'smooth'
                });
            }
        });
    });

    // Animaciones al hacer scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px"
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                
                // Animar las barras de progreso en la sección de habilidades
                if (entry.target.classList.contains('skills-container')) {
                    animateProgressBars();
                }
            }
        });
    }, observerOptions);

    // Observar elementos para animaciones
    document.querySelectorAll('.about-content, .skills-container, .projects-grid, .blog-grid, .contact-container').forEach(el => {
        observer.observe(el);
    });

    // Función para animar las barras de progreso
    function animateProgressBars() {
        const progressBars = document.querySelectorAll('.progress-level');
        progressBars.forEach(bar => {
            const level = bar.getAttribute('data-level');
            // Establecer la variable CSS para la animación
            bar.style.setProperty('--level', level + '%');
            setTimeout(() => {
                bar.style.width = level + '%';
            }, 300); // Pequeño retraso para asegurar la animación
        });
    }

    // Agregar efecto de animación en la sección hero
    const heroContent = document.querySelector('.hero-content');
    if (heroContent) {
        setTimeout(() => {
            heroContent.classList.add('fade-in-up');
        }, 300);
    }

    const heroImage = document.querySelector('.hero-image');
    if (heroImage) {
        setTimeout(() => {
            heroImage.classList.add('fade-in-up', 'delay-1');
        }, 500);
    }

        // Efecto de escritura en el título de la sección hero

        const heroTitle = document.querySelector('.hero-content h1');

        if (heroTitle) {

            const originalText = heroTitle.textContent;

            heroTitle.textContent = '';

            

            let i = 0;

            const typingEffect = setInterval(() => {

                if (i < originalText.length) {

                    heroTitle.textContent += originalText.charAt(i);

                    i++;

                } else {

                    clearInterval(typingEffect);

                }

            }, 100);

        }

    

            // Actualizar el año del copyright automáticamente

    

            const yearSpan = document.getElementById('current-year');

    

            if (yearSpan) {

    

                yearSpan.textContent = new Date().getFullYear();

    

            }

    

        

    

            // Lógica del Theme Switcher (Modo Oscuro)

    

            const themeToggle = document.getElementById('theme-toggle');

    

            const htmlEl = document.documentElement;

    

            const moonIcon = '<i class="fas fa-moon"></i>';

    

            const sunIcon = '<i class="fas fa-sun"></i>';

    

        

    

            // Función para cambiar el tema

    

            function switchTheme(theme) {

    

                htmlEl.setAttribute('data-theme', theme);

    

                localStorage.setItem('theme', theme);

    

                if (theme === 'dark') {

    

                    themeToggle.innerHTML = sunIcon;

    

                    themeToggle.setAttribute('aria-label', 'Switch to light mode');

    

                } else {

    

                    themeToggle.innerHTML = moonIcon;

    

                    themeToggle.setAttribute('aria-label', 'Switch to dark mode');

    

                }

    

            }

    

        

    

            // Evento al hacer clic en el botón

    

            themeToggle.addEventListener('click', () => {

    

                const currentTheme = htmlEl.getAttribute('data-theme') || 'light';

    

                const newTheme = currentTheme === 'light' ? 'dark' : 'light';

    

                switchTheme(newTheme);

    

            });

    

        

    

            // Cargar el tema guardado o preferido por el sistema

    

            const savedTheme = localStorage.getItem('theme');

    

            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    

        

    

            if (savedTheme) {

    

                switchTheme(savedTheme);

    

            } else if (prefersDark) {

    

                switchTheme('dark');

    

            }

    

        });

// Función para detectar si el usuario está en un dispositivo móvil
function isMobile() {
    return window.innerWidth <= 768;
}

// Ajustes para móviles
if (isMobile()) {
    // Ajustes específicos para móviles si es necesario
}