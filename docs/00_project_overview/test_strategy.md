# 株価データ取得・管理システム テスト戦略

## 戦略の核心

この文書では、株価データ取得・管理システムに対する**包括的なテスト戦略**を定義します。

### 戦略の基本方針
1. **リスクベースアプローチ**: 高リスク機能（API連携・データ整合性）を重点的にテスト
2. **段階的品質向上**: MVP → 機能拡張 → 完全自動化の3段階で品質を段階的に向上
3. **継続的フィードバック**: CI/CDパイプラインによる即座の品質フィードバック
4. **コスト効率性**: テストピラミッドに基づく効率的なテスト配分（Unit 70% / Integration 20% / E2E 10%）

## 1. テスト戦略概要

### 1.1 戦略的テスト方針
- **品質第一**: バグの早期発見・修正による品質確保
- **自動化重視**: CI/CDパイプラインでの自動テスト実行
- **段階的拡張**: MVPから段階的にテスト範囲を拡大
- **実用性重視**: 実際の運用で価値のあるテストに集中

### 1.2 戦略の実現手段
- **テストピラミッド構造**: 効率的なテスト配分により開発速度と品質を両立
- **マイクロサービス対応**: 各サービスの独立性を保ちながら統合品質を保証
- **アジャイル連動**: Sprint進行に合わせた段階的テスト拡張
- **品質ゲート**: ブランチ戦略と連動した自動品質チェック

### 1.3 テストレベル
- **単体テスト (Unit Tests)**: 個別モジュール・関数レベル
- **統合テスト (Integration Tests)**: サービス間連携・DB接続
- **E2Eテスト (End-to-End Tests)**: ユーザーシナリオ全体
- **パフォーマンステスト**: 負荷・応答時間検証

## 2. テストピラミッド (マイクロサービス版)

```
              ┌────────────────┐
              │   E2E Tests    │  ← 少数・重要シナリオのみ
              │   (Playwright) │    5-10 tests
              └────────────────┘
            ┌──────────────────────┐
            │   Integration Tests  │  ← サービス間通信
            │   (TestContainers)   │    20-30 tests
            └──────────────────────┘
          ┌──────────────────────────┐
          │     Unit Tests           │  ← 各サービス内のロジック  
          │     (pytest)             │    100+ tests
          └──────────────────────────┘
```

### 2.1 戦略的テスト配分の根拠

#### なぜこの配分なのか？
- **Unit Tests (70%)**: 最も高速で信頼性が高く、開発者の即座のフィードバックを実現
- **Integration Tests (20%)**: マイクロサービス間の結合部分で最も多くのバグが発生するため重点配分
- **E2E Tests (10%)**: 実行時間が長く不安定になりがちなため、重要シナリオに限定

#### この配分がもたらす効果
- **開発速度向上**: 高速なUnit Testにより即座のフィードバック
- **品質保証**: Integration Testによりサービス間連携の確実な動作保証
- **ユーザー体験保証**: E2E Testにより重要な業務フローの確実な動作保証

### 2.2 テスト配分比率
- **Unit Tests**: 70% (高速・大量実行)
- **Integration Tests**: 20% (サービス連携確認)
- **E2E Tests**: 10% (重要シナリオのみ)

## 3. 戦略的リスク分析と対応

### 3.1 主要リスクと戦略的対応

#### 高リスク領域（重点テスト対象）
1. **外部API依存（Yahoo Finance）**: モック・スタブによる安定テスト + 実API統合テスト
2. **データ整合性（重複・欠損）**: 境界値・異常値・大量データテスト
3. **マイクロサービス間通信**: ネットワーク障害・タイムアウト・順序性テスト
4. **並行処理（複数リクエスト）**: 競合状態・デッドロック・リソース枯渇テスト

#### 中リスク領域（標準テスト）
- ユーザー入力検証
- データベースクエリ性能
- APIレスポンス形式

#### 低リスク領域（軽量テスト）
- 静的データ表示
- 単純な計算処理
- UI要素の基本表示

## 4. サービス別テスト方針

### 4.1 Financial Data Service
**主な責務**: Yahoo Finance APIからの株価データ取得

