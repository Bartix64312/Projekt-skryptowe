import os
from testy i weryfikacje.config import Config
from app.services.remote_client import RemoteClient
from app.services.log_collector import LogCollector

def main():
    # 1. Pobieramy konfigurację
    host = "127.0.0.1"
    port = Config.SSH_DEFAULT_PORT
    user = Config.SSH_DEFAULT_USER
    key_path = Config.SSH_KEY_FILE
    password = Config.SSH_PASSWORD

    print(f"--- TEST POŁĄCZENIA SSH: {user}@{host}:{port} ---")
    print(f"--- KLUCZ: {key_path} | HASŁO: {'***' if password else 'BRAK'} ---")

    # 2. Szybkie sprawdzenie czy mamy czym się uwierzytelnić
    if (not key_path or not os.path.exists(key_path)) and not password:
        print(f"❌ BŁĄD: Brak metod uwierzytelniania! (Brak pliku klucza: {key_path} oraz brak hasła)")
        return

    try:
        # 3. Nawiązanie połączenia
        with RemoteClient(host=host, user=user, port=port, key_file=key_path, password=password) as client:
            print("✅ Połączono. Pobieram logi...")

            # 4. Pobranie logów (korzystamy z naszej nowej logiki z Regexami)
            logs = LogCollector.get_linux_logs(client)

            print(f"📊 Znaleziono zdarzeń: {len(logs)}")

            if not logs:
                print("💡 Brak podejrzanych logów (Failed password / Sudo).")
                return

            # 5. Wyświetlenie wyników
            print(f"{'TIMESTAMP':<20} | {'TYP':<15} | {'IP':<15} | {'USER'}")
            print("-" * 65)
            for log in logs:
                print(f"{str(log['timestamp']):<20} | {log['alert_type']:<15} | {log['source_ip']:<15} | {log['user']}")

    except Exception as e:
        print(f"❌ Błąd: {e}")

if __name__ == "__main__":
    main()