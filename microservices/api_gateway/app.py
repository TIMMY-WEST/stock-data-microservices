import logging
import os
from typing import Any, Dict

import requests
from flask import Flask, Response, jsonify, render_template, request
from flask_cors import CORS

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIGateway:
    def __init__(self) -> None:
        self.app = Flask(__name__)
        CORS(self.app)

        # サービスURL設定（MVP時は内部モジュール、将来はHTTP通信）
        self.service_urls = {
            "financial_data": os.getenv("FINANCIAL_DATA_SERVICE_URL", "internal"),
            "data_management": os.getenv("DATA_MANAGEMENT_SERVICE_URL", "internal"),
            "notification": os.getenv("NOTIFICATION_SERVICE_URL", "internal"),
        }

        self._setup_routes()

    def _setup_routes(self) -> None:
        """ルーティング設定"""
        self._setup_frontend_routes()
        self._setup_api_routes()
        self._setup_health_routes()

    def _setup_frontend_routes(self) -> None:
        """フロントエンド関連ルート設定"""

        @self.app.route("/")
        def index() -> str:
            """メイン画面の配信"""
            return render_template("index.html")

    def _setup_api_routes(self) -> None:
        """API関連ルート設定"""
        self._setup_fetch_route()
        self._setup_status_route()
        self._setup_stocks_route()

    def _setup_fetch_route(self) -> None:
        """データ取得ルート設定"""

        @self.app.route("/api/fetch-data", methods=["POST"])
        def fetch_data() -> Response | tuple[Response, int]:
            """株価データ取得開始（Financial Data Serviceに転送）"""
            try:
                data = request.get_json()
                if not data or "symbol" not in data:
                    return (
                        jsonify({"success": False, "error": "symbol パラメータが必要です"}),
                        400,
                    )
                result = self._forward_to_service(
                    "financial_data", "/internal/fetch-stock-data", data
                )
                return jsonify(result)
            except Exception as e:
                logger.error(f"データ取得エラー: {e}")
                return jsonify({"success": False, "error": "データ取得に失敗しました"}), 500

    def _setup_status_route(self) -> None:
        """ステータス確認ルート設定"""

        @self.app.route("/api/fetch-status", methods=["GET"])
        def fetch_status() -> Response | tuple[Response, int]:
            """データ取得進捗確認（Notification Serviceに転送）"""
            try:
                fetch_id = request.args.get("fetch_id")
                if not fetch_id:
                    return (
                        jsonify({"success": False, "error": "fetch_id パラメータが必要です"}),
                        400,
                    )
                result = self._forward_to_service(
                    "notification", f"/internal/task/{fetch_id}/status"
                )
                return jsonify(result)
            except Exception as e:
                logger.error(f"進捗確認エラー: {e}")
                return jsonify({"success": False, "error": "進捗確認に失敗しました"}), 500

    def _setup_stocks_route(self) -> None:
        """株価データ一覧ルート設定"""

        @self.app.route("/api/stocks", methods=["GET"])
        def get_stocks() -> Response | tuple[Response, int]:
            """取得済み株価データ一覧（Data Management Serviceに転送）"""
            try:
                params = {
                    "page": request.args.get("page", 1),
                    "per_page": request.args.get("per_page", 12),
                    "symbol": request.args.get("symbol"),
                }
                result = self._forward_to_service(
                    "data_management", "/internal/stocks", params=params
                )
                return jsonify(result)
            except Exception as e:
                logger.error(f"株価データ取得エラー: {e}")
                return jsonify({"success": False, "error": "株価データ取得に失敗しました"}), 500

    def _setup_health_routes(self) -> None:
        """ヘルスチェック関連ルート設定"""

        @self.app.route("/health", methods=["GET"])
        def health_check() -> Response | tuple[Response, int]:
            """システム全体の稼働状況確認"""
            try:
                services_status = self._check_all_services_health()
                return jsonify(
                    {
                        "success": True,
                        "data": {
                            "status": "healthy",
                            "version": "1.0.0",
                            "services": services_status,
                        },
                    }
                )
            except Exception as e:
                logger.error(f"ヘルスチェックエラー: {e}")
                return jsonify({"success": False, "error": "ヘルスチェックに失敗しました"}), 500

    def _check_all_services_health(self) -> Dict[str, str]:
        """全サービスのヘルスチェック"""
        services_status = {}
        for service_name, url in self.service_urls.items():
            try:
                if url == "internal":
                    services_status[service_name] = "healthy"
                else:
                    response = requests.get(f"{url}/internal/health", timeout=5)
                    services_status[service_name] = (
                        "healthy" if response.status_code == 200 else "unhealthy"
                    )
            except Exception:
                services_status[service_name] = "unhealthy"
        return services_status

    def _forward_to_service(
        self,
        service_name: str,
        endpoint: str,
        data: Dict[str, Any] = None,
        params: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """サービスへのリクエスト転送"""
        service_url = self.service_urls.get(service_name)

        if service_url == "internal":
            # MVP時は内部モジュール呼び出し（将来実装）
            return {
                "success": True,
                "message": f"{service_name} サービスへの内部転送（未実装）",
                "data": {},
            }
        else:
            # 将来のHTTP通信時
            try:
                url = f"{service_url}{endpoint}"
                if data:
                    response = requests.post(url, json=data, timeout=30)
                else:
                    response = requests.get(url, params=params, timeout=30)

                result: Dict[str, Any] = response.json()
                return result
            except Exception as e:
                logger.error(f"サービス転送エラー ({service_name}): {e}")
                raise

    def run(self, host: str = "0.0.0.0", port: int = 8000, debug: bool = False) -> None:
        """アプリケーション起動"""
        logger.info(f"API Gateway starting on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)


def create_app() -> Flask:
    """アプリケーションファクトリ関数"""
    gateway = APIGateway()
    return gateway.app


if __name__ == "__main__":
    gateway = APIGateway()
    gateway.run(host="0.0.0.0", port=8000, debug=True)