#### テスト観点
- **正常系**: 有効な銘柄コードでのデータ取得成功
- **異常系**: 存在しない銘柄コード、APIエラー、ネットワーク障害
- **制限系**: API制限レート、タイムアウト、大量データ処理
- **データ品質**: 取得データの形式・範囲・完整性検証

### 4.2 Data Management Service  
**主な責務**: データベース操作・データ管理

#### テスト観点
- **CRUD操作**: データの作成・読取・更新・削除
- **データ整合性**: 重複データ処理（上書き/スキップ）、トランザクション制御
- **ページネーション**: 大量データの分割取得
- **パフォーマンス**: クエリ実行時間、インデックス効果

### 4.3 API Gateway
**主な責務**: リクエストルーティング・認証・レスポンス変換

#### テスト観点
- **ルーティング**: 各エンドポイントへの正しい転送
- **入力検証**: リクエストパラメータの妥当性チェック
- **エラーハンドリング**: 下位サービスエラーの適切な変換
- **レスポンス形式**: 統一されたAPI仕様への準拠

### 4.4 Notification Service
**主な責務**: タスク進捗管理・リアルタイム通知

#### テスト観点
- **進捗管理**: タスク状態の正確な追跡・更新
- **リアルタイム性**: WebSocketによる即座な状態通知
- **並行処理**: 複数タスクの同時進行管理
- **永続化**: タスク履歴の保存・復旧

## 5. アジャイル対応テスト

### 5.1 Sprint別テスト戦略

#### Sprint 1 (MVP) - 必須テスト
**目標**: 基本機能の動作保証

**単体テスト**:
- [ ] Yahoo Finance API連携テスト
- [ ] データベース保存・取得テスト
- [ ] 銘柄コード検証テスト

**統合テスト**:
- [ ] API経由でのデータ取得→DB保存テスト
- [ ] フロントエンド→バックエンド連携テスト

**E2Eテスト**:
- [ ] 銘柄入力→データ取得→結果表示の基本フロー

#### Sprint 2以降 - 段階的テスト追加
**目標**: 機能拡張に対応したテスト拡充

**追加テスト**:
- [ ] 複数銘柄処理テスト
- [ ] エラーハンドリングテスト
- [ ] パフォーマンステスト（応答時間・同時実行）
- [ ] UI/UXテスト（ブラウザ互換性）

### 5.2 テスト自動化レベル

#### Level 1: MVP (Sprint 1)
```yaml
自動化対象:
- 単体テスト: 100% 自動化
- 統合テスト: 70% 自動化  
- E2E テスト: 50% 自動化（重要パスのみ）
```

#### Level 2: 機能拡張 (Sprint 2-3)
```yaml
自動化対象:
- 単体テスト: 100% 自動化
- 統合テスト: 90% 自動化
- E2E テスト: 80% 自動化
- パフォーマンステスト: 50% 自動化
```

#### Level 3: 完全自動化 (Sprint 4以降)
```yaml
自動化対象:
- 全テストレベル: 95%以上 自動化
- 回帰テスト: 100% 自動化
- デプロイテスト: 100% 自動化
```

## 6. CI/CD テスト自動化

### 6.1 GitHub Actions ワークフロー

CI/CDプラットフォームとして **GitHub Actions** を使用し、以下のワークフローでテストを自動化します：

#### ワークフロー構成
- **単体テスト (Unit Tests)**: 各サービス（financial-data, data-management, api-gateway, notification）について、Python 3.11/3.12環境でのpytestによるテスト実行とコードカバレッジ測定
- **統合テスト (Integration Tests)**: PostgreSQL・Redisサービスを起動し、サービス間連携のテスト実行
- **E2Eテスト (End-to-End Tests)**: Docker Composeでアプリケーション全体を起動し、Playwrightによるブラウザテスト実行
- **セキュリティテスト (Security Tests)**: Bandit・Safetyによる脆弱性スキャン実行

#### 実行順序
1. 単体テスト → 2. 統合テスト → 3. E2Eテスト
4. セキュリティテスト（並行実行）

### 6.2 テスト実行トリガー

テスト実行のトリガー・ブランチ戦略連携については、**[開発者ガイド](developer_guide.md)**を参照してください。

## 7. テストデータ管理

### 7.1 テストデータ戦略

#### 戦略の概要と目的

