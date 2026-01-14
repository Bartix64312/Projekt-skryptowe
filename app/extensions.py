from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager 
from flask_wtf.csrf import CSRFProtect  

#Inicjalizacja globalnych rozszerzeń
db = SQLAlchemy() 
migrate = Migrate() #kontrola wersji dla db
login_manager = LoginManager()  
csrf = CSRFProtect()  