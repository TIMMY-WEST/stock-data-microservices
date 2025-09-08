import os
from typing import Any, Dict


class Config:
    """Financial Data Service 設定クラス"""

    # Flask 設定
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() == "true"

    # Yahoo Finance 設定
    YAHOO_FINANCE_CONFIG = {
        "timeout": int(os.environ.get("YAHOO_TIMEOUT", "30")),
        "max_retries": int(os.environ.get("YAHOO_MAX_RETRIES", "3")),
        "retry_delay": float(os.environ.get("YAHOO_RETRY_DELAY", "1.0")),
        "user_agent": os.environ.get(
            "YAHOO_USER_AGENT",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        ),
    }

    # データ処理設定
    DATA_PROCESSING = {
        "max_records_per_request": int(
            os.environ.get("MAX_RECORDS_PER_REQUEST", "10000")
        ),
        "batch_size": int(os.environ.get("BATCH_SIZE", "1000")),
        "cache_ttl": int(os.environ.get("CACHE_TTL", "300")),  # 5分
    }

    # タスク管理設定
    TASK_MANAGEMENT = {
        "max_concurrent_tasks": int(os.environ.get("MAX_CONCURRENT_TASKS", "10")),
        "task_timeout": int(os.environ.get("TASK_TIMEOUT", "300")),  # 5分
        "cleanup_interval": int(os.environ.get("CLEANUP_INTERVAL", "3600")),  # 1時間
    }

    # ログ設定
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.environ.get(
        "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # 環境設定
    ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")

    # サポートされる期間
    SUPPORTED_PERIODS = [
        "1d",
        "5d",
        "1mo",
        "3mo",
        "6mo",
        "1y",
        "2y",
        "5y",
        "10y",
        "ytd",
        "max",
    ]

    # レート制限設定
    RATE_LIMITING = {
        "enabled": os.environ.get("RATE_LIMITING_ENABLED", "True").lower() == "true",
        "requests_per_minute": int(os.environ.get("REQUESTS_PER_MINUTE", "60")),
        "requests_per_hour": int(os.environ.get("REQUESTS_PER_HOUR", "1000")),
    }

    @classmethod
    def get_yahoo_config(cls) -> Dict[str, Any]:
        """Yahoo Finance 設定を取得"""
        return cls.YAHOO_FINANCE_CONFIG.copy()

    @classmethod
    def get_data_processing_config(cls) -> Dict[str, Any]:
        """データ処理設定を取得"""
        return cls.DATA_PROCESSING.copy()

    @classmethod
    def get_task_config(cls) -> Dict[str, Any]:
        """タスク管理設定を取得"""
        return cls.TASK_MANAGEMENT.copy()

    @classmethod
    def is_valid_period(cls, period: str) -> bool:
        """期間の妥当性をチェック"""
        return period in cls.SUPPORTED_PERIODS


class DevelopmentConfig(Config):
    """開発環境設定"""

    DEBUG = True
    LOG_LEVEL = "DEBUG"

    # 開発環境では制限を緩和
    RATE_LIMITING = {
        "enabled": False,
        "requests_per_minute": 1000,
        "requests_per_hour": 10000,
    }

    # タスク管理設定を開発用に調整
    TASK_MANAGEMENT = {
        "max_concurrent_tasks": 5,
        "task_timeout": 600,  # 10分
        "cleanup_interval": 1800,  # 30分
    }


class ProductionConfig(Config):
    """本番環境設定"""

    DEBUG = False
    LOG_LEVEL = "WARNING"

    # 本番環境では環境変数から必須設定を取得
    SECRET_KEY = os.environ.get("SECRET_KEY")

    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is required in production")

    # 本番環境では厳格なレート制限
    RATE_LIMITING = {
        "enabled": True,
        "requests_per_minute": 30,
        "requests_per_hour": 500,
    }

    # Yahoo Finance 設定を本番用に調整
    YAHOO_FINANCE_CONFIG = {
        "timeout": 60,
        "max_retries": 5,
        "retry_delay": 2.0,
        "user_agent": os.environ.get("YAHOO_USER_AGENT", "StockDataMicroservice/1.0"),
    }


class TestingConfig(Config):
    """テスト環境設定"""

    TESTING = True
    DEBUG = True
    LOG_LEVEL = "DEBUG"

    # テスト環境では制限を無効化
    RATE_LIMITING = {
        "enabled": False,
        "requests_per_minute": 10000,
        "requests_per_hour": 100000,
    }

    # テスト用の短いタイムアウト
    YAHOO_FINANCE_CONFIG = {
        "timeout": 5,
        "max_retries": 1,
        "retry_delay": 0.1,
        "user_agent": "TestAgent/1.0",
    }

    # タスク管理をテスト用に調整
    TASK_MANAGEMENT = {
        "max_concurrent_tasks": 2,
        "task_timeout": 30,
        "cleanup_interval": 60,
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