テストデータ戦略は、**再現可能**・**保守可能**・**効率的**なテストの実現を目指します。株価データという特性上、以下の課題を解決する必要があります：

- **外部API依存**: Yahoo Finance APIからの実データに依存せず、予測可能なテスト結果を保証
- **時系列データ**: 日付・時間に依存するデータの一貫性を保持
- **データ量**: 大量の株価データを効率的に生成・管理
- **データ品質**: 現実的でありながら、テスト目的に適したデータの提供

#### 戦略の実装方針

1. **ファクトリーパターンの採用**
   - `StockDataFactory`によりテストデータを動的生成
   - デフォルト値を設定しつつ、特定テストケースに応じたカスタマイズを可能に
   - メンテナンス性向上のため、データ生成ロジックを一元化

2. **階層化されたフィクスチャ管理**
   - セッションレベル: データベース接続・基盤設定
   - テストレベル: 各テスト用の独立したデータセット
   - 実行効率とテスト独立性の両立

3. **現実的データパターンの提供**
   - 実在銘柄コード（`7203.T`等）を使用して現実的なテスト
   - 価格・出来高の妥当な範囲設定で品質の高いテスト実行
   - 異常値・境界値パターンも網羅

#### テストデータ種類
```python
# tests/fixtures/stock_data.py
SAMPLE_STOCK_DATA = {
    "valid_symbols": ["7203.T", "6758.T", "9984.T"],
    "invalid_symbols": ["INVALID.T", "123.X", ""],
    "sample_data": {
        "7203.T": {
            "company_name": "トヨタ自動車",
            "price_range": (1400, 1600),
            "volume_range": (800000, 1200000)
        }
    }
}

# テストデータファクトリー
class StockDataFactory:
    @staticmethod
    def create_stock_data(symbol="7203.T", **kwargs):
        defaults = {
            "date": "2024-01-01",
            "open": 1500.0,
            "high": 1520.0,
            "low": 1480.0,
            "close": 1510.0,
            "volume": 1000000
        }
        defaults.update(kwargs)
        return StockData(symbol=symbol, **defaults)
```

#### データカテゴリと利用戦略

**有効データ（正常系テスト用）**:
- `valid_symbols`: 実在する日本株銘柄コードを使用
- 現実的な価格レンジと出来高で、システムの通常動作を検証

**無効データ（異常系テスト用）**:
- `invalid_symbols`: 存在しない銘柄コード、フォーマット違反パターン
- エラーハンドリング・バリデーション機能の検証

**境界値データ**:
- 価格の上下限値、出来高ゼロ、異常な値幅など
- システムの堅牢性とエッジケースの処理を検証

#### データベースフィクスチャ
```python
# tests/fixtures/database.py
@pytest.fixture(scope="session")
def test_database():
    """テスト用データベースセットアップ"""
    # テスト用DBの作成
    engine = create_engine("postgresql://test:test@localhost/test_db")
    Base.metadata.create_all(engine)
    
    yield engine
    
    # テスト後のクリーンアップ
    Base.metadata.drop_all(engine)

@pytest.fixture
def sample_stocks(test_database):
    """サンプル株価データ"""
    with Session(test_database) as session:
        stocks = [
            StockDataFactory.create_stock_data("7203.T", date="2024-01-01"),
            StockDataFactory.create_stock_data("6758.T", date="2024-01-01"),
            StockDataFactory.create_stock_data("9984.T", date="2024-01-01")
        ]
        session.add_all(stocks)
        session.commit()
        return stocks
```

#### テストデータ分離戦略

**環境別データ分離**:
- 単体テスト: インメモリデータベース（SQLite）+ モックデータ
- 統合テスト: 専用PostgreSQLインスタンス + 半実データ
- E2Eテスト: 本番相当環境 + 実データサブセット

**データ独立性の確保**:
- 各テストケースは独立したデータセットを使用
- テスト実行前後の自動クリーンアップ
- 並行テスト実行時のデータ競合防止

**データ保守性**:
- ファクトリークラスによる一元管理
- 設定ファイルでのデータパラメータ外部化
- バージョン管理下でのテストデータ変更履歴管理

## 8. パフォーマンステスト

### 8.1 負荷テスト仕様

