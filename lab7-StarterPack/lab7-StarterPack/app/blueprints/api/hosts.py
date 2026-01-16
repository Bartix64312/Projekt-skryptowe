from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models import Host
from app.services.remote_client import RemoteClient
from app.services.system_info import get_linux_metrics, get_windows_metrics

api_bp = Blueprint('api_hosts', __name__)

# ==========================================
# CZĘŚĆ 1: CRUD (Twoje Zadanie)
# ==========================================

@api_bp.route('/hosts', methods=['GET'])
def get_hosts():
    # TODO: Zwróć listę hostów z bazy
    hosts = Host.query.all()
    return jsonify([host.to_dict() for host in hosts])

@api_bp.route('/hosts', methods=['POST'])
def add_host():
    # TODO: Dodaj hosta do bazy
    data = request.get_json()
    if not data or not all (k in data for k in ("hostname", "ip_address", "os_type")):
        return jsonify({"message": "Missing fields"}), 400
    
    new_host = Host(
        hostname=data['hostname'],
        ip_address=data['ip_address'],
        os_type=data['os_type'].upper()
    )

    try:
        db.session.add(new_host)
        db.session.commit()
        return jsonify(new_host.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@api_bp.route('/hosts/<int:host_id>', methods=['DELETE'])
def delete_host(host_id):
    # TODO: Usuń hosta z bazy
    host = Host.query.get_or_404(host_id)
    db.session.delete(host)
    db.session.commit()
    return jsonify({"message": "Host deleted succesfully"})


# ==========================================
# CZĘŚĆ 2: MONITORING
# ==========================================

@api_bp.route('/hosts/<int:host_id>/ssh-info', methods=['GET'])
def get_ssh_info(host_id):
    """
    GOTOWIEC: Ten endpoint łączy się przez SSH z maszyną Vagrant/Linux.
    Analizuj ten kod, aby zrozumieć jak korzystać z current_app i serwisów.
    """
    # 1. Pobieramy hosta (odkomentuj po stworzeniu modelu Host)
    host = Host.query.get_or_404(host_id)

    if host.os_type != 'LINUX':
        return jsonify({"error": "SSH obsługiwane tylko dla Linuxa"}), 400
    
    # Symulacja hosta (usuń to, gdy będziesz mieć bazę):


    # 2. Pobieramy konfigurację z current_app (ustawioną w config.py lub domyślną)
    # Zakładamy, że łączymy się do lokalnej maszyny wirtualnej Vagrant
    ssh_user = current_app.config.get('SSH_DEFAULT_USER', 'vagrant')
    ssh_port = current_app.config.get('SSH_DEFAULT_PORT', 2222)
    ssh_key = current_app.config.get('SSH_KEY_FILE') # np. ścieżka do private_key

    try:
        # Używamy Context Managera (with) do bezpiecznego otwarcia i zamknięcia połączenia
        # UWAGA: Odkomentuj import RemoteClient i get_linux_metrics na górze pliku!
        
        with RemoteClient(host.ip_address, ssh_user, port=ssh_port, key_file=ssh_key) as client:
             data = get_linux_metrics(client)
             return jsonify(data), 200
        
        return jsonify({"info": "Odkomentuj kod w hosts.py"}), 200

    except Exception as e:
        print(f"SSH Error: {e}")
        return jsonify({"error": f"Błąd połączenia: {str(e)}"}), 500


@api_bp.route('/hosts/<int:host_id>/windows-info', methods=['GET'])
def get_windows_info(host_id):
    """
    ZADANIE DLA CIEBIE: Zaimplementuj pobieranie danych lokalnych (Windows).
    """
    # 1. Pobierz hosta z bazy po ID (używając Host.query...)
    # 2. Sprawdź, czy host.os_type == 'WINDOWS'
    host = Host.query.get_or_404(host_id)
    if host.os_type != 'WINDOWS':
        return jsonify({"error": "To nie jest host Windows"}), 400

    
    try:
        # 3. Wywołaj funkcję get_windows_metrics() z pliku services/system_info.py
        data = get_windows_metrics()
        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500