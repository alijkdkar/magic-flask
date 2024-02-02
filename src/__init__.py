from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from .config import config
from src.utils.minioProvider import MinIoProvider

db = SQLAlchemy()
migrate = Migrate()
minio = MinIoProvider()

def create_app(config_mode):
    app = Flask(__name__)
    app.config.from_object(config[config_mode])

    db.init_app(app)
    migrate.init_app(app, db)
    minio.Connect()
    return app