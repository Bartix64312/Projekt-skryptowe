import os

# --- KONFIGURACJA OPISÓW ---
# Mapuje nazwy plików/folderów na ich krótkie opisy
DESCRIPTIONS = {
    # ROOT
    ".env": "Zmienne środowiskowe (klucze, hasła)",
    "config.py": "Główna konfiguracja aplikacji Flask",
    "create_admin.py": "Skrypt do ręcznego tworzenia administratora",
    "verify_fix.py": "Weryfikacja poprawki błędu logów Windows",
    "debug_ssh_output.py": "Narzędzie debugowania SSH (zrzut raw log)",
    "generate_fail.py": "Generuje sztuczne nieudane logowania (Linux)",
    "generate_windows_fail.py": "Generuje sztuczne nieudane logowania (Windows)",
    "test_real_ssh_logs.py": "Test rzeczywistego połączenia SSH z Linuxem",
    "test_windows_logs.py": "Test pobierania logów lokalnych Windows",
    "test_windows_logs_mock.py": "Mock testów Windows (bez dostępu do API)",
    "verify_security.py": "Test bezpieczeństwa API (dostęp bez logowania)",
    "requirements.txt": "Lista zależności Python",
    "app": "Główny katalog aplikacji Flask",

    # APP
    "app/__init__.py": "Application Factory (start aplikacji)",
    "app/extensions.py": "Inicjalizacja rozszerzeń (DB, Login, CSRF)",
    "app/forms.py": "Definicje formularzy (Flask-WTF)",
    "app/models.py": "Modele bazy danych (User, Host, Alert...)",
    
    # SERVICES
    "app/services": "Logika biznesowa (Backend)",
    "app/services/log_collector.py": "Pobieranie logów (SSH/WinApi + Regex)",
    "app/services/remote_client.py": "Klient SSH (Paramiko)",
    "app/services/win_client.py": "Klient Windows (Subprocess/PowerShell)",
    "app/services/log_analyzer.py": "Analiza bezpieczeństwa (wykrywanie ataków)",
    "app/services/data_manager.py": "Warstwa zapisu danych (Parquet/ETL)",

    # BLUEPRINTS
    "app/blueprints": "Obsługa routingu HTTP",
    "app/blueprints/api": "API REST",
    "app/blueprints/api/hosts.py": "Endpoitny API (Hosty, Logi, Alerty)",
    "app/blueprints/auth.py": "Logowanie i wylogowywanie",
    "app/blueprints/ui.py": "Widoki HTML (Dashboard, Config)",
}

IGNORE_DIRS = {'.git', '__pycache__', '.venv', 'venv', 'instance', 'storage', '.vscode', '.idea', 'migrations'}
IGNORE_FILES = {'.gitignore', '.flaskenv'}

def print_tree(startpath, prefix=""):
    files = []
    dirs = []

    # Sortowanie zawartości
    try:
        entries = sorted(os.listdir(startpath))
    except PermissionError:
        return

    for entry in entries:
        if entry in IGNORE_DIRS or entry in IGNORE_FILES:
            continue
        
        full_path = os.path.join(startpath, entry)
        if os.path.isdir(full_path):
            dirs.append(entry)
        else:
            files.append(entry)

    # Łączymy listy: najpierw pliki, potem katalogi (lub odwrotnie, kwestia gustu - tutaj katalogi najpierw)
    all_entries = dirs + files
    
    for i, entry in enumerate(all_entries):
        is_last = (i == len(all_entries) - 1)
        connector = "└── " if is_last else "├── "
        
        rel_path = os.path.relpath(os.path.join(startpath, entry), os.getcwd()).replace("\\", "/")
        
        # Pobieranie opisu
        desc = DESCRIPTIONS.get(rel_path, "")
        if not desc and entry in DESCRIPTIONS: # Fallback dla nazw bez ścieżki (np w root)
             desc = DESCRIPTIONS[entry]

        # Formatowanie ikony
        icon = "📂" if entry in dirs else "📄"
        if entry.endswith(".py"): icon = "🐍"
        if entry == ".env": icon = "🔒"

        # Wypisywanie linii
        print(f"{prefix}{connector}{icon} {entry:<25} {(' # ' + desc) if desc else ''}")

        if entry in dirs:
            extension = "    " if is_last else "│   "
            print_tree(os.path.join(startpath, entry), prefix + extension)

if __name__ == "__main__":
    print("\n📦 STRUKTURA PROJEKTU BLUE-CTF\n")
    print_tree(os.getcwd())
    print("\n✅ Koniec prezentacji.\n")
