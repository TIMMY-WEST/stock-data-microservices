# Stock Data Microservices

株価データの収集、処理、提供を行うマイクロサービスアーキテクチャベースのシステムです。

## Services

- リアルタイム株価データ取得サービス
- データ解析・計算処理サービス
- クライアントアプリケーション向けAPIサービス
- データ永続化サービス

## Quick Start

```bash
# リポジトリをクローン
git clone https://github.com/TIMMY-WEST/stock-data-microservices.git
cd stock-data-microservices

# Python環境のセットアップ
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Pre-commitのセットアップ（開発者向け）
pre-commit install

# アプリケーションの起動
python run.py
```

## 開発環境セットアップ

### Pre-commit設定

このプロジェクトでは、コミット時に自動的にコードフォーマットと静的解析を実行するため、pre-commitを使用しています。

```bash
# Pre-commitのインストール
pip install pre-commit

# Pre-commitフックの有効化
pre-commit install

# 全ファイルに対してpre-commitを実行（初回セットアップ時）
pre-commit run --all-files
```

#### Pre-commitで実行される内容

- **Black**: Pythonコードの自動フォーマット
- **isort**: import文の並び替え
- **flake8**: PEP8準拠チェック
- **mypy**: 型チェック
- **一般的なチェック**: 末尾空白除去、ファイル終端修正、YAMLチェックなど

### テスト実行

```bash
# 単体テスト
python -m pytest tests/unit/ -v

# 統合テスト
python -m pytest tests/integration/ -v

# 全テスト（カバレッジ付き）
python -m pytest tests/ -v --cov=app --cov-report=html
```

## API Endpoints

- `GET /api/stocks/{symbol}` - 現在の株価を取得
- `GET /api/stocks/{symbol}/history` - 過去の株価データを取得
- `GET /api/stocks/trending` - トレンド株を取得

## Technologies

- Python/Flask - APIサービス
- PostgreSQL - データベース
- Redis - キャッシュ・タスクキュー
- Docker - コンテナ化
- GitHub Actions - CI/CD
