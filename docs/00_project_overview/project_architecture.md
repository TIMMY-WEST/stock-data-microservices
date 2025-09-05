# 株価データ取得システム - プロジェクト全体アーキテクチャ

## 1. プロジェクト概要

### 1.1 目的
Yahoo Finance（yfinance）から日本企業の株価データを取得し、PostgreSQLデータベースに格納するWebアプリケーション

### 1.2 設計理念
- **段階的拡張**: MVP → マイクロサービス化の段階的アプローチ
- **マイクロサービス準備**: 将来の分離を考慮した内部設計
- **実用性重視**: 過度な設計よりも動作するものを優先

## 2. アーキテクチャ進化計画

### 2.1 Phase 1: MVP（現在の実装）
```
┌─────────────────────────────────────┐
│            Web Browser              │
│        (Alpine.js + Tailwind)      │
└─────────────────────────────────────┘
                  │ HTTP
                  ▼
┌─────────────────────────────────────┐
│             Flask App               │
│           (Port: 8000)              │
│                                     │
│  ┌─── Frontend Serving ───────────┐ │
│  │  • HTML/CSS/JS                 │ │
│  │  • Static Files                │ │
│  └───────────────────────────────── │ │
│                                     │
│  ┌─── API Endpoints ─────────────┐  │
│  │  • /api/fetch-data            │  │
│  │  • /api/stocks                │  │
│  │  • /api/progress              │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌─── Business Logic ──────────────┐ │
│  │  • Yahoo Finance 連携          │ │
│  │  • データ処理                   │ │
│  │  • プログレス管理               │ │
│  └────────────────────────────────┘ │
└─────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│            PostgreSQL               │
│           (Port: 5432)              │
└─────────────────────────────────────┘
```

### 2.2 Phase 3: マイクロサービス（将来の目標）
```
┌─────────────────┐
│   Frontend      │ Alpine.js + Tailwind CSS
└─────────────────┘
         │
┌─────────────────┐
│  API Gateway    │ Port: 8000
│  (Flask)        │ 統一エントリーポイント
└─────────────────┘
         │
    ┌────┼────┬────────────┬──────────────┐
    │         │            │              │
┌───▼───┐ ┌───▼──────┐ ┌───▼────────┐ ┌───▼──────────┐
│Financial│ │Data Mgmt │ │File Process│ │Notification  │
│Data Svc │ │Service   │ │Service     │ │Service       │
│Port:8001│ │Port:8002 │ │Port:8003   │ │Port:8004     │
└─────────┘ └──────────┘ └────────────┘ └──────────────┘
     │           │
     └───────┬───┘
┌────────────▼────────────┐
│      PostgreSQL         │
│      Database           │
└─────────────────────────┘
```

## 3. 技術スタック

### 3.1 現在のMVP技術スタック
- **フロントエンド**: Alpine.js + Tailwind CSS (CDN)
- **バックエンド**: Flask 3.0+
- **データベース**: PostgreSQL + SQLAlchemy
- **外部API**: Yahoo Finance (yfinance)
- **Background Tasks**: 簡易スレッドプール

### 3.2 将来のマイクロサービス技術スタック
- **フロントエンド**: Alpine.js + Tailwind CSS + Headless UI
- **API Gateway**: Python Flask
- **マイクロサービス**: Python FastAPI
- **データベース**: PostgreSQL
- **メッセージング**: Redis (サービス間通信)
- **外部API**: Yahoo Finance (yfinance ライブラリ)

## 4. マイクロサービス分離計画

### 4.1 将来のサービス構成

#### 4.1.1 API Gateway (Port: 8000)
**役割**: フロントエンドからの全リクエストを受け、適切なサービスにルーティング
**現在の対応**: `routes/api.py` がこの役割を担当

#### 4.1.2 Financial Data Service (Port: 8001)
**役割**: Yahoo Finance APIからのデータ取得専用
**現在の対応**: `services/yahoo_finance.py` がこの機能を実装

#### 4.1.3 Data Management Service (Port: 8002)
**役割**: データベース操作・データ管理専用
**現在の対応**: `services/database.py` + `models/` がこの機能を実装

#### 4.1.4 File Processing Service (Port: 8003)
**役割**: Excelファイル処理・バッチ処理
**現在の対応**: 将来実装予定

