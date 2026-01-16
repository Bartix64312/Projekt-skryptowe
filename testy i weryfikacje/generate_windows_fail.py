import subprocess
import time
import random

def generate_failures():
    print("=== Generating Windows Failed Login Attempts (Event 4625) ===")
    
    users = ["admin_wannabe", "autobot", "hacker_steve", "administrator"]
    
    for i in range(5):
        user = random.choice(users)
        print(f"[{i+1}/5] Próba logowania jako '{user}' z błędnym hasłem...")
        
        # Sposób 1: NET USE (Logon Type 3 - Network)
        # Próbujemy podmapować zasób IPC$ lokalnie z błędnymi danymi
        cmd = f"net use \\\\127.0.0.1\\IPC$ /u:{user} 'badpassword123' >NUL 2>&1"
        subprocess.run(cmd, shell=True)
        
        # Sposób 2: RUNAS (Logon Type 2 - Interactive - trudniejsze do zautomatyzowania bez inputu)
        # Zostajemy przy NET USE, generuje ładne 4625.
        
        time.sleep(1)

    print("\n Zakończono generowanie zdarzeń.")
    print(" Sprawdź teraz 'python test_windows_logs.py'")

if __name__ == "__main__":
    generate_failures()
