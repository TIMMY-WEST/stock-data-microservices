# API仕様書 (MVP版)

## 1. API概要

### 1.1 基本情報
- **ベースURL**: `http://localhost:8000`
- **APIバージョン**: v1 (MVP)
- **データ形式**: JSON
- **文字エンコーディング**: UTF-8
- **認証**: なし (MVP では認証省略)

### 1.2 共通仕様

#### リクエストヘッダー
```http
Content-Type: application/json
Accept: application/json
```

#### レスポンス形式
```json
{
  "success": true,
  "data": {...},
  "message": "Success message",
  "timestamp": "2024-01-15T10:30:00+09:00"
}
```

#### エラーレスポンス形式
```json
{
  "success": false,
  "error": {
    "code": "INVALID_SYMBOL",
    "message": "Invalid symbol format",
    "details": "Symbol must be in format NNNN.T"
  },
  "timestamp": "2024-01-15T10:30:00+09:00"
}
```

### 1.3 ステータスコード

| コード | 説明 | 用途 |
|--------|------|------|
| 200 | OK | 正常処理 |
| 201 | Created | リソース作成 |
| 400 | Bad Request | リクエスト形式エラー |
| 404 | Not Found | リソース未存在 |
| 422 | Unprocessable Entity | バリデーションエラー |
| 500 | Internal Server Error | サーバー内部エラー |

## 2. エンドポイント仕様

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

### 2.2 株価データ取得API

#### POST /api/fetch-data
株価データの取得を開始

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

**リクエストパラメータ:**

| パラメータ | 型 | 必須 | 説明 | 例 |
|-----------|---|------|------|---|
| symbol | string | ✅ | 銘柄コード | "7203.T" |
| period | string | ✅ | 取得期間 | "1y", "5y", "max" |

**バリデーションルール:**
- `symbol`: 正規表現 `^[0-9]{4}\.T$`
- `period`: ["1y", "5y", "max"] のいずれか

**レスポンス (成功):**
```http
HTTP/1.1 200 OK
Content-Type: application/json

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

**レスポンス (バリデーションエラー):**
```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json

{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "入力データが正しくありません",
    "details": {
      "symbol": ["銘柄コードの形式が正しくありません (例: 7203.T)"],
      "period": ["期間は 1y, 5y, max のいずれかを指定してください"]
    }
  },
  "timestamp": "2024-01-15T10:30:00+09:00"
}
```

**レスポンス (外部API エラー):**
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "success": false,
  "error": {
    "code": "SYMBOL_NOT_FOUND",
    "message": "指定された銘柄が見つかりません",
    "details": "Yahoo Finance APIで該当する銘柄データが存在しません"
  },
  "timestamp": "2024-01-15T10:30:00+09:00"
}
```

#### GET /api/fetch-status
データ取得の進捗状況を確認

**リクエスト:**
```http
GET /api/fetch-status?fetch_id=f47ac10b-58cc-4372-a567-0e02b2c3d479 HTTP/1.1
Host: localhost:8000
```

**クエリパラメータ:**

| パラメータ | 型 | 必須 | 説明 | 例 |
|-----------|---|------|------|---|
| fetch_id | string | ✅ | 取得処理ID | "f47ac10b-..." |

**レスポンス (処理中):**
```http
HTTP/1.1 200 OK
Content-Type: application/json

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

**レスポンス (完了):**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "data": {
    "fetch_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "status": "completed",
    "symbol": "7203.T",
    "progress": {
      "current": 252,
      "total": 252,
      "percentage": 100
    },
    "current_status": "データ取得が完了しました",
    "start_time": "2024-01-15T10:30:00+09:00",
    "end_time": "2024-01-15T10:30:45+09:00",
    "processing_time_ms": 45000,
    "records_saved": 252
  },
  "timestamp": "2024-01-15T10:30:45+09:00"
}
```

