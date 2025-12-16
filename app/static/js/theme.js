
export function initTheme() {
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
        if (theme === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.documentElement.setAttribute('data-bs-theme', 'dark');
        } else {
            document.documentElement.setAttribute('data-bs-theme', theme);
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
        const currentTheme = getPreferredTheme();
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
    const btn = document.getElementById('bd-theme-toggle');
    if (btn) {
        btn.addEventListener('click', () => {
            toggleTheme();
        });
    }
}
