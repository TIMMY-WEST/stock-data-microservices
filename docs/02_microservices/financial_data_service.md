# Financial Data Service 仕様書

## 1. サービス概要

### 1.1 役割
- Yahoo Finance API からの株価データ取得
- データの検証・整形
- バックグラウンドでの非同期データ取得処理
- 外部API のエラーハンドリング

### 1.2 技術スタック
- **Framework**: FastAPI (将来) / Flask内モジュール (MVP)
- **Port**: 8001 (将来) / internal (MVP)
- **Dependencies**: yfinance, pandas, numpy, httpx
- **Current Implementation**: `services/yahoo_finance.py`

## 2. 内部API仕様（マイクロサービス時）

### 2.1 株価データ取得

#### POST /internal/fetch-stock-data
Yahoo Finance から株価データを取得

**リクエスト:**
```http
POST /internal/fetch-stock-data HTTP/1.1
Content-Type: application/json

{
  "symbol": "7203.T",
  "period": "1y",
  "fetch_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
}
```

**リクエストパラメータ:**
| パラメータ | 型 | 必須 | 説明 | 例 |
|-----------|---|------|------|---|
| symbol | string | ✅ | 銘柄コード | "7203.T" |
| period | string | ✅ | 取得期間 | "1y", "5y", "max" |
| fetch_id | string | ✅ | 取得処理ID | UUID形式 |

**レスポンス:**
```json
{
  "status": "started",
  "fetch_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "symbol": "7203.T",
  "estimated_records": 252,
  "processing_time_estimate": 15000
}
```

### 2.2 ヘルスチェック

#### GET /internal/health
サービスの稼働状況とYahoo Finance接続確認

**リクエスト:**
```http
GET /internal/health HTTP/1.1
```

**レスポンス:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "dependencies": {
    "yahoo_finance": {
      "status": "reachable",
      "response_time_ms": 250,
      "last_check": "2024-01-15T10:30:00+09:00"
    }
  },
  "system": {
    "memory_usage_mb": 64,
    "active_tasks": 2
  }
}
```

## 3. Yahoo Finance連携

### 3.1 データ取得ロジック

```python
# services/yahoo_finance.py - データ取得実装
import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional
import asyncio
import logging

