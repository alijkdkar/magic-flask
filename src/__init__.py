from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from .config import config
from src.utils.minioProvider import MinIoProvider
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS, cross_origin


db = SQLAlchemy()
migrate = Migrate()
minio = MinIoProvider()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app(config_mode):
    app = Flask(__name__)
    CORS(app, supports_credentials=True,origins=['*','http://192.168.1.12:5173/','http://192.168.1.12:5173','http://192.168.1.12:5173/*','http://*:5173/*','http://localhost:5173/','http://localhost:5173','http://127.0.0.1:5173'])
    app.secret_key = 'what is my secret value i dont knows'
    app.config.from_object(config[config_mode])

    db.init_app(app)
    migrate.init_app(app, db)
    minio.Connect()
    login_manager.init_app(app)
    login_manager.login_view = 'index' # set where must redirect when onlune user is  not logged in
    bcrypt.init_app(app)

    return app