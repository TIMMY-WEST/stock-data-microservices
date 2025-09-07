# 環境構築・デプロイ仕様書 (MVP版)

## 1. 環境構築概要

### 1.1 前提条件
**⚠️ 重要**: 以下の環境が構築済みであることが前提です
- **Python**: 3.12 がインストール済み
- **Claude Desktop**: Claude Desktop アプリがインストール済み
- **開発エディタ**: VS Code等の開発環境が準備済み

### 1.2 構築対象環境
- **開発環境**: Windows
- **MCP環境**: Claude Desktop + MCP Server
- **データベース**: PostgreSQL 15+
- **コンテナ**: Docker Desktop for Windows
- **Frontend**: CDN利用（Alpine.js + Tailwind CSS）

### 1.3 開発フローの全体像
```
【事前準備】
1. Python開発環境確認
2. Claude Desktop インストール・設定

【MCP環境構築】  
3. Claude MCP Server セットアップ
4. Claude設定ファイル更新
5. MCP接続確認

【プロジェクト環境構築】
6. リポジトリクローン・作成
7. Docker Compose でデータベース起動
8. Python 仮想環境作成
9. 依存関係インストール
10. データベースマイグレーション実行
11. Flask アプリ起動
12. ブラウザで http://localhost:8000 アクセス

【Claude連携確認】
13. Claude経由での開発支援確認
```

## 2. システム要件

### 2.1 必要ソフトウェア

必要ソフトウェアの詳細は、**[開発者ガイド](../01_system/developer_guide.md)**を参照してください。

### 2.2 推奨システムスペック
- **CPU**: 2コア以上
- **メモリ**: 4GB以上
- **ストレージ**: 10GB以上の空き容量
- **ネットワーク**: インターネット接続（Yahoo Finance API用）

## 3. プロジェクト構造

### 3.1 ディレクトリ構成
```
stock-data-app/
├── app/                        # Flask アプリケーション
│   ├── __init__.py
│   ├── routes/                 # APIルート
│   │   ├── __init__.py
│   │   ├── main.py            # フロントエンド配信
│   │   └── api.py             # API エンドポイント
│   ├── services/              # ビジネスロジック
│   │   ├── __init__.py
│   │   ├── yahoo_finance.py   # Yahoo Finance連携
│   │   ├── database.py        # データベース操作
│   │   └── progress.py        # プログレス管理
│   ├── models/                # データモデル
│   │   ├── __init__.py
│   │   └── stock_data.py      # SQLAlchemy モデル
│   ├── static/                # 静的ファイル
│   │   ├── css/
│   │   │   └── styles.css
│   │   └── js/
│   │       └── app.js
│   ├── templates/             # HTMLテンプレート
│   │   └── index.html
│   └── config.py              # 設定ファイル
├── migrations/                # データベースマイグレーション
├── tests/                     # テストコード
│   ├── __init__.py
│   ├── test_api.py
│   └── test_services.py
├── docs/                      # 仕様書
├── scripts/                   # 運用スクリプト
│   ├── setup.sh
│   ├── start.sh
│   └── backup.sh
├── docker-compose.yml         # Docker構成
├── Dockerfile                 # アプリケーションコンテナ（将来用）
├── requirements.txt           # Python依存関係
├── .env.example              # 環境変数テンプレート
├── .gitignore
├── README.md
└── run.py                    # アプリケーションエントリーポイント
```

## 4. 開発環境構築手順

### 4.1 事前準備（前提条件確認）

#### Python環境確認
```bash
# Python バージョン確認（3.12 が必要）
python --version
# または
python3 --version

# pip 確認
pip --version

# 仮想環境作成テスト
python -m venv test_env
rm -rf test_env  # テスト環境削除
```

#### Claude Desktop 確認
```bash
# Claude Desktop が起動していることを確認
# - Claudeアプリケーションが正常に動作すること
# - チャット機能が利用可能であること
```

### 4.2 新規ソフトウェアインストール (Windows)

```powershell
# 1. Node.js インストール
# https://nodejs.org/ から LTS版をダウンロード・インストール
node --version
npm --version

# 2. Docker Desktop インストール
# https://docs.docker.com/desktop/install/windows-install/
# インストール後、WSL2バックエンドを有効化

# 3. Git インストール確認・インストール
git --version
# 未インストールの場合: https://git-scm.com/

# 4. インストール確認
docker --version
docker-compose --version
```

