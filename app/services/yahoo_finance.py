import uuid
from datetime import UTC, datetime
from typing import Dict, List, Optional

import requests


class YahooFinanceService:
    """Yahoo Finance API連携サービス"""

    def __init__(self):
        self.base_url = "https://query1.finance.yahoo.com"
        self.timeout = 30

    def fetch_stock_data(self, symbol: str) -> Optional[Dict]:
        """単一の株価データを取得"""
        try:
            # Yahoo Finance APIからリアルタイムデータを取得
            quote_url = f"{self.base_url}/v8/finance/chart/{symbol}"

            params = {"interval": "1d", "range": "1y"}

            response = requests.get(quote_url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            if "chart" not in data or "result" not in data["chart"]:
                return None

            result = data["chart"]["result"][0]
            meta = result["meta"]
            quotes = result["indicators"]["quote"][0]

            # データの整形
            stock_data = {
                "symbol": symbol,
                "company_name": meta.get("longName", symbol),
                "current_price": meta.get("regularMarketPrice", 0),
                "currency": meta.get("currency", "JPY"),
                "market_state": meta.get("marketState", "UNKNOWN"),
                "timezone": meta.get("timezone", "JST"),
                "exchange": meta.get("exchangeName", "Unknown"),
                "fetched_at": datetime.now(UTC).isoformat(),
                "historical_data": {
                    "timestamps": result.get("timestamp", []),
                    "open": quotes.get("open", []),
                    "high": quotes.get("high", []),
                    "low": quotes.get("low", []),
                    "close": quotes.get("close", []),
                    "volume": quotes.get("volume", []),
                },
            }

            return stock_data

        except requests.RequestException as e:
            print(f"Yahoo Finance APIエラー ({symbol}): {e}")
            return None
        except Exception as e:
            print(f"データ取得エラー ({symbol}): {e}")
            return None

    def fetch_multiple_symbols(self, symbols: List[str]) -> str:
        """複数の株価データを非同期で取得（タスクIDを返す）"""
        task_id = str(uuid.uuid4())

        # 実際の実装では、Celeryやバックグラウンドタスクを使用
        # MVP版では同期処理として実装
        from app.services.database import DatabaseService
        from app.services.progress import ProgressService

        progress_service = ProgressService()
        db_service = DatabaseService()

        # プログレス初期化
        progress_service.initialize_task(task_id, len(symbols))

        try:
            for i, symbol in enumerate(symbols):
                # データ取得
                stock_data = self.fetch_stock_data(symbol)

                if stock_data:
                    # データベース保存
                    db_service.save_stock_data(stock_data)
                    progress_service.update_progress(
                        task_id, i + 1, f"{symbol} データ取得完了"
                    )
                else:
                    progress_service.update_progress(
                        task_id, i + 1, f"{symbol} データ取得失敗"
                    )

            progress_service.complete_task(task_id)

        except Exception as e:
            progress_service.error_task(task_id, str(e))

        return task_id

    def validate_symbol(self, symbol: str) -> bool:
        """シンボルの有効性をチェック"""
        try:
            search_url = f"{self.base_url}/v1/finance/search"
            params = {"q": symbol}

            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            quotes = data.get("quotes", [])

            # 完全一致するシンボルがあるかチェック
            for quote in quotes:
                if quote.get("symbol") == symbol:
                    return True

            return False

        except Exception:
            return False
