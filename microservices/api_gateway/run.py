#!/usr/bin/env python3
"""
API Gateway Service 起動スクリプト
"""

import logging
import os
import sys
from typing import Any

from config import get_config

from app import create_app


def setup_logging(config: Any) -> None:
    """ログ設定"""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/api_gateway.log", encoding="utf-8"),
        ]
        if os.path.exists("logs")
        else [logging.StreamHandler(sys.stdout)],
    )


def main() -> None:
    """メイン関数"""
    try:
        # 環境変数から設定を取得
        environment = os.environ.get("ENVIRONMENT", "development")
        config = get_config(environment)

        # ログ設定
        setup_logging(config)
        logger = logging.getLogger(__name__)

        logger.info(f"Starting API Gateway Service in {environment} mode")

        # アプリケーション作成
        app = create_app()

        # サービス URL 確認
        logger.info("Service URLs:")
        for service_name, url in config.get_all_service_urls().items():
            logger.info(f"  {service_name}: {url}")

        # サーバー起動設定
        host = os.environ.get("HOST", "0.0.0.0")
        port = int(os.environ.get("PORT", "8000"))

        if environment == "production":
            # 本番環境では Gunicorn を推奨
            logger.info(
                f"Production mode: Use 'gunicorn -w 4 -b {host}:{port} run:app'"
            )
            logger.info(
                "Starting with Flask development server "
                "(not recommended for production)"
            )

        logger.info(f"API Gateway Service starting on http://{host}:{port}")

        # アプリケーション起動
        app.run(host=host, port=port, debug=config.DEBUG, threaded=True)

    except Exception as e:
        logger.error(f"Failed to start API Gateway Service: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
