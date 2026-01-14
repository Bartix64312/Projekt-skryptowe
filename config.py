import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv() #zaczytywanie zmiennych z pliku .env, którego nie można przesyłać publicznie

class Config: #wykorzystywane w create_app
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-bardzo-tajny') #2 wartość to fallback w przypadku gdy nie będzie wartości nr.1 w .env
    
    # Baza danych
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///../instance/lab7.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Konfiguracja SSH (Domyślne dla Vagranta)
    SSH_DEFAULT_USER = os.getenv('SSH_DEFAULT_USER', 'vagrant')
    SSH_DEFAULT_PORT = int(os.getenv('SSH_DEFAULT_PORT', 2222))
    SSH_KEY_FILE = os.getenv('SSH_KEY_FILE', '') 

    # Folder na logi (Parquet)
    STORAGE_FOLDER = Path.cwd() / 'storage' # Domyślny folder na logi