**レスポンス (エラー):**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "data": {
    "fetch_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "status": "error",
    "symbol": "7203.T",
    "progress": {
      "current": 0,
      "total": 0,
      "percentage": 0
    },
    "current_status": "データ取得中にエラーが発生しました",
    "error_message": "Yahoo Finance API connection timeout",
    "start_time": "2024-01-15T10:30:00+09:00",
    "end_time": "2024-01-15T10:30:15+09:00"
  },
  "timestamp": "2024-01-15T10:30:15+09:00"
}
```

### 2.3 株価データ取得API

#### GET /api/stocks
取得済み株価データの一覧取得

**リクエスト:**
```http
GET /api/stocks?page=1&per_page=12&symbol=7203.T HTTP/1.1
Host: localhost:8000
```

**クエリパラメータ:**

| パラメータ | 型 | 必須 | デフォルト | 説明 | 例 |
|-----------|---|------|-----------|------|---|
| page | integer | ❌ | 1 | ページ番号 | 1, 2, 3... |
| per_page | integer | ❌ | 12 | 1ページあたりの件数 | 12, 24, 48 |
| symbol | string | ❌ | - | 銘柄コードでフィルター | "7203.T" |
| start_date | string | ❌ | - | 開始日でフィルター | "2024-01-01" |
| end_date | string | ❌ | - | 終了日でフィルター | "2024-12-31" |

**レスポンス:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

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
        "latest_date": "2024-01-15",
        "created_at": "2024-01-15T10:30:45+09:00",
        "updated_at": "2024-01-15T10:30:45+09:00"
      },
      {
        "symbol": "6758.T",
        "company_name": "ソニーグループ",
        "data_count": 252,
        "date_range": {
          "start": "2023-01-15",
          "end": "2024-01-15"
        },
        "latest_close": 12450.00,
        "latest_date": "2024-01-15",
        "created_at": "2024-01-15T11:15:20+09:00",
        "updated_at": "2024-01-15T11:15:20+09:00"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 12,
      "total": 2,
      "pages": 1,
      "has_next": false,
      "has_prev": false
    }
  },
  "timestamp": "2024-01-15T12:00:00+09:00"
}
```

#### GET /api/stocks/{symbol}/data
特定銘柄の詳細データ取得

**リクエスト:**
```http
GET /api/stocks/7203.T/data?start_date=2024-01-01&end_date=2024-01-31&page=1&per_page=50 HTTP/1.1
Host: localhost:8000
```

**パスパラメータ:**

| パラメータ | 型 | 必須 | 説明 | 例 |
|-----------|---|------|------|---|
| symbol | string | ✅ | 銘柄コード | "7203.T" |

**クエリパラメータ:**

| パラメータ | 型 | 必須 | デフォルト | 説明 | 例 |
|-----------|---|------|-----------|------|---|
| start_date | string | ❌ | - | 開始日 | "2024-01-01" |
| end_date | string | ❌ | - | 終了日 | "2024-01-31" |
| page | integer | ❌ | 1 | ページ番号 | 1, 2, 3... |
| per_page | integer | ❌ | 50 | 1ページあたりの件数 | 50, 100 |

**レスポンス:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "data": {
    "symbol": "7203.T",
    "company_name": "トヨタ自動車",
    "price_data": [
      {
        "date": "2024-01-31",
        "open": 2520.00,
        "high": 2580.50,
        "low": 2510.25,
        "close": 2530.75,
        "adj_close": 2530.75,
        "volume": 1250000
      },
      {
        "date": "2024-01-30",
        "open": 2500.50,
        "high": 2525.00,
        "low": 2485.00,
        "close": 2520.00,
        "adj_close": 2520.00,
        "volume": 980000
      }
    ],
    "summary": {
      "period": {
        "start": "2024-01-01",
        "end": "2024-01-31"
      },
      "total_records": 22,
      "price_range": {
        "high": 2580.50,
        "low": 2485.00
      },
      "volume_range": {
        "max": 2100000,
        "min": 650000,
        "average": 1125000
      }
    },
    "pagination": {
      "page": 1,
      "per_page": 50,
      "total": 22,
      "pages": 1,
      "has_next": false,
      "has_prev": false
    }
  },
  "timestamp": "2024-01-15T12:00:00+09:00"
}
```

**レスポンス (銘柄未存在):**
```http
HTTP/1.1 404 Not Found
Content-Type: application/json

{
  "success": false,
  "error": {
    "code": "SYMBOL_NOT_FOUND",
    "message": "指定された銘柄のデータが存在しません",
    "details": "銘柄コード '7203.T' のデータがデータベースに存在しません"
  },
  "timestamp": "2024-01-15T12:00:00+09:00"
}
```

#### DELETE /api/stocks/{symbol}
特定銘柄のデータを削除

**リクエスト:**
```http
DELETE /api/stocks/7203.T HTTP/1.1
Host: localhost:8000
```

**レスポンス (成功):**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "data": {
    "symbol": "7203.T",
    "deleted_records": 252
  },
  "message": "銘柄データを削除しました",
  "timestamp": "2024-01-15T12:00:00+09:00"
}
```

