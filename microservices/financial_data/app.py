import logging
import threading
import time
import uuid
from datetime import datetime
from typing import Any, Dict

import pandas as pd
import yfinance as yf
from flask import Flask, jsonify, request

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FinancialDataService:
    def __init__(self):
        self.app = Flask(__name__)

        # アクティブなタスクを管理
        self.active_tasks = {}

        self._setup_routes()

    def _setup_routes(self):
        """ルーティング設定"""
        self._setup_data_routes()
        self._setup_health_routes()
        self._setup_task_routes()

    def _setup_data_routes(self):
        """データ取得関連ルート設定"""

        @self.app.route("/internal/fetch-stock-data", methods=["POST"])
        def fetch_stock_data():
            """Yahoo Finance から株価データを取得"""
            try:
                data = request.get_json()
                validation_error = self._validate_fetch_request(data)
                if validation_error:
                    return validation_error

                symbol = data["symbol"]
                period = data["period"]
                fetch_id = data.get("fetch_id", str(uuid.uuid4()))

                self._start_background_fetch(fetch_id, symbol, period)
                estimated_records = self._estimate_records(period)

                return jsonify(
                    {
                        "success": True,
                        "data": {
                            "status": "started",
                            "fetch_id": fetch_id,
                            "symbol": symbol,
                            "period": period,
                            "estimated_records": estimated_records,
                            "processing_time_estimate": estimated_records * 50,
                        },
                    }
                )
            except Exception as e:
                logger.error(f"データ取得開始エラー: {e}")
                return jsonify({"success": False, "error": "データ取得の開始に失敗しました"}), 500

    def _setup_health_routes(self):
        """ヘルスチェック関連ルート設定"""

        @self.app.route("/internal/health", methods=["GET"])
        def health_check():
            """サービスの稼働状況とYahoo Finance接続確認"""
            try:
                yahoo_status = self._check_yahoo_finance_connection()
                return jsonify(
                    {
                        "success": True,
                        "data": {
                            "status": "healthy",
                            "version": "1.0.0",
                            "dependencies": {"yahoo_finance": yahoo_status},
                            "system": {"active_tasks": len(self.active_tasks)},
                        },
                    }
                )
            except Exception as e:
                logger.error(f"ヘルスチェックエラー: {e}")
                return jsonify({"success": False, "error": "ヘルスチェックに失敗しました"}), 500

    def _setup_task_routes(self):
        """タスク管理関連ルート設定"""

        @self.app.route("/internal/task/<task_id>/status", methods=["GET"])
        def get_task_status(task_id):
            """タスクの進捗状況を取得"""
            try:
                if task_id not in self.active_tasks:
                    return jsonify({"success": False, "error": "タスクが見つかりません"}), 404
                task_info = self.active_tasks[task_id]
                return jsonify({"success": True, "data": task_info})
            except Exception as e:
                logger.error(f"タスク状況取得エラー: {e}")
                return jsonify({"success": False, "error": "タスク状況の取得に失敗しました"}), 500

    def _validate_fetch_request(self, data):
        """データ取得リクエストのバリデーション"""
        required_fields = ["symbol", "period"]
        for field in required_fields:
            if not data or field not in data:
                return (
                    jsonify({"success": False, "error": f"{field} パラメータが必要です"}),
                    400,
                )

        period = data["period"]
        valid_periods = [
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
        if period not in valid_periods:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f'無効な期間です。有効な値: {", ".join(valid_periods)}',
                    }
                ),
                400,
            )
        return None

    def _start_background_fetch(self, fetch_id, symbol, period):
        """バックグラウンドでデータ取得開始"""
        thread = threading.Thread(
            target=self._fetch_data_background, args=(fetch_id, symbol, period)
        )
        thread.daemon = True
        thread.start()

    def _fetch_data_background(self, fetch_id: str, symbol: str, period: str):
        """バックグラウンドでのデータ取得処理"""
        try:
            # タスク情報を初期化
            self.active_tasks[fetch_id] = {
                "fetch_id": fetch_id,
                "symbol": symbol,
                "period": period,
                "status": "running",
                "progress": {"current": 0, "total": 100, "percentage": 0},
                "current_status": "データ取得を開始しています...",
                "start_time": datetime.now().isoformat(),
                "data": None,
                "error": None,
            }

            logger.info(f"データ取得開始: {symbol} ({period})")

            # Yahoo Finance からデータ取得
            ticker = yf.Ticker(symbol)

            # 進捗更新
            self.active_tasks[fetch_id]["progress"]["current"] = 25
            self.active_tasks[fetch_id]["progress"]["percentage"] = 25
            self.active_tasks[fetch_id]["current_status"] = "Yahoo Finance に接続しています..."

            # データ取得
            hist = ticker.hist(period=period)

            if hist.empty:
                raise ValueError(f"銘柄 {symbol} のデータが見つかりません")

            # 進捗更新
            self.active_tasks[fetch_id]["progress"]["current"] = 75
            self.active_tasks[fetch_id]["progress"]["percentage"] = 75
            self.active_tasks[fetch_id]["current_status"] = "データを処理しています..."

            # データ整形
            processed_data = self._process_stock_data(hist, symbol)

            # 完了
            self.active_tasks[fetch_id].update(
                {
                    "status": "completed",
                    "progress": {"current": 100, "total": 100, "percentage": 100},
                    "current_status": "データ取得が完了しました",
                    "data": processed_data,
                    "end_time": datetime.now().isoformat(),
                }
            )

            logger.info(f"データ取得完了: {symbol} ({len(processed_data['records'])} レコード)")

        except Exception as e:
            logger.error(f"データ取得エラー ({fetch_id}): {e}")

            # エラー情報を更新
            if fetch_id in self.active_tasks:
                self.active_tasks[fetch_id].update(
                    {
                        "status": "failed",
                        "current_status": f"エラーが発生しました: {str(e)}",
                        "error": str(e),
                        "end_time": datetime.now().isoformat(),
                    }
                )

    def _process_stock_data(self, hist: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """株価データの処理と整形"""
        records = []

        for date, row in hist.iterrows():
            records.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"]) if pd.notna(row["Volume"]) else 0,
                }
            )

        return {
            "symbol": symbol,
            "records": records,
            "summary": {
                "total_records": len(records),
                "date_range": {
                    "start": records[0]["date"] if records else None,
                    "end": records[-1]["date"] if records else None,
                },
                "latest_close": records[-1]["close"] if records else None,
            },
        }

    def _estimate_records(self, period: str) -> int:
        """期間に基づく推定レコード数"""
        estimates = {
            "1d": 1,
            "5d": 5,
            "1mo": 22,
            "3mo": 66,
            "6mo": 132,
            "1y": 252,
            "2y": 504,
            "5y": 1260,
            "10y": 2520,
            "ytd": 200,
            "max": 5000,
        }
        return estimates.get(period, 252)

    def _check_yahoo_finance_connection(self) -> Dict[str, Any]:
        """Yahoo Finance接続確認"""
        try:
            start_time = time.time()

            # 簡単なテスト取得
            ticker = yf.Ticker("AAPL")
            ticker.info  # 接続テスト用

            response_time = int((time.time() - start_time) * 1000)

            return {
                "status": "reachable",
                "response_time_ms": response_time,
                "last_check": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.warning(f"Yahoo Finance接続テスト失敗: {e}")
            return {
                "status": "unreachable",
                "error": str(e),
                "last_check": datetime.now().isoformat(),
            }

    def run(self, host="0.0.0.0", port=8001, debug=False):
        """アプリケーション起動"""
        logger.info(f"Financial Data Service starting on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)


def create_app():
    """アプリケーションファクトリ"""
    service = FinancialDataService()
    return service.app


if __name__ == "__main__":
    service = FinancialDataService()
    service.run(debug=True)
