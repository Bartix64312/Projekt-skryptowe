import { initHosts } from './config_hosts.js';

function main() {
    const path = window.location.pathname;
    console.log("App initialized on path:", path);

    // Sprawdzamy, czy jesteśmy na widoku, który ma kontener hostów
    // (Dzięki temu unika błędów na podstronach bez tego elementu)
    if (document.getElementById('hostsContainer')) {
        initHosts();
    }
}

// Uruchamiamy aplikację
main();