**レスポンス (銘柄未存在):**
```http
HTTP/1.1 404 Not Found
Content-Type: application/json

{
  "success": false,
  "error": {
    "code": "SYMBOL_NOT_FOUND",
    "message": "指定された銘柄のデータが存在しません"
  },
  "timestamp": "2024-01-15T12:00:00+09:00"
}
```

### 2.4 ヘルスチェックAPI

#### GET /health
システムの稼働状況確認

**リクエスト:**
```http
GET /health HTTP/1.1
Host: localhost:8000
```

**レスポンス (正常):**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "uptime_seconds": 3600,
    "dependencies": {
      "database": {
        "status": "connected",
        "response_time_ms": 15
      },
      "yahoo_finance": {
        "status": "reachable",
        "response_time_ms": 250
      }
    },
    "system": {
      "memory_usage_mb": 128,
      "cpu_usage_percent": 12
    }
  },
  "timestamp": "2024-01-15T12:00:00+09:00"
}
```

**レスポンス (異常):**
```http
HTTP/1.1 500 Internal Server Error
Content-Type: application/json

{
  "success": false,
  "error": {
    "code": "SYSTEM_UNHEALTHY",
    "message": "システムに異常があります",
    "details": "データベース接続に失敗しています"
  },
  "data": {
    "status": "unhealthy",
    "dependencies": {
      "database": {
        "status": "disconnected",
        "error": "Connection timeout"
      }
    }
  },
  "timestamp": "2024-01-15T12:00:00+09:00"
}
```

## 3. エラーコード一覧

### 3.1 バリデーションエラー (4xx)

| エラーコード | HTTPステータス | 説明 | 対処法 |
|-------------|---------------|------|--------|
| VALIDATION_ERROR | 422 | 入力データ形式エラー | リクエストデータを確認 |
| INVALID_SYMBOL | 422 | 銘柄コード形式エラー | NNNN.T形式で入力 |
| INVALID_PERIOD | 422 | 期間指定エラー | 1y/5y/max のいずれかを指定 |
| INVALID_DATE_RANGE | 422 | 日付範囲エラー | 開始日≦終了日で指定 |
| SYMBOL_NOT_FOUND | 404 | 銘柄データ未存在 | データ取得後に再試行 |

### 3.2 外部API エラー (4xx)

| エラーコード | HTTPステータス | 説明 | 対処法 |
|-------------|---------------|------|--------|
| YAHOO_API_ERROR | 400 | Yahoo Finance API エラー | 銘柄コードを確認 |
| YAHOO_API_TIMEOUT | 408 | Yahoo Finance API タイムアウト | 再試行 |
| YAHOO_API_RATE_LIMIT | 429 | Yahoo Finance API 制限 | 時間をおいて再試行 |

### 3.3 システムエラー (5xx)

| エラーコード | HTTPステータス | 説明 | 対処法 |
|-------------|---------------|------|--------|
| DATABASE_ERROR | 500 | データベースエラー | 管理者に連絡 |
| INTERNAL_ERROR | 500 | 内部処理エラー | 管理者に連絡 |
| SYSTEM_UNHEALTHY | 503 | システム異常 | 復旧まで待機 |

## 4. 実装例

### 4.1 Flask ルートハンドラー例

```python
# app/routes/api.py
from flask import Blueprint, request, jsonify
from app.services.yahoo_finance import YahooFinanceService
from app.services.database import DatabaseService
import uuid
from datetime import datetime

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/fetch-data', methods=['POST'])
def fetch_data():
    """株価データ取得開始"""
    try:
        data = request.get_json()

        # バリデーション
        errors = validate_fetch_request(data)
        if errors:
            return error_response(
                'VALIDATION_ERROR',
                '入力データが正しくありません',
                details=errors
            ), 422

        symbol = data['symbol'].upper()
        period = data['period']

        # 取得ID生成
        fetch_id = str(uuid.uuid4())

        # バックグラウンドでデータ取得開始
        yahoo_service = YahooFinanceService()
        yahoo_service.fetch_stock_data_async(fetch_id, symbol, period)

        return success_response({
            'fetch_id': fetch_id,
            'status': 'started',
            'symbol': symbol,
            'period': period,
            'estimated_records': estimate_records(period)
        }, 'データ取得を開始しました')

    except Exception as e:
        return error_response('INTERNAL_ERROR', str(e)), 500

