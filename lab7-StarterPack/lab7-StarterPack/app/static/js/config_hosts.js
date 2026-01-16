import { createEl, clearContainer } from './dom.js';
import { fetchHosts, createHost, removeHost, checkHostStatus } from './api.js';

const hostsContainer = document.getElementById('hostsContainer');
const hostForm = document.getElementById('hostForm');

export async function initHosts() {
    if (!hostsContainer) return;

    if (hostForm) {
        hostForm.addEventListener('submit', handleAddHost);
    }

    await refreshHostsList();
}

async function refreshHostsList() {
    clearContainer(hostsContainer);
    try {
        const hosts = await fetchHosts();
        
        if (hosts.length === 0) {
            createEl('div', ['alert', 'alert-info'], 'Brak hostów w bazie. Dodaj pierwszy!', hostsContainer);
            return;
        }

        hosts.forEach(host => renderHostRow(host));

    } catch (err) {
        console.error(err);
        createEl('div', ['alert', 'alert-danger'], 'Błąd pobierania danych z API.', hostsContainer);
    }
}

/**
 * Rysuje wiersz hosta z zachowaniem sztywnej siatki kolumn
 */
function renderHostRow(host) {
    const item = createEl('div', ['list-group-item', 'py-3', 'border-bottom'], '', hostsContainer);
    
    // Używamy row + g-0 (brak marginesów) + flex-nowrap (jedna linia)
    const row = createEl('div', ['row', 'align-items-center', 'flex-nowrap', 'g-0'], '', item);
    
    // --- KOLUMNA 1: DANE (4/12) ---
    const colInfo = createEl('div', ['col-4', 'd-flex', 'align-items-center', 'overflow-hidden'], '', row);
    
    const iconChar = host.os_type === 'LINUX' ? '🐧' : '🪟';
    createEl('span', ['fs-2', 'me-2'], iconChar, colInfo);
    
    const details = createEl('div', ['d-flex', 'flex-column', 'w-100'], '', colInfo);
    createEl('div', ['fw-bold', 'text-truncate'], host.hostname, details); 
    createEl('small', ['text-muted', 'text-truncate'], host.ip_address, details);
    
    // --- KOLUMNA 2: STATUS (6/12) ---
    // To jest kluczowe: ta kolumna zawsze ma 50% szerokości listy.
    const colStatus = createEl('div', ['col-6', 'px-2'], '', row);
    
    // Placeholder
    createEl('div', ['text-muted', 'small', 'text-center', 'fst-italic'], 'Kliknij Sprawdź...', colStatus);

    // --- KOLUMNA 3: AKCJE (2/12) ---
    const colActions = createEl('div', ['col-2', 'text-end'], '', row);
    const btnGroup = createEl('div', ['btn-group', 'btn-group-sm'], '', colActions);
    
    const checkBtn = createEl('button', ['btn', 'btn-outline-primary'], 'Sprawdź', btnGroup);
    checkBtn.addEventListener('click', () => handleCheckStatusFancy(host, colStatus, checkBtn));
    
    const deleteBtn = createEl('button', ['btn', 'btn-outline-danger'], '✖', btnGroup);
    deleteBtn.title = "Usuń hosta";
    deleteBtn.addEventListener('click', () => handleDelete(host.id));
}

/**
 * Obsługa przycisku i renderowanie BADGES
 */
async function handleCheckStatusFancy(host, container, btn) {
    const originalText = btn.textContent;
    
    // Spinner w przycisku
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
    btn.disabled = true;

    clearContainer(container);
    // Loader w sekcji statusu
    createEl('div', ['text-muted', 'small', 'text-center'], 'Łączenie...', container);

    try {
        const data = await checkHostStatus(host.id, host.os_type);
        
        clearContainer(container);
        
        // Flexbox rozrzucający elementy
        const badgesRow = createEl('div', ['d-flex', 'justify-content-between', 'align-items-center', 'w-100'], '', container);

        // Dodajemy KAFELKI (Badges)
        // Kluczowe: renderujemy je w kontenerze o ustalonej szerokości, żeby były równo w pionie
        addBadge(badgesRow, 'RAM', `${data.free_ram_mb} MB`, 'text-success');
        addBadge(badgesRow, 'HDD', `${data.disk_info} / ${data.disk_total}`, 'text-warning');
        addBadge(badgesRow, 'CPU', data.cpu_load, 'text-info');
        addBadge(badgesRow, 'Uptime', data.uptime_hours, 'text-secondary');

        // Sukces - ikona odświeżania
        btn.innerHTML = '🔄'; 
        btn.title = "Odśwież status";

    } catch (err) {
        clearContainer(container);
        createEl('div', ['text-danger', 'small', 'fw-bold', 'text-center'], 'Błąd połączenia', container);
        console.error(err);
        btn.innerHTML = 'Ponów';
    } finally {
        btn.disabled = false;
    }
}

/**
 * Helper: Tworzy ładny KAFELEK (Badge)
 */
function addBadge(parent, label, value, colorClass) {
    // Stylizacja: ramka, zaokrąglenie, tło
    const box = createEl('div', ['text-center', 'border', 'rounded', 'bg-light', 'py-1'], '', parent);
    
    // KLUCZ DO WYRÓWNANIA:
    // Ustawiamy sztywną szerokość (width) na ok. 23% (bo mamy 4 elementy).
    // Dzięki temu każdy kafelek zajmie tyle samo miejsca w każdym wierszu.
    box.style.width = '24%'; 
    
    // Etykieta
    const lbl = createEl('div', ['text-muted', 'text-uppercase'], label, box);
    lbl.style.fontSize = '0.65rem';
    
    // Wartość
    const val = createEl('div', ['fw-bold', 'text-nowrap', colorClass], value || '?', box);
    val.style.fontSize = '0.8rem'; // Nieco mniejsza czcionka, żeby się mieściło
}

// --- Reszta bez zmian ---

async function handleAddHost(e) {
    e.preventDefault();
    const hostname = document.getElementById('hostname').value;
    const ip = document.getElementById('ip_address').value;
    const os = document.getElementById('os_type').value;

    try {
        await createHost({ hostname, ip_address: ip, os_type: os });
        e.target.reset();
        await refreshHostsList();
    } catch (err) {
        alert(err.message);
    }
}

async function handleDelete(id) {
    if(confirm("Czy na pewno usunąć tego hosta z monitoringu?")) {
        await removeHost(id);
        await refreshHostsList();
    }
}