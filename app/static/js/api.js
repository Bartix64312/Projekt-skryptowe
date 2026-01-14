function getCsrfToken() { //pomocnicza do pobierania tokena CSRF
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
}

async function secureFetch(url, options = {}) {
    const headers = { //nagłówki HTTP
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
        ...options.headers
    };

    const response = await fetch(url, { ...options, headers });

    if (response.status === 401) {
        throw new Error('401: Wymagane logowanie');
    }

    if(!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.error || `Błąd HTTP ${response.status}`);
    }
    return response.json();
}

// HOSTS
export async function fetchHosts() {
    return await secureFetch('/api/hosts');
}
export async function createHost(data) {
    return await secureFetch('/api/hosts', {
        method: 'POST',
        body: JSON.stringify(data)
    });
}
export async function updateHost(id, data) {
    return await secureFetch(`/api/hosts/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
    });
}
export async function removeHost(id) {
    return await secureFetch(`/api/hosts/${id}`, {
        method: 'DELETE'
    });
}

//MONITORING I LOGI
export async function checkHostStatus(id, osType) { //sprawdzanie statusu
    const endpoint = (osType === 'LINUX') 
        ? `/api/hosts/${id}/ssh-info` 
        : `/api/hosts/${id}/windows-info`;
        
    return await secureFetch(endpoint);
}

export async function triggerLogFetch(hostId) { //pobieranie logów
    return await secureFetch(`/api/hosts/${hostId}/logs`, {
        method: 'POST'
    });
}

// IP zarejestrowane 
export async function fetchIPs() { 
    return await secureFetch('/api/ips');
}

export async function createIP(data) {
    return await secureFetch('/api/ips', {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

export async function updateIP(id, data) {
    return await secureFetch(`/api/ips/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

export async function removeIP(id) {
    const res = await secureFetch(`/api/ips/${id}`, { 
        method: 'DELETE' 
    });
}

//ALERTY
export async function fetchAlerts() {
    return await secureFetch('/api/alerts');
}

export async function fetchAlertStats() {
    return await secureFetch('/api/stats/alerts');
}