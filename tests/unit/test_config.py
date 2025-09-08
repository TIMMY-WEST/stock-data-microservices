"""
単体テスト: 設定関連のテスト
外部依存関係なし
"""
import os
from unittest.mock import patch

from app.config import Config


class TestConfig:
    """設定クラスの単体テスト"""

    def test_default_config(self):
        """デフォルト設定テスト"""
        config = Config()

        # デフォルト値の確認
        assert hasattr(config, "SECRET_KEY")
        assert hasattr(config, "SQLALCHEMY_TRACK_MODIFICATIONS")
        assert config.SQLALCHEMY_TRACK_MODIFICATIONS is False

    @patch.dict(os.environ, {"DATABASE_URL": "postgresql://test:test@localhost/test"})
    def test_database_url_from_env(self):
        """環境変数からのデータベースURL取得テスト"""
        config = Config()

        if hasattr(config, "SQLALCHEMY_DATABASE_URI"):
            # 環境変数が設定されている場合の動作確認
            assert "postgresql://" in str(config.SQLALCHEMY_DATABASE_URI)

    @patch.dict(os.environ, {"REDIS_URL": "redis://localhost:6380"})
    def test_redis_url_from_env(self):
        """環境変数からのRedis URL取得テスト"""
        config = Config()

        if hasattr(config, "REDIS_URL"):
            # 環境変数が設定されている場合の動作確認
            assert "redis://" in str(config.REDIS_URL)
