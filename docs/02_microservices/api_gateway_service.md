# API Gateway Service 仕様書

## 1. サービス概要

### 1.1 役割
- フロントエンドからの全リクエストを受信
- 適切なマイクロサービスにリクエストをルーティング
- 統一されたAPIエンドポイントの提供
- エラーハンドリングとレスポンス統一

### 1.2 技術スタック
- **Framework**: Flask 3.0+
- **Port**: 8000
- **Dependencies**: requests, flask-cors
- **Current Implementation**: MVP版では単一Flaskアプリが担当

## 2. API エンドポイント仕様

### 2.1 フロントエンド配信

#### GET /
メイン画面の配信

```http
GET / HTTP/1.1
Host: localhost:8000
```

**レスポンス:**
```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8

<!DOCTYPE html>
<html>
<!-- Alpine.js + Tailwind CSS のSPA -->
</html>
```

#### GET /static/{filename}
静的ファイル配信

```http
GET /static/css/styles.css HTTP/1.1
Host: localhost:8000
```

### 2.2 API プロキシエンドポイント

#### POST /api/fetch-data
株価データ取得開始（Financial Data Serviceに転送）

**リクエスト:**
```http
POST /api/fetch-data HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "symbol": "7203.T",
  "period": "1y"
}
```

**転送先**: Financial Data Service `/internal/fetch-stock-data`

**レスポンス:**
```json
{
  "success": true,
  "data": {
    "fetch_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "status": "started",
    "symbol": "7203.T",
    "period": "1y",
    "estimated_records": 252
  },
  "message": "データ取得を開始しました",
  "timestamp": "2024-01-15T10:30:00+09:00"
}
```

#### GET /api/fetch-status
データ取得進捗確認（Notification Serviceに転送）

**リクエスト:**
```http
GET /api/fetch-status?fetch_id=f47ac10b-58cc-4372-a567-0e02b2c3d479 HTTP/1.1
Host: localhost:8000
```

**転送先**: Notification Service `/internal/task/{id}/status`

**レスポンス:**
```json
{
  "success": true,
  "data": {
    "fetch_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "status": "running",
    "symbol": "7203.T",
    "progress": {
      "current": 150,
      "total": 252,
      "percentage": 59.5
    },
    "current_status": "データを処理しています... (150/252)",
    "start_time": "2024-01-15T10:30:00+09:00"
  },
  "timestamp": "2024-01-15T10:30:30+09:00"
}
```

#### GET /api/stocks
取得済み株価データ一覧（Data Management Serviceに転送）

**リクエスト:**
```http
GET /api/stocks?page=1&per_page=12&symbol=7203.T HTTP/1.1
Host: localhost:8000
```

**転送先**: Data Management Service `/internal/stocks`

**レスポンス:**
```json
{
  "success": true,
  "data": {
    "stocks": [
      {
        "symbol": "7203.T",
        "company_name": "トヨタ自動車",
        "data_count": 252,
        "date_range": {
          "start": "2023-01-15",
          "end": "2024-01-15"
        },
        "latest_close": 2530.75,
        "latest_date": "2024-01-15"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 12,
      "total": 1,
      "pages": 1
    }
  }
}
```

### 2.3 ヘルスチェック

#### GET /health
システム全体の稼働状況確認

```http
GET /health HTTP/1.1
Host: localhost:8000
```

**レスポンス:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "services": {
      "financial_data": "healthy",
      "data_management": "healthy",
      "notification": "healthy"
    }
  }
}
```

## 3. サービス間通信

### 3.1 内部サービス通信設定

```python
# config.py - サービスURL設定
class Config:
    # MVP時は内部モジュール呼び出し
    FINANCIAL_DATA_SERVICE_URL = 'internal'  # services.yahoo_finance
    DATA_MANAGEMENT_SERVICE_URL = 'internal'  # services.database
    NOTIFICATION_SERVICE_URL = 'internal'     # services.progress

class ProductionConfig:
    # 将来のマイクロサービス時
    FINANCIAL_DATA_SERVICE_URL = 'http://financial-data:8001'
    DATA_MANAGEMENT_SERVICE_URL = 'http://data-mgmt:8002'
    NOTIFICATION_SERVICE_URL = 'http://notification:8004'
```

### 3.2 リクエスト転送ロジック

```python
# routes/api.py - API Gateway実装例
import httpx
from flask import Blueprint, request, jsonify, current_app

api = Blueprint('api', __name__, url_prefix='/api')

class ServiceClient:
    def __init__(self):
        self.financial_data_url = current_app.config['FINANCIAL_DATA_SERVICE_URL']
        self.data_mgmt_url = current_app.config['DATA_MANAGEMENT_SERVICE_URL']
        self.notification_url = current_app.config['NOTIFICATION_SERVICE_URL']

    async def call_financial_data_service(self, endpoint, method='GET', data=None):
        """Financial Data Serviceへのリクエスト"""
        if self.financial_data_url == 'internal':
            # MVP時は内部モジュール呼び出し
            from services.yahoo_finance import YahooFinanceService
            service = YahooFinanceService()
            return await service.handle_request(endpoint, method, data)
        else:
            # マイクロサービス時はHTTP通信
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method, f"{self.financial_data_url}{endpoint}", json=data
                )
                return response.json()

