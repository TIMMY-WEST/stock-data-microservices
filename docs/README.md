# 株価データ取得システム - ドキュメント

> **⚠️ 重要な開発方針**
> このプロジェクトは**小規模個人開発**であり、**動作するものを作成することを最優先**としています。
> 完璧な設計よりも実動するソフトウェアの迅速な開発を重視します。

## 📋 ドキュメント構成

### 🏗️ プロジェクト全体
- **[プロジェクト全体アーキテクチャ](00_project_overview/project_architecture.md)** - システム全体の設計思想と進化計画

### 🔧 システム仕様
- **[アジャイル開発計画](00_project_overview/agile_development_plan.md)** - スプリント計画・開発プロセス
- **[開発者ガイド](00_project_overview/developer_guide.md)** - 開発プロセス・ブランチ戦略・運用ガイド
- **[テスト戦略](00_project_overview/test_strategy.md)** - テスト設計・CI/CD自動化

### 🏛️ アーキテクチャ設計
- **[データベース設計](01_architecture/database_design.md)** - DB スキーマ・インデックス戦略
- **[フロントエンド設計](01_architecture/frontend_design.md)** - UI/UX・コンポーネント設計
- **[環境構築仕様書](01_architecture/environment_setup.md)** - 開発環境・ディレクトリ構成
- **[API仕様書](01_architecture/api_specification.md)** - MVP版APIエンドポイント仕様

### 🐋 マイクロサービス仕様
- **[API Gateway Service](02_microservices/api_gateway_service.md)** - リクエストルーティング・統一API
- **[Financial Data Service](02_microservices/financial_data_service.md)** - Yahoo Finance連携・データ取得
- **[Data Management Service](02_microservices/data_management_service.md)** - データベース操作・永続化
- **[Notification Service](02_microservices/notification_service.md)** - 進捗管理・リアルタイム通知

## 🚀 クイックスタート

### 1. プロジェクト概要を理解する
まず **[プロジェクト全体アーキテクチャ](00_project_overview/project_architecture.md)** を読んで、システムの全体像と進化計画を把握してください。

### 2. 現在の実装（MVP版）を確認
- **[プロジェクト全体アーキテクチャ](00_project_overview/project_architecture.md)** - MVP実装と将来計画
- **[API仕様書](02_architecture/api_specification.md)** - 現在のAPIエンドポイント

### 3. 将来のマイクロサービス設計を理解
`03_microservices/` 配下の各サービス仕様書を参照して、将来の分離計画を理解してください。

### 4. 開発を開始する
- **[環境構築仕様書](02_architecture/environment_setup.md)** - 開発環境のセットアップ
- **[開発者ガイド](00_project_overview/developer_guide.md)** - 開発プロセス・ブランチ戦略

## 📊 アーキテクチャ進化

### Phase 1: MVP（現在）
```
Browser → Flask App → PostgreSQL
```
- 単一Flaskアプリで全機能を提供
- 基本的な株価データ取得・表示機能

### Phase 2: 機能拡張
```
Browser → Flask App (+ Redis) → PostgreSQL
```
- Redis追加（キャッシュ・タスクキュー）
- Excelファイル処理機能
- プログレス表示強化

### Phase 3: マイクロサービス分離
```
Browser → API Gateway → [Financial Data | Data Management | Notification] Services → PostgreSQL
```
- 4つの独立サービスに分離
- Docker コンテナ化
- サービス間HTTP通信

### Phase 4: スケーリング対応
```
Load Balancer → API Gateway → Microservices → Database Cluster
```
- 高可用性・負荷分散対応
- 監視・メトリクス収集
- Kubernetes対応

## 🎯 開発優先度

### 🔥 **高優先度（Sprint 1-2）**
1. **MVP機能完成** - 基本的なデータ取得・表示
2. **UI/UX改善** - macOS風デザイン実装
3. **エラーハンドリング強化**

### 🚀 **中優先度（Sprint 3-4）**
1. **Excel連携機能** - ファイル処理サービス
2. **プログレス表示強化** - リアルタイム更新
3. **データ管理機能** - 削除・更新機能

### 💡 **将来実装（Phase 3以降）**
1. **マイクロサービス分離** - 独立サービス化
2. **WebSocket通知** - リアルタイム進捗
3. **認証・認可** - ユーザー管理

## 🔍 ドキュメント更新ポリシー

### ドキュメント管理原則
1. **プロジェクト全体仕様** と **個別マイクロサービス仕様** に明確に分離
2. **MVP実装** と **将来計画** の両方を記載
3. **実装例** を豊富に含める
4. **設計思想** と **技術選択理由** を明記

### 更新タイミング
- ✅ **仕様変更時**: 該当ドキュメントを即座に更新
- ✅ **実装完了時**: 実装内容をドキュメントに反映
- ✅ **アーキテクチャ変更時**: 関連する全ドキュメントを更新
- ✅ **定期レビュー**: スプリント終了時にドキュメント整合性確認

## 🤝 コントリビューション

### ドキュメント改善への貢献
- 不明確な記述の改善提案
- 実装例の追加
- 図表・フローチャートの追加
- 翻訳・多言語対応

### 技術仕様の提案
- 新機能の仕様設計
- パフォーマンス改善提案
- セキュリティ強化提案

---

## 📞 サポート・フィードバック

ドキュメントに関する質問や改善提案がある場合は、以下の方法でお気軽にご連絡ください：

- **Issue作成** - 特定のドキュメント改善提案
- **Pull Request** - 直接的なドキュメント修正
- **ディスカッション** - 設計思想や技術選択に関する議論

このドキュメント構成により、**現在のMVP開発** と **将来のマイクロサービス移行** の両方をサポートし、段階的な成長を実現できます。
