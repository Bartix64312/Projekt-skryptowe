import paramiko
from config import Config

def main():
    host = "127.0.0.1"
    port = 2222
    user = "invalid_guy"
    
    # Intentionally wrong password
    password = "WRONG_PASSWORD_123"
    
    print(f"Attempting to connect to {user}@{host}:{port} with WRONG password...")
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, port=port, username=user, password=password, timeout=5)
    except paramiko.AuthenticationException:
        print("✅ Authentication failed as expected.")
    except Exception as e:
        print(f"Other error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()
