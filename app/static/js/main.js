import { initDashboard } from './dashboard.js'; //import modułów
import { initAdmin } from './admin.js';


function setupThemeToggle() { //obsługa kliknięcia w przycisk 
    const btn = document.getElementById('themeToggle');
    if (!btn) return;

    btn.addEventListener('click', () => {
        const html = document.documentElement;
        const currentTheme = html.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark'; //domyslnie ciemny
        
        html.setAttribute('data-bs-theme', newTheme);
        localStorage.setItem('theme', newTheme); //ustawianie w local storage (zapamiętuje motyw)
        
        updateThemeIcon(newTheme);
    });

    // Ustawienie ikony na starcie
    const currentTheme = document.documentElement.getAttribute('data-bs-theme');
    updateThemeIcon(currentTheme);
}

function updateThemeIcon(theme) {
    const iconSpan = document.getElementById('themeIcon');
    if (iconSpan) {
        iconSpan.textContent = theme === 'dark' ? '🌙' : '☀️';
    }
}

function main() {
    setupThemeToggle();
    const path = window.location.pathname; //pobiera to co jest w pasku adresu po domenie

    if (path === '/' || path === '/index') {
        console.log("Inicjalizacja Dashboardu");
        initDashboard();
    } 
    else if (path === '/config') {
        console.log("Inicjalizacja Panelu Admina");
        initAdmin();
    }
}

main();