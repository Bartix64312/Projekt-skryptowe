import pandas as pd
from datetime import datetime, timezone, timedelta
from app.extensions import db
from app.models import Alert, IPRegistry, Host
from app.services.data_manager import DataManager

class LogAnalyzer:
    """
    Serce systemu SIEM. Analizuje pliki logów przy użyciu Pandas
    i generuje alerty w bazie danych.
    """

    @staticmethod
    def analyze_parquet(filename, host_id):
        """
        Główna funkcja analityczna.
        """
        # 1. Wczytanie danych (To masz gotowe)
        df = DataManager.load_logs(filename)
        
        if df.empty:
            return 0 
            
        # Zabezpieczenie przed brakiem kolumn
        if 'alert_type' not in df.columns or 'source_ip' not in df.columns:
            return 0

        # 2. Filtrowanie: Interesują nas tylko ataki
       
        attack_pattern = ['FAILED_LOGIN', 'INVALID_USER', 'WIN_FAILED_LOGIN', 'SUDO_USAGE']
        threats = df[df['alert_type'].isin(attack_pattern)]
        
        if threats.empty:
            return 0

        alerts_created = 0
        current_time = datetime.now(timezone.utc)
        
        # 3. Iteracja po zagrożeniach
        for index, row in threats.iterrows():
            ip = row['source_ip']
            user = row.get('user', 'unknown')

            ip_entry = IPRegistry.query.filter_by(ip_address=ip).first() # czy IP jest już zarejestrowane w bazie
            status = ip_entry.status if ip_entry else 'UNKNOWN'

            #sprawdzanie statusu przy tworzeniu nowych alertów 
            if status == 'BANNED':
                severity = 'CRITICAL'
                message = f"SECURITY BREACH: Attack from BANNED IP {ip}"
            elif status == 'TRUSTED':
                severity = 'INFO'
                message = f"Authorized activity from trusted IP {ip}"
            else:
                severity = 'WARNING'
                message = f"Suspicious login attempt for IP: {ip} (User: {user})"

            if not ip_entry:
                ip_entry = IPRegistry( #domyślne tworzenie IP do bazy
                    ip_address = ip,
                    status='UNKNOWN',
                    last_seen=current_time
                )
                db.session.add(ip_entry)
            else:
                ip_entry.last_seen = current_time

            severity = 'WARNING' #domyślnie 
            message = f"Suspicious login attempt for IP: {ip} (User: {user})"
            
            time_treshold = current_time - timedelta(minutes=10) #przedział czasowy

            cross_host_attacks = Alert.query.filter( #ataki między hostami, sprawdzanie czy w bazie już jest log z takim adresem IP w odpowiednim zakresie czasu
                Alert.source_ip == ip,
                Alert.host_id != host_id,
                Alert.timestamp >= time_treshold
            ).count()

            #logika ataków rozproszonych 
            if cross_host_attacks > 0 and ip_entry.status != 'TRUSTED':
                severity = 'CRITICAL'
                message = f"DISTRIBUTED ATTACK: IP {ip} attacking multiple hosts!"

                ip_entry.status = 'BANNED'
                db.session.add(ip_entry)

            #dopisanie severity do reszty przypadków
            if ip_entry.status == 'TRUSTED':
                severity = 'INFO'
                
            elif ip_entry.status == 'BANNED':
                severity = 'CRITICAL'
                message = f"SECURITY BREACH: Attack from BANNED IP {ip} (User: {user})"

            log_timestamp = row['timestamp']
            if isinstance(log_timestamp, str): #dopisanie znacznika czasowego (czas logu, nie czas pobrania z bazy)
                try:
                    log_timestamp = datetime.fromisoformat(log_timestamp)
                except:
                    log_timestamp = current_time

            #aby nie powtarzać alertów - sprawdzamy czy jest w bazie - jeżeli nie to tworzymy nowy
            existing_alert = Alert.query.filter_by(
                host_id=host_id,
                timestamp=log_timestamp,
                source_ip=ip,
                alert_type=row['alert_type']
            ).first()

            if existing_alert:
                if severity == 'CRITICAL' and existing_alert.severity != 'CRITICAL':
                    existing_alert.severity = 'CRITICAL'
                    existing_alert.message = message
                continue 

            new_alert = Alert(
                host_id=host_id,
                alert_type=row['alert_type'],
                source_ip=ip,
                severity=severity,
                message=message,
                timestamp=log_timestamp
            )
            # 6. Dodaj do sesji (db.session.add) i zwiększ licznik alerts_created.
            db.session.add(new_alert)
            alerts_created += 1
            
        # Zatwierdzenie zmian w bazie
        db.session.commit()
        return alerts_created