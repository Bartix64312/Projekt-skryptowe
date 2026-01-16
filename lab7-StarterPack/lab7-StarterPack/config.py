class Config:
    SECRET_KEY = 'sekretny-klucz'
    SQLALCHEMY_DATABASE_URI = "sqlite:///../instance/lab7.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    
    # Konfiguracja SSH (dla maszyny Vagrant)
    SSH_DEFAULT_USER = 'vagrant'
    SSH_DEFAULT_PORT = 2222
    # 🔑 jedna z dwóch metod autoryzacji (tylko jedna powinna być aktywna)
    #SSH_PASSWORD = "vagrant"   # logowanie hasłem
    #SSH_KEY_FILE logowanie kluczem, poniżej przykładowy klucz
    #SSH_KEY_FILE = r"c:\Mirek\cyber-lab\vagrant-ok\.vagrant\machines\default\virtualbox\private_key"
    SSH_KEY_FILE = "C:\\Users\\natal\\vagrant-lab\\.vagrant\\machines\\default\\virtualbox\\private_key"