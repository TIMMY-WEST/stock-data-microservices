#!/usr/bin/env python3
"""
Financial Data Service 起動スクリプト
"""

import logging
import os
import sys
import threading
import time
from typing import Any, List

from config import get_config

from app import FinancialDataService


def setup_logging(config: Any) -> None:
    """ログ設定"""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=config.LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/financial_data.log", encoding="utf-8"),
        ]
        if os.path.exists("logs")
        else [logging.StreamHandler(sys.stdout)],
    )


def cleanup_old_tasks(service: FinancialDataService, config: Any) -> None:
    """古いタスクのクリーンアップ"""
    logger = logging.getLogger("cleanup")

    while True:
        try:
            current_time = time.time()
            task_timeout = config.get_task_config()["task_timeout"]
            tasks_to_remove = _find_expired_tasks(
                service, current_time, task_timeout, logger
            )
            _remove_expired_tasks(service, tasks_to_remove, logger)
        except Exception as e:
            logger.error(f"Error during task cleanup: {e}")
        time.sleep(config.get_task_config()["cleanup_interval"])


def _find_expired_tasks(
    service: FinancialDataService,
    current_time: float,
    task_timeout: int,
    logger: logging.Logger,
) -> List[str]:
    """期限切れタスクを探す"""
    tasks_to_remove = []
    for task_id, task_info in service.active_tasks.items():
        if task_info["status"] in ["completed", "failed"]:
            task_end_time = task_info.get("end_time", task_info.get("start_time"))
            if task_end_time and _is_task_expired(
                task_end_time, current_time, task_timeout, logger
            ):
                tasks_to_remove.append(task_id)
    return tasks_to_remove


def _is_task_expired(
    task_end_time: str, current_time: float, task_timeout: int, logger: logging.Logger
) -> bool:
    """タスクが期限切れかチェック"""
    from datetime import datetime

    try:
        end_dt = datetime.fromisoformat(task_end_time.replace("Z", "+00:00"))
        end_timestamp = end_dt.timestamp()
        return current_time - end_timestamp > task_timeout
    except Exception as e:
        logger.warning(f"Failed to parse task time {task_end_time}: {e}")
        return False


def _remove_expired_tasks(
    service: FinancialDataService, tasks_to_remove: List[str], logger: logging.Logger
) -> None:
    """期限切れタスクを削除"""
    for task_id in tasks_to_remove:
        del service.active_tasks[task_id]
        logger.info(f"Cleaned up old task: {task_id}")
    if tasks_to_remove:
        logger.info(f"Cleaned up {len(tasks_to_remove)} old tasks")


def main() -> None:
    """メイン関数"""
    try:
        # 環境変数から設定を取得
        environment = os.environ.get("ENVIRONMENT", "development")
        config = get_config(environment)

        # ログ設定
        setup_logging(config)
        logger = logging.getLogger(__name__)

        logger.info(f"Starting Financial Data Service in {environment} mode")

        # 設定情報をログ出力
        logger.info("Configuration:")
        yahoo_config = config.get_yahoo_config()
        task_config = config.get_task_config()
        logger.info(f"  Yahoo Finance timeout: {yahoo_config['timeout']}s")
        logger.info(f"  Max concurrent tasks: {task_config['max_concurrent_tasks']}")
        logger.info(f"  Rate limiting: {config.RATE_LIMITING['enabled']}")

        # サービス作成
        service = FinancialDataService()

        # バックグラウンドでタスククリーンアップを開始
        cleanup_thread = threading.Thread(
            target=cleanup_old_tasks, args=(service, config), daemon=True
        )
        cleanup_thread.start()
        logger.info("Task cleanup thread started")

        # サーバー起動設定
        host = os.environ.get("HOST", "0.0.0.0")
        port = int(os.environ.get("PORT", "8001"))

        if environment == "production":
            # 本番環境では Gunicorn を推奨
            logger.info(
                f"Production mode: Use 'gunicorn -w 4 -b {host}:{port} run:app'"
            )
            logger.info(
                "Starting with Flask development server "
                "(not recommended for production)"
            )

        logger.info(f"Financial Data Service starting on http://{host}:{port}")
        logger.info("Available endpoints:")
        logger.info("  POST /internal/fetch-stock-data - Yahoo Finance データ取得")
        logger.info("  GET  /internal/health - ヘルスチェック")
        logger.info("  GET  /internal/task/<task_id>/status - タスク状況確認")

        # アプリケーション起動
        service.run(host=host, port=port, debug=config.DEBUG)

    except Exception as e:
        logger.error(f"Failed to start Financial Data Service: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
