# mini-SIEM (Security Information & Event Management)

## Opis Projektu
Funkcjonalny prototyp systemu SIEM zaprojektowany do monitorowania bezpieczeństwa infrastruktury, gromadzenia logów oraz wykrywania incydentów w czasie rzeczywistym. System oparty jest na architekturze Klient-Serwer z wykorzystaniem frameworka Flask (Backend) oraz Vanilla JS (Frontend).

Kluczowe zaimplementowane funkcje:
*   **Defense in Depth**: Zabezpieczenie aplikacji poprzez haszowanie haseł (`werkzeug.security`), system uwierzytelniania oparty na `flask_login` oraz ścisłą kontrolę dostępu do API przy użyciu dekoratorów `@login_required`.
*   **Informatyka Śledcza (Forensics)**: Implementacja potoku ETL (Extract, Transform, Load), gdzie surowe logi są archiwizowane w formacie `.parquet` przed analizą, co zapewnia integralność materiału dowodowego.
*   **Silnik Korelacji SIEM**: Logika biznesowa (`log_analyzer.py`) korelująca nieudane próby logowania z rejestrem reputacji adresów IP w celu wykrywania anomalii.
*   **Cross-Host Correlation**: Zaawansowana logika wykrywająca i banująca adresy IP atakujące wiele niezależnych hostów jednocześnie (Wykrywanie Ataków Rozproszonych).
*   **Najlepsze Praktyki Bezpieczeństwa**: Pełna ochrona CSRF skonfigurowana dla wszystkich punktów końcowych API.

## Wymagania Wstępne
*   Python 3.8+
*   Dostęp do monitorowanych maszyn przez SSH (Linux) lub WMI (Windows)

## Instalacja

1.  Sklonuj repozytorium.
2.  Zainstaluj zależności:
    ```bash
    pip install -r requirements.txt
    ```
3.  Zainicjuj bazę danych:
    ```bash
    flask shell
    >>> db.create_all()
    >>> exit()
    ```
4.  Utwórz użytkownika administracyjnego:
    ```bash
    flask shell
    >>> from app.models import User
    >>> u = User(username='admin')
    >>> u.set_password('securepassword')
    >>> db.session.add(u)
    >>> db.session.commit()
    >>> exit()
    ```

## Użycie

Uruchom serwer aplikacji:
```bash
flask run
```

Panel nawigacyjny dostępny jest pod adresem `http://localhost:5000`. Zaloguj się danymi utworzonymi podczas instalacji.

## Struktura Projektu

```text
/
├── app/                          # Główny katalog aplikacji Flask
│   ├── blueprints/               # Obsługa routingu HTTP
│   │   ├── api/                  # API REST
│   │   │   └── hosts.py          # Endpointy API (Hosty, Logi, Alerty)
│   │   ├── __init__.py
│   │   ├── auth.py               # Logowanie i wylogowywanie
│   │   └── ui.py                 # Widoki HTML (Dashboard, Config)
│   │
│   ├── services/                 # Logika biznesowa (Backend)
│   │   ├── __init__.py
│   │   ├── data_manager.py       # Warstwa zapisu danych (Parquet/ETL)
│   │   ├── log_analyzer.py       # Analiza bezpieczeństwa (wykrywanie ataków)
│   │   ├── log_collector.py      # Pobieranie logów (SSH/WinApi + Regex)
│   │   ├── remote_client.py      # Klient SSH (Paramiko)
│   │   └── win_client.py         # Klient Windows (Subprocess/PowerShell)
│   │
│   ├── static/                   # Pliki statyczne
│   │   ├── css/
│   │   │   └── style.css         # Główny arkusz stylów
│   │   └── js/
│   │       ├── admin.js          # Logika panelu administracyjnego
│   │       ├── api.js            # Wrapper do komunikacji z API
│   │       ├── dashboard.js      # Odświeżanie danych na dashboardzie
│   │       ├── dom.js            # Helpery do manipulacji DOM
│   │       ├── main.js           # Inicjalizacja frontendu
│   │       └── theme.js          # Obsługa trybu ciemnego/jasnego
│   │
│   ├── templates/                # Szablony HTML (Jinja2)
│   │   ├── base.html             # Layout bazowy aplikacji
│   │   ├── config.html           # Panel zarządzania hostami
│   │   ├── index.html            # Główny widok dashboardu
│   │   └── login.html            # Formularz logowania
│   │
│   ├── __init__.py               # Application Factory
│   ├── extensions.py             # Konfiguracja rozszerzeń (DB, Login, CSRF)
│   ├── forms.py                  # Definicje formularzy (WTF)
│   └── models.py                 # Modele bazy danych
│
├── testy i weryfikacje/          # Skrypty pomocnicze i testowe
├── config.py                     # Główna konfiguracja
├── requirements.txt              # Zależności Python
└── README.md                     # Dokumentacja
```

## Licencja
Projekt stworzony w celach edukacyjnych.