class YahooFinanceService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    async def fetch_stock_data(
        self, 
        symbol: str, 
        period: str = "1y",
        fetch_id: Optional[str] = None
    ) -> Dict:
        """
        Yahoo Finance から株価データを取得
        
        Args:
            symbol: 銘柄コード (e.g., "7203.T")
            period: 取得期間 ("1y", "5y", "max")
            fetch_id: 取得処理ID（進捗管理用）
            
        Returns:
            取得結果とデータ
        """
        try:
            self.logger.info(f"Starting fetch for {symbol}, period: {period}")
            
            # 進捗通知サービスに開始を通知
            if fetch_id:
                await self._notify_progress(fetch_id, "started", 0, 0)
            
            # Yahoo Finance からデータ取得
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            
            if df.empty:
                raise ValueError(f"No data found for symbol {symbol}")
            
            # データ変換・整形
            stock_data = await self._convert_to_stock_data(df, symbol)
            
            # 進捗通知
            if fetch_id:
                await self._notify_progress(
                    fetch_id, "processing", len(stock_data), len(stock_data)
                )
            
            # データ保存サービスに送信
            save_result = await self._save_to_database(symbol, stock_data)
            
            # 完了通知
            if fetch_id:
                await self._notify_progress(
                    fetch_id, "completed", len(stock_data), len(stock_data)
                )
            
            return {
                "status": "success",
                "symbol": symbol,
                "records_processed": len(stock_data),
                "date_range": {
                    "start": stock_data[0]["date"] if stock_data else None,
                    "end": stock_data[-1]["date"] if stock_data else None
                },
                "save_result": save_result
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {str(e)}")
            
            # エラー通知
            if fetch_id:
                await self._notify_progress(
                    fetch_id, "error", 0, 0, str(e)
                )
            
            raise
    
    async def _convert_to_stock_data(
        self, 
        df: pd.DataFrame, 
        symbol: str
    ) -> List[Dict]:
        """DataFrame を標準的な株価データ形式に変換"""
        stock_data = []
        
        for date, row in df.iterrows():
            stock_data.append({
                "symbol": symbol,
                "date": date.strftime("%Y-%m-%d"),
                "open": float(row["Open"]) if pd.notna(row["Open"]) else None,
                "high": float(row["High"]) if pd.notna(row["High"]) else None,
                "low": float(row["Low"]) if pd.notna(row["Low"]) else None,
                "close": float(row["Close"]) if pd.notna(row["Close"]) else None,
                "adj_close": float(row["Adj Close"]) if pd.notna(row["Adj Close"]) else None,
                "volume": int(row["Volume"]) if pd.notna(row["Volume"]) else None
            })
        
        return stock_data
    
    async def _save_to_database(
        self, 
        symbol: str, 
        stock_data: List[Dict]
    ) -> Dict:
        """Data Management Service にデータ保存を依頼"""
        # MVP時は内部モジュール呼び出し
        from services.database import DatabaseService
        
        db_service = DatabaseService()
        return await db_service.save_stock_data(symbol, stock_data)
    
    async def _notify_progress(
        self, 
        fetch_id: str, 
        status: str, 
        current: int, 
        total: int,
        error_message: Optional[str] = None
    ):
        """Notification Service に進捗を通知"""
        # MVP時は内部モジュール呼び出し
        from services.progress import ProgressService
        
        progress_service = ProgressService()
        await progress_service.update_progress(
            fetch_id, status, current, total, error_message
        )
```

### 3.2 データバリデーション

```python
# services/yahoo_finance.py - データ検証
class DataValidator:
    @staticmethod
    def validate_symbol(symbol: str) -> bool:
        """銘柄コード形式の検証"""
        import re
        # 日本株式: 4桁数字.T
        if re.match(r'^[0-9]{4}\.T$', symbol):
            return True
        # 将来他の市場にも対応
        return False
    
    @staticmethod
    def validate_period(period: str) -> bool:
        """期間指定の検証"""
        valid_periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
        return period in valid_periods
    
    @staticmethod
    def validate_stock_data(data: List[Dict]) -> List[str]:
        """取得したデータの検証"""
        errors = []
        
        if not data:
            errors.append("No data received")
            return errors
        
        for i, record in enumerate(data):
            if not record.get("date"):
                errors.append(f"Missing date in record {i}")
            
            # 価格データの妥当性チェック
            if record.get("open") and record.get("close"):
                if record["open"] <= 0 or record["close"] <= 0:
                    errors.append(f"Invalid price data in record {i}")
        
        return errors
```

### 3.3 エラーハンドリング

```python
# services/yahoo_finance.py - エラー処理
class YahooFinanceError(Exception):
    """Yahoo Finance関連のカスタム例外"""
    pass

class YahooFinanceService:
    async def _handle_yahoo_finance_errors(self, symbol: str, error: Exception):
        """Yahoo Finance APIのエラーを分類・処理"""
        
        if "No data found" in str(error):
            return {
                "error_code": "SYMBOL_NOT_FOUND",
                "error_message": f"銘柄 {symbol} のデータが見つかりません",
                "retry_recommended": False
            }
        
        elif "timeout" in str(error).lower():
            return {
                "error_code": "YAHOO_API_TIMEOUT", 
                "error_message": "Yahoo Finance APIがタイムアウトしました",
                "retry_recommended": True
            }
        
        elif "rate limit" in str(error).lower():
            return {
                "error_code": "YAHOO_API_RATE_LIMIT",
                "error_message": "Yahoo Finance APIの利用制限に達しました", 
                "retry_recommended": True,
                "retry_after": 300  # 5分後
            }
        
        else:
            return {
                "error_code": "YAHOO_API_ERROR",
                "error_message": f"Yahoo Finance APIエラー: {str(error)}",
                "retry_recommended": True
            }
```

## 4. バックグラウンド処理

### 4.1 非同期タスク管理

```python
# services/yahoo_finance.py - バックグラウンド処理
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List
import uuid

class BackgroundTaskManager:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.running_tasks = {}
    
    async def start_fetch_task(
        self, 
        symbols: List[str], 
        period: str = "1y"
    ) -> str:
        """複数銘柄の並列取得を開始"""
        
        task_id = str(uuid.uuid4())
        
        # バックグラウンドでタスク実行
        task = asyncio.create_task(
            self._fetch_multiple_symbols(symbols, period, task_id)
        )
        
        self.running_tasks[task_id] = {
            "task": task,
            "symbols": symbols,
            "status": "running",
            "start_time": datetime.now()
        }
        
        return task_id
    
    async def _fetch_multiple_symbols(
        self, 
        symbols: List[str], 
        period: str,
        task_id: str
    ):
        """複数銘柄を並列で取得"""
        
        yahoo_service = YahooFinanceService()
        
        # 並列処理でデータ取得
        tasks = [
            yahoo_service.fetch_stock_data(symbol, period, f"{task_id}_{symbol}")
            for symbol in symbols
        ]
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 結果の集計
            successful = sum(1 for r in results if not isinstance(r, Exception))
            failed = len(results) - successful
            
            self.running_tasks[task_id]["status"] = "completed"
            self.running_tasks[task_id]["results"] = {
                "successful": successful,
                "failed": failed,
                "details": results
            }
            
        except Exception as e:
            self.running_tasks[task_id]["status"] = "error"
            self.running_tasks[task_id]["error"] = str(e)
    
    def get_task_status(self, task_id: str) -> Dict:
        """タスクの状況を取得"""
        return self.running_tasks.get(task_id, {"status": "not_found"})
```

## 5. 設定・環境管理

### 5.1 サービス設定

```python
# config.py - Financial Data Service 設定
import os

class FinancialDataConfig:
    # Yahoo Finance設定
    YAHOO_FINANCE_TIMEOUT = int(os.environ.get('YAHOO_FINANCE_TIMEOUT', '30'))
    YAHOO_FINANCE_RETRY_COUNT = int(os.environ.get('YAHOO_FINANCE_RETRY_COUNT', '3'))
    YAHOO_FINANCE_RETRY_DELAY = int(os.environ.get('YAHOO_FINANCE_RETRY_DELAY', '5'))
    
    # 並列処理設定
    MAX_PARALLEL_REQUESTS = int(os.environ.get('MAX_PARALLEL_REQUESTS', '5'))
    REQUEST_RATE_LIMIT = int(os.environ.get('REQUEST_RATE_LIMIT', '10'))  # per minute
    
    # データ検証設定
    MIN_DATA_POINTS = int(os.environ.get('MIN_DATA_POINTS', '10'))
    MAX_DATA_POINTS = int(os.environ.get('MAX_DATA_POINTS', '10000'))
    
    # ログ設定
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # 他サービス連携設定（マイクロサービス時）
    DATA_MANAGEMENT_SERVICE_URL = os.environ.get(
        'DATA_MANAGEMENT_SERVICE_URL', 'http://data-mgmt:8002'
    )
    NOTIFICATION_SERVICE_URL = os.environ.get(
        'NOTIFICATION_SERVICE_URL', 'http://notification:8004'
    )
```

### 5.2 率制限・リトライ機能

```python
# services/yahoo_finance.py - 率制限対応
import time
from functools import wraps
import asyncio

class RateLimiter:
    def __init__(self, calls_per_minute: int = 10):
        self.calls_per_minute = calls_per_minute
        self.calls = []
    
    async def wait_if_needed(self):
        """必要に応じて待機"""
        now = time.time()
        
        # 1分以内の呼び出し回数をカウント
        recent_calls = [call for call in self.calls if now - call < 60]
        self.calls = recent_calls
        
        if len(recent_calls) >= self.calls_per_minute:
            wait_time = 60 - (now - recent_calls[0])
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        self.calls.append(now)

def with_retry(max_retries: int = 3, delay: int = 5):
    """リトライデコレータ"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    
                    # リトライ可能なエラーかチェック
                    if "rate limit" in str(e).lower() or "timeout" in str(e).lower():
                        wait_time = delay * (2 ** attempt)  # exponential backoff
                        await asyncio.sleep(wait_time)
                    else:
                        raise
            
        return wrapper
    return decorator
```

## 6. 現在のMVP実装

### 6.1 MVP時のファイル構造
```
services/
└── yahoo_finance.py    # 現在の実装ファイル
    ├── YahooFinanceService クラス
    ├── データ取得メソッド
    ├── バリデーション機能
    └── エラーハンドリング
```

### 6.2 マイクロサービス移行準備

```python
# services/yahoo_finance.py - 移行準備の実装
from abc import ABC, abstractmethod

class FinancialDataServiceInterface(ABC):
    """Financial Data Service インターフェース"""
    
    @abstractmethod
    async def fetch_stock_data(self, symbol: str, period: str) -> Dict:
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict:
        pass

class YahooFinanceService(FinancialDataServiceInterface):
    """Yahoo Finance実装（MVP時の内部実装）"""
    
    async def handle_request(self, endpoint: str, method: str, data: dict):
        """統一リクエストハンドラ（将来のHTTP API用）"""
        
        if endpoint == '/internal/fetch-stock-data' and method == 'POST':
            return await self.fetch_stock_data(
                data['symbol'], data['period']
            )
        
        elif endpoint == '/internal/health' and method == 'GET':
            return await self.health_check()
        
        else:
            raise ValueError(f"Unknown endpoint: {endpoint}")
```

---

## まとめ

このFinancial Data Service仕様書では：

### ✅ **現在のMVP対応**
- `services/yahoo_finance.py` での実装
- Yahoo Finance APIとの連携
- データ検証・整形機能

### 🚀 **将来のマイクロサービス対応**
- FastAPI による独立サービス化準備
- 統一されたAPI設計
- エラーハンドリングとリトライ機能

### 🛡️ **信頼性・パフォーマンス**
- 率制限対応
- 並列処理サポート
- 包括的なエラー処理

この設計により、外部APIとの安定した連携を実現し、将来の拡張に対応できます。