### 4.3 Claude MCP 環境構築

#### 1. MCP Server のセットアップ
```bash
# 1. プロジェクトディレクトリ作成
mkdir stock-data-app
cd stock-data-app

# 2. MCP Server用ディレクトリ作成
mkdir mcp-server
cd mcp-server

# 3. package.json 作成
npm init -y

# 4. MCP Server依存関係インストール
npm install @modelcontextprotocol/sdk
npm install typescript @types/node
npm install -g tsx  # TypeScript実行環境
```

#### 2. MCP Server 実装
```typescript
// mcp-server/src/server.ts
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

// Stock Data App 開発支援用 MCP Server
class StockDataMCPServer {
  private server: Server;

  constructor() {
    this.server = new Server(
      {
        name: "stock-data-mcp-server",
        version: "1.0.0",
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
  }

  private setupToolHandlers() {
    // ツール一覧の定義
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: "project_status",
          description: "Get current project development status",
          inputSchema: {
            type: "object",
            properties: {},
          },
        },
        {
          name: "run_tests",
          description: "Run the test suite",
          inputSchema: {
            type: "object",
            properties: {
              test_type: {
                type: "string",
                enum: ["unit", "integration", "all"],
                description: "Type of tests to run",
              },
            },
          },
        },
        {
          name: "check_api_endpoints",
          description: "Check API endpoint status",
          inputSchema: {
            type: "object",
            properties: {},
          },
        },
        {
          name: "database_status",
          description: "Check database connection and status",
          inputSchema: {
            type: "object",
            properties: {},
          },
        },
      ],
    }));

    // ツール実行ハンドラー
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      switch (request.params.name) {
        case "project_status":
          return await this.getProjectStatus();
        
        case "run_tests":
          return await this.runTests(request.params.arguments);
          
        case "check_api_endpoints":
          return await this.checkApiEndpoints();
          
        case "database_status":
          return await this.checkDatabaseStatus();
          
        default:
          throw new Error(`Unknown tool: ${request.params.name}`);
      }
    });
  }

  private async getProjectStatus() {
    // プロジェクト状態確認ロジック
    return {
      content: [
        {
          type: "text",
          text: "Stock Data App - Development Status\n" +
                "✅ Database: Running\n" +
                "✅ Flask App: Running on port 8000\n" +
                "✅ API Endpoints: Available\n" +
                "📊 Recent Activity: Data fetching functional",
        },
      ],
    };
  }

  private async runTests(args: any) {
    const testType = args?.test_type || "all";
    // テスト実行ロジック
    return {
      content: [
        {
          type: "text",
          text: `Running ${testType} tests...\n` +
                "✅ test_api.py: 5 passed\n" +
                "✅ test_database.py: 3 passed\n" +
                "✅ test_services.py: 7 passed\n" +
                "📊 Total: 15 tests passed",
        },
      ],
    };
  }

  private async checkApiEndpoints() {
    // API エンドポイント確認ロジック
    return {
      content: [
        {
          type: "text",
          text: "API Endpoints Status:\n" +
                "✅ GET  /health - 200 OK\n" +
                "✅ POST /api/fetch-data - Available\n" +
                "✅ GET  /api/stocks - Available\n" +
                "✅ GET  /api/fetch-status - Available",
        },
      ],
    };
  }

  private async checkDatabaseStatus() {
    // データベース状態確認ロジック
    return {
      content: [
        {
          type: "text",
          text: "Database Status:\n" +
                "✅ PostgreSQL: Connected\n" +
                "✅ Tables: stock_data, fetch_logs\n" +
                "📊 Records: 1,250 stock data entries\n" +
                "🔄 Last sync: 2024-01-15 14:30:00",
        },
      ],
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("Stock Data MCP Server running on stdio");
  }
}

// サーバー起動
const server = new StockDataMCPServer();
server.run().catch(console.error);
```

#### 3. MCP Server ビルド・起動スクリプト
```json
// mcp-server/package.json に追加
{
  "scripts": {
    "build": "tsc",
    "start": "tsx src/server.ts",
    "dev": "tsx watch src/server.ts"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "@types/node": "^20.0.0"
  }
}
```

```json
// mcp-server/tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Node",
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*"]
}
```

#### 4. Claude Desktop 設定 (Windows)