#### 4.1.5 Notification Service (Port: 8004)
**役割**: プログレス管理・リアルタイム通知
**現在の対応**: `services/progress.py` がこの機能を実装

### 4.2 現在のMVP実装構造（分離準備済み）

```
app/
├── __init__.py
├── routes/
│   ├── __init__.py
│   ├── main.py          # フロントエンド配信
│   └── api.py           # API エンドポイント (→ API Gateway)
├── services/            # 将来のマイクロサービス候補
│   ├── __init__.py
│   ├── yahoo_finance.py # → Financial Data Service
│   ├── database.py      # → Data Management Service
│   └── progress.py      # → Notification Service
├── models/
│   ├── __init__.py
│   └── stock.py         # SQLAlchemy モデル
├── static/              # フロントエンド静的ファイル
│   ├── css/
│   ├── js/
│   └── images/
└── templates/
    └── index.html       # SPA エントリーポイント
```

#### MVP技術スタック
- **Framework**: Flask 3.0+
- **Database**: PostgreSQL + SQLAlchemy
- **Frontend**: Alpine.js + Tailwind CSS (CDN)
- **External API**: Yahoo Finance (yfinance)
- **Background Tasks**: 簡易スレッドプール

#### 将来移行への準備
各 `services/` モジュールは統一インターフェースで実装し、設定による内部呼び出し/HTTP呼び出しの切り替えに対応：

```python
# 将来の移行準備
class BaseService(ABC):
    @abstractmethod
    async def handle_request(self, endpoint: str, method: str, data: dict):
        pass

# 設定による切り替え
class DevelopmentConfig:
    FINANCIAL_DATA_SERVICE_URL = 'internal'  # MVP時
    
class ProductionConfig:
    FINANCIAL_DATA_SERVICE_URL = 'http://financial-data:8001'  # マイクロサービス時
```

## 5. 段階的移行計画

### Phase 1: MVP (現在)
- 単一 Flask アプリ
- PostgreSQL のみ
- 基本機能実装

### Phase 2: 機能拡張  
- Redis 追加 (キャッシュ・タスクキュー)
- Excel ファイル処理機能
- プログレス表示強化

### Phase 3: マイクロサービス分離
- services/ フォルダを独立サービス化
- Docker コンテナ化  
- API Gateway 独立

### Phase 4: スケーリング対応
- ロードバランサー導入
- 監視ツール導入 (Prometheus/Grafana)
- 高可用性対応

## 6. 技術仕様概要

詳細な技術仕様については以下のドキュメントを参照：

- **[データベース設計](../02_architecture/database_design.md)** - DB スキーマ・インデックス戦略
- **[API仕様書](../02_architecture/api_specification.md)** - MVP版APIエンドポイント
- **[各マイクロサービス仕様](../03_microservices/)** - 将来のサービス分離設計

### 6.1 セキュリティ要件
- **MVP**: 基本的な入力検証・CORS設定
- **将来**: JWT認証・Rate Limiting・HTTPS対応

### 6.2 監視・運用
- **MVP**: 基本ログ・ヘルスチェック
- **将来**: Prometheus/Grafana・ELK Stack

### 6.3 デプロイメント
- **MVP**: Python仮想環境・ローカル開発
- **将来**: Docker・Kubernetes・CI/CD

## 7. MVP品質要件

- **動作性**: 基本機能が確実に動作すること
- **保守性**: コードが理解しやすく修正しやすいこと  
- **拡張性**: 将来の機能追加が容易であること
- **性能**: 基本的な応答性（レスポンス時間 < 5秒）

---

## まとめ

このプロジェクトアーキテクチャでは：

### ✅ **MVP優先アプローチ**
- 動作するものを素早く構築
- 段階的な機能追加
- 将来の拡張を考慮した内部設計

### 🚀 **マイクロサービス移行準備**
- サービス境界の明確化
- 疎結合な内部構造
- 独立デプロイ可能な設計

### 📈 **持続的な進化**
- 技術要件の変化に対応
- スケーラビリティの確保
- 保守性の維持

この設計により、**現在のニーズに対応**しつつ、**将来の成長**にも対応可能なシステムを構築できます。