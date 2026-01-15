import os
import json
from testy i weryfikacje.config import Config
from app.services.remote_client import RemoteClient

def main():
    host = "127.0.0.1"
    port = Config.SSH_DEFAULT_PORT
    user = Config.SSH_DEFAULT_USER
    key_path = Config.SSH_KEY_FILE
    password = Config.SSH_PASSWORD

    print(f"Connecting to {user}@{host}:{port}...")

    try:
        with RemoteClient(host=host, user=user, port=port, key_file=key_path, password=password) as client:
            # Get last 20 lines in plain text
            cmd = "sudo journalctl -u ssh -n 20 --no-pager"
            stdout, stderr = client.run(cmd)
            
            with open('log_dump.txt', 'w', encoding='utf-8') as f:
                 f.write(stdout)
            print(f"Saved {len(stdout)} chars to log_dump.txt")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