@api.route('/fetch-status', methods=['GET'])
def fetch_status():
    """データ取得進捗確認"""
    try:
        fetch_id = request.args.get('fetch_id')

        if not fetch_id:
            return error_response(
                'VALIDATION_ERROR',
                'fetch_id パラメータが必要です'
            ), 422

        # 進捗状況取得
        progress_service = ProgressService()
        status = progress_service.get_fetch_status(fetch_id)

        if not status:
            return error_response(
                'FETCH_NOT_FOUND',
                '指定された取得処理が見つかりません'
            ), 404

        return success_response(status)

    except Exception as e:
        return error_response('INTERNAL_ERROR', str(e)), 500

@api.route('/stocks', methods=['GET'])
def get_stocks():
    """株価データ一覧取得"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 12))
        symbol = request.args.get('symbol')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        db_service = DatabaseService()
        result = db_service.get_stock_list(
            page=page,
            per_page=per_page,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )

        return success_response(result)

    except Exception as e:
        return error_response('INTERNAL_ERROR', str(e)), 500

def validate_fetch_request(data):
    """リクエストデータバリデーション"""
    errors = {}

    if not data.get('symbol'):
        errors['symbol'] = ['銘柄コードは必須です']
    elif not re.match(r'^[0-9]{4}\.T$', data['symbol']):
        errors['symbol'] = ['銘柄コードの形式が正しくありません (例: 7203.T)']

    if not data.get('period'):
        errors['period'] = ['期間は必須です']
    elif data['period'] not in ['1y', '5y', 'max']:
        errors['period'] = ['期間は 1y, 5y, max のいずれかを指定してください']

    return errors if errors else None

def success_response(data=None, message=None):
    """成功レスポンス生成"""
    return {
        'success': True,
        'data': data,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }

def error_response(code, message, details=None):
    """エラーレスポンス生成"""
    return {
        'success': False,
        'error': {
            'code': code,
            'message': message,
            'details': details
        },
        'timestamp': datetime.now().isoformat()
    }
```

### 4.2 JavaScript クライアント例

```javascript
// app/static/js/api-client.js
class StockApiClient {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
    }

    async fetchStockData(symbol, period) {
        const response = await fetch(`${this.baseURL}/api/fetch-data`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ symbol, period })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error?.message || 'データ取得に失敗しました');
        }

        return data.data;
    }

    async getFetchStatus(fetchId) {
        const response = await fetch(`${this.baseURL}/api/fetch-status?fetch_id=${fetchId}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error?.message || 'ステータス取得に失敗しました');
        }

        return data.data;
    }

    async getStocks(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const response = await fetch(`${this.baseURL}/api/stocks?${queryString}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error?.message || 'データ取得に失敗しました');
        }

        return data.data;
    }

    async deleteStock(symbol) {
        const response = await fetch(`${this.baseURL}/api/stocks/${symbol}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error?.message || '削除に失敗しました');
        }

        return data.data;
    }
}
```

## 5. テスト例

### 5.1 APIテスト (Pytest)

```python
# tests/test_api.py
import pytest
import json
from app import create_app

@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.test_client() as client:
        yield client

def test_fetch_data_success(client):
    """正常な株価データ取得リクエスト"""
    response = client.post('/api/fetch-data',
        data=json.dumps({
            'symbol': '7203.T',
            'period': '1y'
        }),
        content_type='application/json'
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'fetch_id' in data['data']
    assert data['data']['symbol'] == '7203.T'

def test_fetch_data_validation_error(client):
    """バリデーションエラーのテスト"""
    response = client.post('/api/fetch-data',
        data=json.dumps({
            'symbol': 'INVALID',
            'period': 'invalid_period'
        }),
        content_type='application/json'
    )

    assert response.status_code == 422
    data = json.loads(response.data)
    assert data['success'] == False
    assert data['error']['code'] == 'VALIDATION_ERROR'

def test_get_stocks(client):
    """株価データ一覧取得テスト"""
    response = client.get('/api/stocks?page=1&per_page=12')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'stocks' in data['data']
    assert 'pagination' in data['data']
```

## まとめ

このMVP版API仕様書では：

### ✅ **実装範囲**
- 株価データ取得・進捗確認API
- データ一覧・詳細・削除API
- ヘルスチェックAPI
- 詳細なエラーハンドリング

### 🛠️ **実装支援**
- 完全なリクエスト・レスポンス例
- Flaskルートハンドラーサンプル
- JavaScriptクライアントサンプル
- テストコード例

### 🚀 **拡張準備**
- バージョニング対応
- 認証機能追加準備
- 詳細なエラーコード体系

この仕様書により、フロントエンド・バックエンドの**並行開発**が可能になります！