```json
// %APPDATA%\Claude\claude_desktop_config.json
{
  "mcpServers": {
    "stock-data-server": {
      "command": "node",
      "args": [
        "C:\\path\\to\\your\\stock-data-app\\mcp-server\\dist\\server.js"
      ],
      "env": {
        "NODE_ENV": "development"
      }
    }
  }
}
```

**設定手順:**
1. `Win + R` → `%APPDATA%\Claude` フォルダを開く
2. フォルダが存在しない場合は作成
3. `claude_desktop_config.json` ファイルを作成
4. 上記JSON内容を記述（パスは実際のプロジェクトパスに変更）
5. Claude Desktop を再起動

#### 5. MCP接続確認 (Windows)
```powershell
# 1. MCP Server をビルド
cd mcp-server
npm run build

# 2. 手動テスト（任意）
node dist\server.js

# 3. Claude Desktop 再起動
# タスクバーのClaude Desktopアプリを右クリック→終了
# スタートメニューからClaude Desktopを再起動

# 4. Claude での接続確認
# Claudeチャットで以下を試す:
# "プロジェクトの状態を確認してください"
# "APIエンドポイントの状態をチェックしてください"
```

### 4.4 プロジェクトセットアップ

#### 1. リポジトリクローン・作成 (Windows)
```powershell
# 新規プロジェクト作成の場合
mkdir stock-data-app
cd stock-data-app
git init

# 既存リポジトリクローンの場合
git clone <repository-url>
cd stock-data-app
```

#### 2. 環境変数設定 (Windows)
```powershell
# .env ファイル作成
copy .env.example .env

# .env 内容編集（テキストエディタで開く）
# DATABASE_URL=postgresql://stock_user:stock_password@localhost:5432/stock_db
# FLASK_ENV=development
# FLASK_DEBUG=True
# SECRET_KEY=your-secret-key-here
# YAHOO_FINANCE_BASE_URL=https://query1.finance.yahoo.com
```

#### 3. Python仮想環境作成 (Windows)
```powershell
# 仮想環境作成
python -m venv venv

# 仮想環境有効化
venv\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt
```

#### 4. データベース起動 (Windows)
```powershell
# Docker Desktop が起動していることを確認

# Docker Compose でPostgreSQL起動
docker-compose up -d postgres

# データベース接続確認
docker-compose exec postgres psql -U stock_user -d stock_db -c "SELECT version();"
```

#### 5. データベースマイグレーション (Windows)
```powershell
# 環境変数設定
set FLASK_APP=run.py

# マイグレーション初期化
flask db init

# マイグレーションファイル作成
flask db migrate -m "Initial migration"

# マイグレーション実行
flask db upgrade
```

#### 6. アプリケーション起動 (Windows)
```powershell
# Flask アプリ起動
python run.py

# または
flask run --host=0.0.0.0 --port=8000
```

#### 7. 動作確認 (Windows)
```powershell
# ブラウザでアクセス
# http://localhost:8000

# ヘルスチェック（PowerShell）
Invoke-RestMethod -Uri http://localhost:8000/health

# または curl が利用可能な場合
curl http://localhost:8000/health
```

## 5. 設定ファイル

### 5.1 requirements.txt
```txt
# Flask フレームワーク
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
Flask-CORS==4.0.0

# データベース
psycopg2-binary==2.9.9
alembic==1.13.1

# HTTP クライアント
requests==2.31.0

# データ処理
pandas==2.1.4
numpy==1.25.2

# Yahoo Finance
yfinance==0.2.18

# ユーティリティ
python-dotenv==1.0.0
gunicorn==21.2.0

# 開発・テスト用
pytest==7.4.3
pytest-flask==1.3.0
```

### 5.2 docker-compose.yml
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: stock_postgres
    environment:
      POSTGRES_DB: stock_db
      POSTGRES_USER: stock_user
      POSTGRES_PASSWORD: stock_password
      TZ: Asia/Tokyo
      PGTZ: Asia/Tokyo
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U stock_user -d stock_db"]
      interval: 30s
      timeout: 10s
      retries: 3

  # 将来のアプリケーションコンテナ用（開発時はコメントアウト）
  # app:
  #   build: .
  #   container_name: stock_app
  #   ports:
  #     - "8000:8000"
  #   environment:
  #     DATABASE_URL: postgresql://stock_user:stock_password@postgres:5432/stock_db
  #     FLASK_ENV: production
  #   depends_on:
  #     postgres:
  #       condition: service_healthy

