import time
from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required
from datetime import timezone, datetime
from sqlalchemy import func
import os

from app.models import Host, LogSource, LogArchive, Alert, IPRegistry
from app.services.remote_client import RemoteClient
from app.services.win_client import WinClient
from app.services.log_collector import LogCollector
from app.services.data_manager import DataManager
from app.services.log_analyzer import LogAnalyzer
from app.extensions import db

api_bp = Blueprint("api_hosts", __name__)

# --- CRUD HOSTS (GOTOWE - ABY UI DZIAŁAŁO) ---

@api_bp.route("/hosts", methods=["GET"])
@login_required
def get_hosts():
    hosts = Host.query.all()
    return jsonify([h.to_dict() for h in hosts])

@api_bp.route("/hosts", methods=["POST"])
@login_required
def add_host():
    data = request.get_json()
    if not data: return jsonify({"error": "Brak danych"}), 400
    if Host.query.filter_by(ip_address=data.get("ip_address")).first():
        return jsonify({"error": "IP musi być unikalne"}), 409
    new_host = Host(hostname=data.get("hostname"), ip_address=data.get("ip_address"), os_type=data.get("os_type"))
    db.session.add(new_host)
    db.session.commit()
    return jsonify(new_host.to_dict()), 201

@api_bp.route("/hosts/<int:host_id>", methods=["DELETE"])
@login_required
def delete_host(host_id):
    host = Host.query.get_or_404(host_id)
    db.session.delete(host)
    db.session.commit()
    return jsonify({"message": "Usunięto hosta"}), 200

@api_bp.route("/hosts/<int:host_id>", methods=["PUT"])
@login_required
def update_host(host_id):
    host = Host.query.get_or_404(host_id)
    data = request.get_json()
    if 'hostname' in data: host.hostname = data['hostname']
    if 'ip_address' in data: host.ip_address = data['ip_address']
    if 'os_type' in data: host.os_type = data['os_type']
    db.session.commit()
    return jsonify(host.to_dict()), 200

# --- MONITORING LIVE (GOTOWE) ---

@api_bp.route("/hosts/<int:host_id>/ssh-info", methods=["GET"])
@login_required
def get_ssh_info(host_id):
    host = Host.query.get_or_404(host_id)
    ssh_user = current_app.config.get("SSH_DEFAULT_USER", "vagrant")
    ssh_port = current_app.config.get("SSH_DEFAULT_PORT", 2222)
    ssh_key = current_app.config.get("SSH_KEY_FILE")
    try:
        with RemoteClient(host=host.ip_address, user=ssh_user, port=ssh_port, key_file=ssh_key) as remote:
            ram_out, _ = remote.run("free -m | grep Mem | awk '{print $7}'")
            disk_percentage, _ = remote.run("df -h | grep '/$' | awk '{print $5}'")
            if not disk_percentage: disk_percentage, _ = remote.run("df -h | grep '/dev/sda1' | awk '{print $5}'")
            disk_total, _ = remote.run("df -h | grep '/dev/sda1' | awk '{print $2}'")
            cpu_load, _ = remote.run("uptime | awk -F'load average:' '{ print $2 }' | cut -d',' -f1")
            uptime_seconds_str, _ = remote.run("cat /proc/uptime | awk '{print $1}'")
            uptime_formatted = "N/A"
            try:
                total_seconds = float(uptime_seconds_str)
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                uptime_formatted = f"{hours}h {minutes}m"
            except: pass

            return jsonify({
                "free_ram_mb": ram_out.strip(), "disk_info": disk_percentage.strip(),
                "disk_total": disk_total.strip(), "cpu_load": cpu_load.strip(), "uptime_hours": uptime_formatted
            }), 200
    except Exception as e:
        return jsonify({"error": f"Błąd połączenia: {str(e)}"}), 500

