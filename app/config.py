import os


class Config:
    """基本設定"""

    # Flask 設定
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-in-production")

    # データベース設定
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://stock_user:stock_password@localhost:5432/stock_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.environ.get("FLASK_ENV") == "development"

    # Yahoo Finance 設定
    YAHOO_FINANCE_BASE_URL = os.environ.get(
        "YAHOO_FINANCE_BASE_URL", "https://query1.finance.yahoo.com"
    )
    YAHOO_FINANCE_TIMEOUT = int(os.environ.get("YAHOO_FINANCE_TIMEOUT", 30))

    # CORS設定
    CORS_ORIGINS = ["http://localhost:8000", "http://127.0.0.1:8000"]

    # アプリケーション設定
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    JSON_SORT_KEYS = False

    # ページネーション設定
    DEFAULT_PER_PAGE = 12
    MAX_PER_PAGE = 100


class DevelopmentConfig(Config):
    """開発環境設定"""

    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """本番環境設定"""

    DEBUG = False
    TESTING = False

    # 本番環境専用設定
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """テスト環境設定"""

    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


# 環境別設定マッピング
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