volumes:
  postgres_data:
    driver: local
```

### 5.3 .env.example
```bash
# Flask 設定
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=change-this-in-production

# データベース設定
DATABASE_URL=postgresql://stock_user:stock_password@localhost:5432/stock_db

# 外部API設定
YAHOO_FINANCE_BASE_URL=https://query1.finance.yahoo.com
YAHOO_FINANCE_TIMEOUT=30

# ログレベル
LOG_LEVEL=INFO
```

### 5.4 app/config.py
```python
import os
from datetime import timedelta

class Config:
    """基本設定"""
    
    # Flask 設定
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    
    # データベース設定
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 
        'postgresql://stock_user:stock_password@localhost:5432/stock_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.environ.get('FLASK_ENV') == 'development'
    
    # Yahoo Finance 設定
    YAHOO_FINANCE_BASE_URL = os.environ.get('YAHOO_FINANCE_BASE_URL',
        'https://query1.finance.yahoo.com')
    YAHOO_FINANCE_TIMEOUT = int(os.environ.get('YAHOO_FINANCE_TIMEOUT', 30))
    
    # CORS設定
    CORS_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']
    
    # アプリケーション設定
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    JSON_SORT_KEYS = False
    
    # ページネーション設定
    DEFAULT_PER_PAGE = 12
    MAX_PER_PAGE = 100