@api_bp.route("/hosts/<int:host_id>/windows-info", methods=["GET"])
@login_required
def get_windows_info(host_id):
    import psutil
    host = Host.query.get_or_404(host_id)
    if host.os_type != "WINDOWS": return jsonify({"error": "Wrong OS"}), 400
    try:
        mem = psutil.virtual_memory()
        free_ram_mb = str(round(mem.available / (1024 * 1024)))
        cpu_load = f"{psutil.cpu_percent(interval=0.1)}%"
        try:
            usage = psutil.disk_usage("C:\\")
            disk_percentage = f"{usage.percent}%"
            disk_total = f"{round(usage.total / (1024**3), 1)}GB"
        except:
            disk_percentage, disk_total = "N/A", "?"
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime_seconds = (datetime.now() - boot_time).total_seconds()
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        return jsonify({
            "free_ram_mb": free_ram_mb, "disk_info": disk_percentage,
            "disk_total": disk_total, "cpu_load": cpu_load, "uptime_hours": f"{hours}h {minutes}m"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===================================================================
# MIEJSCE NA TWOJĄ IMPLEMENTACJĘ (ZADANIE 2 i 3)
# ===================================================================

@api_bp.route("/hosts/<int:host_id>/logs", methods=["POST"])
@login_required
def fetch_logs(host_id):
    host = Host.query.get_or_404(host_id)
    
    # 1. Zarządzanie Stanem: Pobieramy lub tworzymy źródło logów
    log_source = LogSource.query.filter_by(host_id=host.id).first()
    if not log_source:
        log_source = LogSource(host_id=host.id, log_type='security', last_fetch=None)
        db.session.add(log_source)
        db.session.commit()
    
    last_fetch_time = log_source.last_fetch
    current_fetch_time = datetime.now()
    logs = []
    
    # 2. Pobieranie Logów (ETL - Extract)
    try:
        if host.os_type == "LINUX":
            ssh_user = current_app.config.get("SSH_DEFAULT_USER", "vagrant")
            ssh_port = current_app.config.get("SSH_DEFAULT_PORT", 2222)
            ssh_key = current_app.config.get("SSH_KEY_FILE")
            
            # Context Manager dla połączenia SSH
            with RemoteClient(host=host.ip_address, user=ssh_user, port=ssh_port, key_file=ssh_key) as client:
                # Przekazujemy last_fetch aby pobrać tylko nowe logi
                logs = LogCollector.get_linux_logs(client, last_fetch_time=None)

        elif host.os_type == "WINDOWS":
            # Context Manager dla klienta Windows (lokalny powershell/wmi)
            with WinClient() as client:
                logs = LogCollector.get_windows_logs(client, last_fetch=last_fetch_time)

        else:
            return jsonify({"error": "Unsupported OS type"}), 400
        

    except Exception as e:
        return jsonify({"error": f"Connection/Collection failed: {str(e)}"}), 500

    if not logs:
        return jsonify({"message": "No new logs found", "alerts": 0}), 200

    # 3. Archiwizacja (ETL - Load)
    # Zapisujemy surowe dane do Parquet dla celów dowodowych (forensics)
    try:
        filename, count = DataManager.save_logs_to_parquet(logs, host_id=host.id)
        
        # Rejestrujemy archiwum w bazie
        archive = LogArchive(host_id=host.id, timestamp=current_fetch_time, filename=filename, record_count=count)
        db.session.add(archive)
        new_alerts_count = LogAnalyzer.analyze_parquet(filename, host.id)
        
        # Aktualizujemy stan (watermark) - ostatnie pobranie
        log_source.last_fetch = current_fetch_time
        db.session.commit()

        return jsonify({
            "message": f"Success. Processed {count} logs.", 
            "new_alerts": new_alerts_count
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500
    
@api_bp.route("/alerts", methods=["GET"])
@login_required
def get_recent_alerts():
    alerts = Alert.query.order_by(Alert.timestamp.desc()).limit(50).all()
    ip_registry = {ip.ip_address: ip.status for ip in IPRegistry.query.all()}

    results = []
    for alert in alerts:
        current_status = ip_registry.get(alert.source_ip, 'UNKNOWN')
        
        msg = alert.message
        display_severity = 'WARNING' 
        if current_status == 'BANNED':
            display_severity = 'CRITICAL'
            if "BANNED" not in msg:
                msg = f"SECURITY BREACH: Attack from BANNED IP {alert.source_ip}"
        
        elif current_status == 'TRUSTED':
            display_severity = 'INFO'
            msg = msg.replace("SECURITY BREACH: ", "").replace("Attack from BANNED IP", "Activity from")
            msg = f"[TRUSTED] {msg}"
            
        else: 
            if alert.severity == 'INFO':
                display_severity = 'INFO'
            else:
                display_severity = 'WARNING'
            msg = msg.replace("SECURITY BREACH: ", "")
            msg = msg.replace("Attack from BANNED IP", "Suspicious attempt from")

        host_name = alert.host.hostname if alert.host else "Unknown"
        
        results.append({
            "id": alert.id,
            "severity": display_severity, 
            "timestamp": alert.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "message": msg,
            "host_name": host_name,
            "alert_type": alert.alert_type,
            "source_ip": alert.source_ip
        })
        
    return jsonify(results)

@api_bp.route("/stats/alerts", methods=["GET"])
@login_required
def get_alert_stats():
    stats = db.session.query(
        Alert.source_ip, 
        func.count(Alert.id)
    ).group_by(Alert.source_ip)\
     .order_by(func.count(Alert.id).desc())\
     .limit(5).all()

    labels = [s[0] if s[0] else "Unknown" for s in stats]
    values = [s[1] for s in stats]
    
    return jsonify({"labels": labels, "values": values})

@api_bp.route("/ips", methods=["GET"])
@login_required
def get_ips():
    ips = IPRegistry.query.order_by(IPRegistry.last_seen.desc()).all()
    result = []
    for ip in ips:
        result.append({
            "id": ip.id,
            "ip_address": ip.ip_address,
            "status": ip.status,
            "last_seen": ip.last_seen.strftime("%Y-%m-%d %H:%M:%S") if ip.last_seen else "-"
        })
    return jsonify(result)

@api_bp.route("/ips", methods=["POST"])
@login_required
def add_ip():
    data = request.get_json()
    if not data or 'ip_address' not in data:
        return jsonify({"error": "Brak adresu IP"}), 400
        
    if IPRegistry.query.filter_by(ip_address=data['ip_address']).first():
        return jsonify({"error": "IP już istnieje w rejestrze"}), 409
        
    new_ip = IPRegistry(
        ip_address=data['ip_address'],
        last_seen=datetime.now(timezone.utc)
    )
    db.session.add(new_ip)
    db.session.commit()
    return jsonify({"message": "Dodano adres IP"}), 201


@api_bp.route("/ips/<int:ip_id>", methods=["PUT"])
@login_required
def update_ip(ip_id):
    ip_entry = IPRegistry.query.get_or_404(ip_id)
    data = request.get_json()
    
    if 'status' in data:
        ip_entry.status = data['status']
    
    db.session.commit()
    return jsonify({"message": "Zaktualizowano status IP"}), 200

@api_bp.route("/ips/<int:ip_id>", methods=["DELETE"])
@login_required
def delete_ip(ip_id):
    ip_entry = IPRegistry.query.get_or_404(ip_id)
    db.session.delete(ip_entry)
    db.session.commit()
    return jsonify({"message": "Usunięto adres IP z bazy"}), 200
