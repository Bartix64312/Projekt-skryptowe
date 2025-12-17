
export function initTheme() {
    // CDN URLs
    const THEME_DARK = 'https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/vapor/bootstrap.min.css';
    const THEME_LIGHT = 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css';

    const getStoredTheme = () => localStorage.getItem('theme');
    const setStoredTheme = theme => localStorage.setItem('theme', theme);

    const getPreferredTheme = () => {
        const storedTheme = getStoredTheme();
        if (storedTheme) {
            return storedTheme;
        }
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    };

    const setTheme = theme => {
        const linkElement = document.getElementById('theme-css');
        if (linkElement) {
            if (theme === 'dark') {
                linkElement.setAttribute('href', THEME_DARK);
                document.documentElement.setAttribute('data-bs-theme', 'dark');
            } else {
                linkElement.setAttribute('href', THEME_LIGHT);
                document.documentElement.setAttribute('data-bs-theme', 'light');
            }
        }
    };

    const updateIcon = theme => {
        const icon = document.getElementById('theme-icon');
        if (!icon) return;

        icon.classList.remove('bi-sun-fill', 'bi-moon-fill');
        if (theme === 'dark') {
            icon.classList.add('bi-moon-fill');
        } else {
            icon.classList.add('bi-sun-fill');
        }
    };

    const toggleTheme = () => {
        const currentTheme = getStoredTheme() || getPreferredTheme();
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setStoredTheme(newTheme);
        setTheme(newTheme);
        updateIcon(newTheme);
    };

    // Initialize
    const savedTheme = getPreferredTheme();
    setTheme(savedTheme);
    updateIcon(savedTheme);

    // Event Listener
    // Wait for DOM in case script runs before button header
    document.addEventListener('DOMContentLoaded', () => {
        const btn = document.getElementById('bd-theme-toggle');
        if (btn) {
            btn.addEventListener('click', () => {
                toggleTheme();
            });
        } else {
            // Try explicit binding if element already exists (defer script)
            const btnNow = document.getElementById('bd-theme-toggle');
            if (btnNow) btnNow.addEventListener('click', toggleTheme);
        }
        updateIcon(savedTheme);
    });
}