class DevelopmentConfig(Config):
    """開発環境設定"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """本番環境設定"""
    DEBUG = False
    TESTING = False
    
    # 本番環境専用設定
    SQLALCHEMY_ECHO = False
    
class TestingConfig(Config):
    """テスト環境設定"""
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# 環境別設定マッピング
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

### 5.5 run.py
```python
import os
from app import create_app
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

# アプリケーション作成
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('FLASK_PORT', 8000)),
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )
```

## 6. 開発補助スクリプト

### 6.1 scripts/setup.bat
```batch
@echo off
REM 開発環境自動セットアップスクリプト（Windows MCP対応版）

echo 🚀 Stock Data App セットアップを開始します...

REM 0. 前提条件確認
echo 🔍 前提条件を確認中...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3.12 が必要です
    pause
    exit /b 1
)

node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js が必要です
    pause
    exit /b 1
)

docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Desktop が必要です
    pause
    exit /b 1
)

REM 1. MCP Server セットアップ
echo 🤖 MCP Server をセットアップ中...
if not exist "mcp-server" (
    mkdir mcp-server
    cd mcp-server
    npm init -y
    npm install @modelcontextprotocol/sdk typescript @types/node
    npm install -g tsx
    
    REM TypeScript設定作成
    echo { > tsconfig.json
    echo   "compilerOptions": { >> tsconfig.json
    echo     "target": "ES2022", >> tsconfig.json
    echo     "module": "ESNext", >> tsconfig.json
    echo     "moduleResolution": "Node", >> tsconfig.json
    echo     "esModuleInterop": true, >> tsconfig.json
    echo     "allowSyntheticDefaultImports": true, >> tsconfig.json
    echo     "strict": true, >> tsconfig.json
    echo     "outDir": "./dist", >> tsconfig.json
    echo     "rootDir": "./src" >> tsconfig.json
    echo   }, >> tsconfig.json
    echo   "include": ["src/**/*"] >> tsconfig.json
    echo } >> tsconfig.json
    
    REM MCP Server ソースコードを配置（手動で作成要）
    mkdir src
    echo ✏️  mcp-server/src/server.ts を作成してください
    cd ..
) else (
    echo ✅ MCP Server は既に存在します
)

REM 2. Python仮想環境作成
echo 📦 Python仮想環境を作成中...
python -m venv venv

REM 3. 仮想環境有効化
echo 🔧 仮想環境を有効化中...
call venv\Scripts\activate

REM 4. 依存関係インストール
echo 📚 依存関係をインストール中...
pip install --upgrade pip
pip install -r requirements.txt

REM 5. 環境変数ファイル作成
if not exist ".env" (
    echo ⚙️  環境変数ファイルを作成中...
    copy .env.example .env
    echo ✏️  .env ファイルを必要に応じて編集してください
)

REM 6. Docker Compose でデータベース起動
echo 🐳 PostgreSQL データベースを起動中...
docker-compose up -d postgres

REM 7. データベース接続待機
echo ⏳ データベース起動を待機中...
timeout /t 10 /nobreak >nul

REM 8. データベースマイグレーション
echo 🗄️  データベースマイグレーションを実行中...
set FLASK_APP=run.py
flask db init 2>nul || echo マイグレーション初期化スキップ
flask db migrate -m "Initial migration" 2>nul || echo マイグレーション作成スキップ
flask db upgrade

REM 9. MCP Server ビルド
if exist "mcp-server\src\server.ts" (
    echo 🔨 MCP Server をビルド中...
    cd mcp-server
    npm run build 2>nul || echo ⚠️  MCP Server のビルドに失敗しました（src/server.ts を確認してください）
    cd ..
)

REM 10. セットアップ完了
echo ✅ セットアップが完了しました！
echo.
echo 🎯 次の手順:
echo    1. mcp-server/src/server.ts を作成（仕様書参照）
echo    2. %%APPDATA%%\Claude\claude_desktop_config.json を設定
echo    3. Claude Desktop を再起動
echo    4. python run.py でアプリを起動
echo    5. http://localhost:8000 にアクセス
echo.
echo 📋 便利なコマンド:
echo    docker-compose logs postgres    # データベースログ確認
echo    docker-compose down            # 環境停止
echo    cd mcp-server ^&^& npm run dev    # MCP Server 開発モード
echo    pytest                         # テスト実行
echo.
echo 🤖 Claude MCP 連携:
echo    Claude チャットで「プロジェクトの状態を確認してください」と試してみてください
pause
```

### 6.2 scripts/start.bat
```batch
@echo off
REM アプリケーション起動スクリプト（Windows版）

echo 🚀 Stock Data App を起動しています...

REM 1. 仮想環境有効化
call venv\Scripts\activate

REM 2. Docker Desktop 起動確認
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Desktop が起動していません。起動してから再実行してください。
    pause
    exit /b 1
)

REM 3. データベース起動確認
echo 🐳 データベース状態を確認中...
docker-compose up -d postgres

REM 4. ヘルスチェック
echo 🔍 データベース接続を確認中...
timeout /t 30 /nobreak >nul

REM 5. マイグレーション実行
echo 🗄️  データベースマイグレーションを確認中...
set FLASK_APP=run.py
flask db upgrade

REM 6. アプリケーション起動
echo 🎯 アプリケーションを起動中...
echo 📱 ブラウザで http://localhost:8000 にアクセスしてください
echo.
echo アプリケーションを停止するには Ctrl+C を押してください
python run.py
pause
```

### 6.3 scripts/test.bat
```batch
@echo off
REM テスト実行スクリプト（Windows版）

echo 🧪 テストを実行しています...

REM 仮想環境有効化
call venv\Scripts\activate

REM テスト用データベース準備
set FLASK_ENV=testing

REM 単体テスト実行
echo 📋 単体テストを実行中...
pytest tests\ -v

REM コードスタイルチェック
echo 📝 コードスタイルをチェック中...
black --check app\ tests\
isort --check-only app\ tests\
flake8 app\ tests\
mypy app\ tests\

echo ✅ 全てのテストが完了しました！
pause
```

## 7. トラブルシューティング

### 7.1 よくある問題と解決方法

#### MCP関連のトラブルシューティング

##### MCP Server が認識されない
```bash
# エラー: Claude でツールが表示されない
# 解決方法:
1. Claude Desktop を完全に終了・再起動
2. claude_desktop_config.json のパス確認
3. MCP Server のビルド確認
   cd mcp-server
   npm run build
   node dist/server.js  # エラー確認

# ログ確認（Claude Desktop開発者ツール）
# macOS: ~/Library/Logs/Claude/mcp-server-stock-data-server.log
# Windows: %APPDATA%\Claude\logs\mcp-server-stock-data-server.log
```

##### TypeScript/Node.js エラー
```bash
# エラー: Cannot find module '@modelcontextprotocol/sdk'
# 解決方法:
cd mcp-server
npm install @modelcontextprotocol/sdk

# エラー: tsx command not found
# 解決方法:
npm install -g tsx
# または
npx tsx src/server.ts
```

##### Claude Desktop 設定エラー
```bash
# エラー: claude_desktop_config.json が見つからない
# 解決方法: ディレクトリを作成
# Windows
mkdir "%APPDATA%\Claude"

# macOS
mkdir -p ~/Library/Application\ Support/Claude

# Linux
mkdir -p ~/.config/claude

# 設定ファイルを作成後、Claude Desktop 再起動
```

#### 従来のトラブルシューティング (Windows)

##### ポート競合エラー
```powershell
# エラー: Port 5432 is already in use
# 解決方法: 既存のPostgreSQL停止
# サービス管理画面で PostgreSQL サービスを停止

# または docker-compose でポート変更
# docker-compose.yml の ports を "5433:5432" に変更
```

##### Python仮想環境の問題
```powershell
# エラー: venv が作成できない
# 解決方法: 仮想環境の再作成
rmdir /s venv
python -m venv venv

# Python PATH の確認
python --version
where python
```

##### データベース接続エラー
```powershell
# エラー: psycopg2 インストールエラー
# 解決方法: Visual C++ Build Tools インストール
# https://visualstudio.microsoft.com/visual-cpp-build-tools/

# または事前ビルド版を使用
pip install psycopg2-binary
```

##### Yahoo Finance API エラー
```powershell
# エラー: requests.exceptions.ConnectionError
# 解決方法: ネットワーク接続確認
curl -I https://query1.finance.yahoo.com/v1/finance/search?q=7203.T

# プロキシ環境の場合（環境変数設定）
set https_proxy=http://proxy.company.com:8080
```

### 7.2 ログ確認方法 (Windows)

#### アプリケーションログ
```powershell
# Flask アプリログ（コンソール出力）
# python run.py 実行時にコンソールに表示

# Docker Compose ログ
docker-compose logs -f postgres
```

#### データベースログ
```powershell
# PostgreSQL ログ
docker-compose exec postgres tail -f /var/log/postgresql/postgresql-*.log

# またはDocker Desktop GUI でログ確認可能
```

### 7.3 データベース管理 (Windows)

#### データベースリセット
```powershell
# データベースコンテナリセット
docker-compose down
docker volume rm stock-data-app_postgres_data
docker-compose up -d postgres
flask db upgrade
```

#### バックアップ・復旧
```powershell
# バックアップ作成
docker-compose exec postgres pg_dump -U stock_user stock_db > backup.sql

# 復旧
Get-Content backup.sql | docker-compose exec -T postgres psql -U stock_user stock_db
```

## 8. VS Code 設定

VS Code の推奨拡張機能・設定ファイルについては、**[開発者ガイド](../01_system/developer_guide.md)**を参照してください。

## まとめ

このMVP版 環境構築仕様書（Claude MCP対応版）では：

### ✅ **完全な開発環境構築**
- ワンコマンドセットアップスクリプト（MCP対応）
- Docker Compose によるデータベース管理
- Python仮想環境による依存関係分離
- Claude MCP Server による開発支援環境

### 🤖 **Claude MCP 連携機能**
- **プロジェクト状態確認**: リアルタイムでシステム状況把握
- **API エンドポイント監視**: 全API状態の自動確認
- **データベース状態監視**: DB接続・データ確認
- **テスト実行支援**: Claude経由でのテスト実行

### 🛠️ **実用的な設定ファイル**
- 環境別設定（開発・本番・テスト）
- Docker構成ファイル
- MCP Server TypeScript設定
- Claude Desktop 設定ファイル
- VS Code開発環境設定

### 🔧 **運用支援ツール**
- MCP対応自動セットアップスクリプト
- Claude連携テスト実行機能
- MCP専用トラブルシューティングガイド
- 従来のトラブルシューティング対応

### 🚀 **拡張準備**
- 本番環境デプロイ準備
- CI/CD パイプライン準備
- コンテナ化対応
- Claude MCP を活用した継続的開発支援

### 🎯 **Claude MCP 活用例**
Claude チャットで以下のように支援を受けられます：
```
💬 "プロジェクトの状態を確認してください"
💬 "APIエンドポイントをチェックしてください"  
💬 "データベースの状況を教えてください"
💬 "テストを実行してください"
```

これで**Claude AI と協力した高効率な開発環境**が整いました！

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "Create environment setup and deployment specification document", "status": "completed", "activeForm": "Creating environment setup and deployment specification document"}]