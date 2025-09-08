from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.config import config

# 拡張機能の初期化
db: SQLAlchemy = SQLAlchemy()
migrate = Migrate()


def create_app(config_name: str = "default") -> Flask:
    """アプリケーションファクトリ"""
    app = Flask(__name__)

    # 設定の読み込み
    app.config.from_object(config[config_name])

    # 拡張機能の初期化
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, origins=app.config["CORS_ORIGINS"])

    # ブループリントの登録
    from app.routes.main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    from app.routes.api import api as api_blueprint

    app.register_blueprint(api_blueprint, url_prefix="/api")

    return app