#### テストシナリオ
```python
# tests/performance/test_load.py
import pytest
from locust import HttpUser, task, between

class StockDataUser(HttpUser):
    wait_time = between(1, 5)
    
    @task(3)
    def fetch_single_stock(self):
        """単一銘柄取得（頻度高）"""
        self.client.post("/api/fetch-data", 
                        json={"symbol": "7203.T", "period": "1y"})
    
    @task(1)
    def fetch_multiple_stocks(self):
        """複数銘柄取得（頻度低）"""
        self.client.post("/api/fetch-data",
                        json={"symbols": ["7203.T", "6758.T"], "period": "1y"})
    
    @task(2)
    def get_stocks_list(self):
        """株価一覧取得"""
        self.client.get("/api/stocks?page=1&limit=10")

# 負荷テスト実行設定
"""
実行コマンド:
locust -f tests/performance/test_load.py --host=http://localhost:8000

テスト条件:
- 同時ユーザー数: 10-100
- 実行時間: 5-60分
- 目標レスポンス時間: < 5秒
- エラー率: < 1%
"""
```

### 8.2 パフォーマンス指標

#### 応答時間目標
- **API エンドポイント**: 平均 < 2秒, 95%ile < 5秒
- **データベースクエリ**: 平均 < 500ms, 95%ile < 1秒
- **Yahoo Finance API**: 平均 < 3秒, 95%ile < 8秒

#### スループット目標
- **同時リクエスト**: 50リクエスト/秒
- **データ取得**: 10銘柄/分
- **データベース書き込み**: 1000レコード/分

## 9. テスト環境管理

### 9.1 環境別テスト設定

```python
# tests/conftest.py
import pytest
import os
from app import create_app
from app.models import db

@pytest.fixture
def app():
    """テスト用アプリケーション"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """テスト用HTTPクライアント"""
    return app.test_client()

# 環境別設定
TEST_CONFIG = {
    "unit": {
        "database": "sqlite:///:memory:",
        "external_api": "mock"
    },
    "integration": {
        "database": "postgresql://test:test@localhost/integration_test",
        "external_api": "staging"
    },
    "e2e": {
        "database": "postgresql://test:test@localhost/e2e_test",
        "external_api": "production"
    }
}
```

### 9.2 Docker Compose テスト環境

```yaml
# docker-compose.test.yml
version: '3.8'

services:
  postgres-test:
    image: postgres:15
    environment:
      POSTGRES_DB: stock_test_db
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_password
    ports:
      - "5433:5432"
    tmpfs:
      - /var/lib/postgresql/data  # インメモリDB（高速化）

  redis-test:
    image: redis:7
    ports:
      - "6380:6379"

  app-test:
    build: .
    environment:
      DATABASE_URL: postgresql://test_user:test_password@postgres-test:5432/stock_test_db
      REDIS_URL: redis://redis-test:6379
      FLASK_ENV: testing
    depends_on:
      - postgres-test
      - redis-test
    ports:
      - "8001:8000"
```

## 10. テスト品質メトリクス

### 10.1 カバレッジ目標

#### コードカバレッジ
- **Unit Tests**: 90%以上
- **Integration Tests**: 80%以上  
- **E2E Tests**: 60%以上（主要パス）

#### 機能カバレッジ
- **MVP機能**: 100%カバー
- **拡張機能**: 90%以上カバー
- **エラーケース**: 80%以上カバー

### 10.2 品質ゲート

品質ゲート・ブランチ別のマージ条件については、**[開発者ガイド](developer_guide.md)**を参照してください。

---

## まとめ

このテスト戦略では以下を実現しています：

✅ **包括的テスト設計**: Unit → Integration → E2E の段階的テスト  
✅ **自動化重視**: CI/CD パイプラインでの完全自動化  
✅ **アジャイル対応**: Sprint ごとの段階的テスト拡張  
✅ **品質保証**: カバレッジ・パフォーマンス・セキュリティの統合的品質管理  
✅ **実用性重視**: 実際の開発で価値のあるテストに集中

**次のアクション**:
1. MVP用テストの実装開始
2. CI/CD パイプラインのセットアップ
3. テストデータ・フィクスチャの準備
4. パフォーマンステスト環境の構築

この戦略により、高品質で信頼性の高いシステムを継続的に開発・リリースできます。