/**
 * Wrapper na Fetch API do komunikacji z backendem Flask
 */

export async function fetchHosts() {
    const res = await fetch('/api/hosts');
    return await res.json();
}

export async function createHost(hostData) {
    const res = await fetch('/api/hosts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(hostData)
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || 'Błąd dodawania hosta');
    }
    return await res.json();
}

export async function removeHost(id) {
    const res = await fetch(`/api/hosts/${id}`, {
        method: 'DELETE'
    });
    return res.ok;
}

export async function checkHostStatus(id, osType) {
    // ZMIANA: Dostosowanie endpointów do nowej logiki w hosts.py
    const endpoint = (osType === 'LINUX') 
        ? `/api/hosts/${id}/ssh-info` 
        : `/api/hosts/${id}/windows-info`;
        
    const res = await fetch(endpoint);
    // Obsługa błędów HTTP (np. 500 SSH Error)
    if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.error || `Błąd HTTP ${res.status}`);
    }
    return await res.json();
}