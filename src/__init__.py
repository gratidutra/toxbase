import os

from dotenv import load_dotenv
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# import src

# Carregar variáveis do .env
load_dotenv()

# Criar extensões
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()


app = Flask(__name__)

# Configuração do banco de dados PostgreSQL
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# Inicializar extensões com o app
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)

login_manager.login_view = "login"
login_manager.login_message = "Please login"
login_manager.login_category = "info"
from src import routes
