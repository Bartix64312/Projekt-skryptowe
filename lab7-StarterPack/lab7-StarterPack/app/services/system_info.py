# app/services/system_info.py
import psutil
import time
import datetime
import os

def get_linux_metrics(ssh_client):
    """
    GOTOWIEC: Ta funkcja wykonuje komendy na zdalnym serwerze (Linux/Vagrant)
    i parsuje ich wyniki. Nie musisz jej modyfikować.
    """
    try:
        # 1. RAM (wolna pamięć w MB)
        ram_out, _ = ssh_client.run("free -m | grep Mem | awk '{print $7}'")
        
        # 2. DYSK (Zajętość % oraz Rozmiar Całkowity)
        # Próbujemy pobrać dla partycji montowanej w '/'
        # awk '{print $5}' to procenty, awk '{print $2}' to rozmiar (np. 20G)
        disk_percentage, _ = ssh_client.run("df -h | grep '/$' | awk '{print $5}'")
        disk_total, _ = ssh_client.run("df -h | grep '/$' | awk '{print $2}'")
        
        # Fallback na /dev/sda1 jeśli nie znaleziono '/'
        if not disk_percentage:
            disk_percentage, _ = ssh_client.run("df -h | grep '/dev/sda1' | awk '{print $5}'")
            disk_total, _ = ssh_client.run("df -h | grep '/dev/sda1' | awk '{print $2}'")
        
        # 3. CPU Load (load average z 5 min)
        cpu_load, _ = ssh_client.run("uptime | awk -F'load average:' '{ print $2 }' | cut -d',' -f1")
        
        # 4. UPTIME
        uptime_seconds_str, _ = ssh_client.run("cat /proc/uptime | awk '{print $1}'")
        
        uptime_formatted = "N/A"
        try:
            total_seconds = float(uptime_seconds_str)
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            uptime_formatted = f"{hours}h {minutes}m"
        except (ValueError, TypeError):
            uptime_formatted = "?"

        return {
            "free_ram_mb": ram_out.strip(),
            "disk_info": disk_percentage.strip(), # np. "45%"
            "disk_total": disk_total.strip(),     # np. "20G"
            "cpu_load": cpu_load.strip(),
            "uptime_hours": uptime_formatted
        }
    except Exception as e:
        print(f"Parsing Error: {e}")
        return {
            "free_ram_mb": "Err", "disk_info": "Err", "disk_total": "?",
            "cpu_load": "Err", "uptime_hours": "Err"
        }

def get_windows_metrics():
    """
    ZADANIE DLA CIEBIE:
    Użyj biblioteki psutil, aby pobrać parametry lokalnego systemu Windows.
    Zwróć słownik o takiej samej strukturze jak funkcja wyżej.
    """
    try:
        mem = psutil.virtual_memory()
        free_ram_mb = str(int(mem.available / (1024 * 1024)))

        try:
            disk = psutil.disk_usage('C:\\')
        except Exception as e:
            disk = psutil.disk_usage(os.path.abspath(os.sep))
        disk_percent = f"{disk.percent}%"
        disk_total_gb = f"{int(disk.total / (1024**3))}GB"

        cpu_load = str(psutil.cpu_percent(interval=0.1))

        boot_time = psutil.boot_time()
        now = time.time()
        uptime_seconds = now - boot_time

        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        uptime_formatted = f"{hours}h {minutes}m"
    # Podpowiedzi:
    # ram = psutil.virtual_memory() -> ram.available
    # cpu = psutil.cpu_percent()
    # disk = psutil.disk_usage('C:\\') -> disk.percent oraz disk.total
    # uptime -> psutil.boot_time() (trzeba odjąć od datetime.now())

        data = {
            "free_ram_mb": free_ram_mb,     # Wynik w MB (string)
            "disk_info": disk_percent,       # Wynik w % (string, np. "45%")
            "disk_total": disk_total_gb,      # Wynik w GB (string, np. "100GB")
            "cpu_load": cpu_load,        # Wynik w % (string)
            "uptime_hours": uptime_formatted     # Czas pracy (string np. "1h 30m")
        }
        return data
    
    except Exception as e:
        print(f"Windows Metrics Error: {e}")
        return {
            "free_ram_mb": "Err", "disk_info": "Err", "disk_total": "?",
            "cpu_load": "Err", "uptime_hours": "Err"
        }