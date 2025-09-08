import os
from typing import Dict


class Config:
    """API Gateway Service 設定クラス"""

    # Flask 設定
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() == "true"

    # CORS 設定
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")

    # サービス URL 設定
    SERVICES = {
        "financial_data": {
            "internal_url": os.environ.get(
                "FINANCIAL_DATA_INTERNAL_URL", "http://localhost:8001"
            ),
            "production_url": os.environ.get(
                "FINANCIAL_DATA_PRODUCTION_URL", "http://financial-data-service:8001"
            ),
        },
        "data_management": {
            "internal_url": os.environ.get(
                "DATA_MANAGEMENT_INTERNAL_URL", "http://localhost:8002"
            ),
            "production_url": os.environ.get(
                "DATA_MANAGEMENT_PRODUCTION_URL", "http://data-management-service:8002"
            ),
        },
        "notification": {
            "internal_url": os.environ.get(
                "NOTIFICATION_INTERNAL_URL", "http://localhost:8003"
            ),
            "production_url": os.environ.get(
                "NOTIFICATION_PRODUCTION_URL", "http://notification-service:8003"
            ),
        },
    }

    # 環境設定
    ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")

    # ログ設定
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

    # タイムアウト設定
    REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", "30"))

    # リトライ設定
    MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "3"))
    RETRY_DELAY = float(os.environ.get("RETRY_DELAY", "1.0"))

    @classmethod
    def get_service_url(cls, service_name: str) -> str:
        """環境に応じたサービス URL を取得"""
        if service_name not in cls.SERVICES:
            raise ValueError(f"Unknown service: {service_name}")

        service_config = cls.SERVICES[service_name]

        if cls.ENVIRONMENT == "production":
            return service_config["production_url"]
        else:
            return service_config["internal_url"]

    @classmethod
    def get_all_service_urls(cls) -> Dict[str, str]:
        """全サービスの URL を取得"""
        return {
            service_name: cls.get_service_url(service_name)
            for service_name in cls.SERVICES.keys()
        }


class DevelopmentConfig(Config):
    """開発環境設定"""

    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """本番環境設定"""

    DEBUG = False
    LOG_LEVEL = "WARNING"

    # 本番環境では環境変数から必須設定を取得
    SECRET_KEY = os.environ.get("SECRET_KEY")

    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is required in production")


class TestingConfig(Config):
    """テスト環境設定"""

    TESTING = True
    DEBUG = True
    LOG_LEVEL = "DEBUG"

    # テスト用のモックサービス URL
    SERVICES = {
        "financial_data": {
            "internal_url": "http://localhost:18001",
            "production_url": "http://localhost:18001",
        },
        "data_management": {
            "internal_url": "http://localhost:18002",
            "production_url": "http://localhost:18002",
        },
        "notification": {
            "internal_url": "http://localhost:18003",
            "production_url": "http://localhost:18003",
        },
    }


# 環境に応じた設定クラスの選択
config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config(environment: str = None) -> Config:
    """環境に応じた設定クラスを取得"""
    if environment is None:
        environment = os.environ.get("ENVIRONMENT", "development")

    config_class = config_map.get(environment, DevelopmentConfig)
    return config_class()
