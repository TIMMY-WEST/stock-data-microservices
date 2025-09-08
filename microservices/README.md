# マイクロサービス基本スケルトン

このディレクトリには、株式データマイクロサービスプロジェクトの各サービスの基本スケルトンが含まれています。

## サービス構成

### 1. API Gateway Service (ポート: 8000)
- **役割**: フロントエンドからのリクエストを受け取り、適切なマイクロサービスに転送
- **エンドポイント**:
  - `GET /` - フロントエンド配信
  - `POST /api/fetch-stock-data` - 株価データ取得API
  - `GET /api/stocks` - 株価データ一覧取得API
  - `GET /health` - ヘルスチェック

### 2. Financial Data Service (ポート: 8001)
- **役割**: Yahoo Finance APIから株価データを取得
- **内部エンドポイント**:
  - `POST /internal/fetch-stock-data` - 株価データ取得
  - `GET /internal/health` - ヘルスチェック
  - `GET /internal/task/<task_id>/status` - タスク状況確認

### 3. Data Management Service (ポート: 8002)
- **役割**: データの永続化と管理（プレースホルダー）

### 4. Notification Service (ポート: 8003)
- **役割**: 通知機能（プレースホルダー）

## 起動方法

### Docker Compose を使用した起動（推奨）

```bash
# 全サービスを一括起動
cd microservices
docker-compose up -d

# ログを確認
docker-compose logs -f

# 特定のサービスのログを確認
docker-compose logs -f api-gateway
docker-compose logs -f financial-data

# サービス停止
docker-compose down
```

### 個別サービスの起動

#### API Gateway Service
```bash
cd api_gateway
pip install -r requirements.txt
python run.py
```

#### Financial Data Service
```bash
cd financial_data
pip install -r requirements.txt
python run.py
```

## 環境変数

### API Gateway Service
- `ENVIRONMENT`: 実行環境 (development/production/testing)
- `HOST`: バインドホスト (デフォルト: 0.0.0.0)
- `PORT`: ポート番号 (デフォルト: 8000)
- `FINANCIAL_DATA_INTERNAL_URL`: Financial Data Service URL
- `CORS_ORIGINS`: CORS許可オリジン

### Financial Data Service
- `ENVIRONMENT`: 実行環境 (development/production/testing)
- `HOST`: バインドホスト (デフォルト: 0.0.0.0)
- `PORT`: ポート番号 (デフォルト: 8001)
- `YAHOO_TIMEOUT`: Yahoo Finance APIタイムアウト (秒)
- `MAX_CONCURRENT_TASKS`: 最大同時実行タスク数
- `RATE_LIMITING_ENABLED`: レート制限有効化

## ヘルスチェック

各サービスの稼働状況を確認できます：

```bash
# API Gateway
curl http://localhost:8000/health

# Financial Data Service
curl http://localhost:8001/internal/health
```

## API使用例

### 株価データ取得

```bash
# API Gateway経由でデータ取得を開始
curl -X POST http://localhost:8000/api/fetch-stock-data \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "period": "1mo"
  }'

# レスポンス例
{
  "success": true,
  "data": {
    "status": "started",
    "fetch_id": "uuid-here",
    "symbol": "AAPL",
    "period": "1mo",
    "estimated_records": 22,
    "processing_time_estimate": 1100
  }
}
```

### タスク状況確認

```bash
# Financial Data Service に直接問い合わせ
curl http://localhost:8001/internal/task/{fetch_id}/status

# レスポンス例（進行中）
{
  "success": true,
  "data": {
    "fetch_id": "uuid-here",
    "symbol": "AAPL",
    "status": "running",
    "progress": {
      "current": 75,
      "total": 100,
      "percentage": 75
    },
    "current_status": "データを処理しています..."
  }
}
```

## ログ

各サービスのログは以下の場所に出力されます：
- `logs/api_gateway.log`
- `logs/financial_data.log`

## 開発時の注意事項

1. **ポート競合**: 各サービスが異なるポートを使用していることを確認
2. **依存関係**: API Gateway は Financial Data Service に依存
3. **環境設定**: 開発環境では `.env` ファイルで環境変数を管理可能
4. **ヘルスチェック**: サービス間通信前にヘルスチェックを実行

## 次のステップ

1. Data Management Service の実装
2. Notification Service の実装
3. 認証・認可機能の追加
4. モニタリング・ログ集約の設定
5. CI/CD パイプラインの構築