@api.route('/fetch-data', methods=['POST'])
async def fetch_data():
    """株価データ取得開始"""
    try:
        data = request.get_json()

        # バリデーション
        errors = validate_fetch_request(data)
        if errors:
            return error_response('VALIDATION_ERROR', errors), 422

        # Financial Data Serviceに転送
        client = ServiceClient()
        result = await client.call_financial_data_service(
            '/internal/fetch-stock-data',
            'POST',
            data
        )

        return success_response(result, 'データ取得を開始しました')

    except Exception as e:
        return error_response('INTERNAL_ERROR', str(e)), 500
```

## 4. エラーハンドリング

### 4.1 統一エラーレスポンス形式

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": "Additional error details or validation errors"
  },
  "timestamp": "2024-01-15T10:30:00+09:00"
}
```

### 4.2 エラーコード一覧

| エラーコード | HTTPステータス | 説明 | 対処法 |
|-------------|---------------|------|--------|
| VALIDATION_ERROR | 422 | 入力データ形式エラー | リクエストデータを確認 |
| SERVICE_UNAVAILABLE | 503 | 内部サービス接続失敗 | サービス復旧を待つ |
| SERVICE_TIMEOUT | 408 | 内部サービスタイムアウト | 再試行 |
| INTERNAL_ERROR | 500 | 内部処理エラー | 管理者に連絡 |

### 4.3 サービスエラーハンドリング

```python
# routes/api.py - エラーハンドリング実装
async def call_service_with_fallback(service_call):
    """サービス呼び出しのエラーハンドリング"""
    try:
        return await service_call()
    except httpx.ConnectError:
        return error_response(
            'SERVICE_UNAVAILABLE',
            'サービスに接続できません'
        ), 503
    except httpx.TimeoutException:
        return error_response(
            'SERVICE_TIMEOUT',
            'サービスがタイムアウトしました'
        ), 408
    except Exception as e:
        return error_response(
            'INTERNAL_ERROR',
            f'内部エラーが発生しました: {str(e)}'
        ), 500
```

## 5. 設定・環境管理

### 5.1 環境別設定

```python
# config.py - 環境設定
import os

class Config:
    """基本設定"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')

    # CORS設定
    CORS_ORIGINS = ['http://localhost:8000']

    # サービス間通信タイムアウト
    SERVICE_TIMEOUT = 30

    # ログレベル
    LOG_LEVEL = 'INFO'

class DevelopmentConfig(Config):
    """開発環境設定"""
    DEBUG = True
    FINANCIAL_DATA_SERVICE_URL = 'internal'
    DATA_MANAGEMENT_SERVICE_URL = 'internal'
    NOTIFICATION_SERVICE_URL = 'internal'

class ProductionConfig(Config):
    """本番環境設定"""
    DEBUG = False
    FINANCIAL_DATA_SERVICE_URL = os.environ.get(
        'FINANCIAL_DATA_SERVICE_URL', 'http://financial-data:8001'
    )
    DATA_MANAGEMENT_SERVICE_URL = os.environ.get(
        'DATA_MANAGEMENT_SERVICE_URL', 'http://data-mgmt:8002'
    )
    NOTIFICATION_SERVICE_URL = os.environ.get(
        'NOTIFICATION_SERVICE_URL', 'http://notification:8004'
    )
```

## 6. 現在のMVP実装

### 6.1 MVP時の内部構造
現在のMVP版では、API Gatewayの機能は以下のファイルで実装されています：

```
app/
├── routes/
│   ├── api.py      # APIエンドポイント（Gateway相当）
│   └── main.py     # フロントエンド配信
├── services/       # 内部サービス（将来分離予定）
│   ├── yahoo_finance.py
│   ├── database.py
│   └── progress.py
└── models/
    └── stock.py
```

### 6.2 マイクロサービス移行準備

```python
# services/base.py - 将来の分離準備
from abc import ABC, abstractmethod

class BaseService(ABC):
    """マイクロサービス基底クラス"""

    @abstractmethod
    async def handle_request(self, endpoint: str, method: str, data: dict):
        """リクエスト処理の統一インターフェース"""
        pass

    @abstractmethod
    def health_check(self) -> dict:
        """ヘルスチェックの統一インターフェース"""
        pass
```

---

## まとめ

このAPI Gateway Service仕様書では：

### ✅ **現在のMVP対応**
- 単一Flaskアプリ内での実装
- 内部モジュール呼び出し
- 統一されたAPI設計

### 🚀 **将来のマイクロサービス対応**
- HTTPベースのサービス間通信準備
- 設定による切り替え可能な実装
- エラーハンドリングの統一

この設計により、MVP版から段階的にマイクロサービスに移行できます。
