# 株価データ取得・管理システム 開発者ガイド

## 1. アーキテクチャ・設計原則

### 1.1 基本設計原則
- **マイクロサービス**: サービス分離による拡張性・保守性の確保
- **API First**: サービス間通信をRESTful APIで統一
- **MVP優先**: 動作するものから段階的拡張
- **アジャイル対応**: 仕様変更に柔軟に対応可能な設計

### 1.2 技術スタック標準
- **フロントエンド**: Alpine.js + Tailwind CSS + Headless UI
- **API Gateway**: Python Flask
- **マイクロサービス**: Python FastAPI
- **データベース**: PostgreSQL
- **メッセージング**: Redis (サービス間通信)
- **外部API**: Yahoo Finance (yfinance ライブラリ)

### 1.3 デザインシステム
- **Color Palette**: macOS Big Sur風の色合い（グレー基調、アクセントブルー）
- **Typography**: San Francisco風フォント（system-ui, -apple-system）
- **Components**: 角丸、影、透明度を活用
- **Animation**: 60fps スムーズトランジション

## 2. 開発環境セットアップ

### 2.1 必要ソフトウェア（必須）
| ソフトウェア | バージョン | 用途 |
|-------------|-----------|------|
| Python | 3.11+ | バックエンド開発 |
| Git | 2.30+ | バージョン管理 |
| Docker | 20.0+ | データベースコンテナ |
| Docker Compose | 2.0+ | コンテナオーケストレーション |
| Node.js | 18+ | MCP Server実行環境 |

### 2.2 開発環境構築手順
1. **Python仮想環境の使用必須**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Docker Composeでのデータベース管理**
   ```bash
   docker-compose up -d postgres
   ```

3. **環境変数管理（.envファイル使用）**
   ```bash
   cp .env.example .env
   # .env ファイルを環境に合わせて編集
   ```

### 2.3 VS Code推奨設定
```json
{
    "python.interpreter": "./venv/bin/python",
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "88"],
    "python.linting.flake8Enabled": true
}
```

**推奨拡張機能**:
- ms-python.python
- ms-python.black-formatter
- ms-python.flake8
- bradlc.vscode-tailwindcss

## 3. ブランチ戦略・Git運用ルール

### 3.1 ブランチ構成
```
main (本番用)
├── develop (統合開発用)
│   ├── feature/fetch-single-stock (機能開発用)
│   ├── feature/ui-progress-bar
│   └── feature/database-setup
└── hotfix/critical-bug-fix (緊急修正用)
```

### 3.2 ブランチ運用ルール

#### mainブランチ
- **用途**: 本番リリース可能な状態を維持
- **保護**: 直接pushは禁止、Pull Requestのみ
- **マージ条件**: テスト通過 + コードレビュー完了

#### developブランチ  
- **用途**: 各機能ブランチの統合・結合テスト
- **作成元**: mainブランチから作成
- **マージ先**: mainブランチへPull Request

#### feature/ブランチ
- **命名規則**: `feature/{sprint-task-name}`
  - 例: `feature/fetch-single-stock`, `feature/ui-macOS-design`
- **作成元**: developブランチから作成
- **マージ先**: developブランチへPull Request
- **削除**: マージ後は削除

### 3.3 コミットメッセージ規約

#### 3.3.1 基本フォーマット
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### 3.3.2 Type（種別）
- **feat**: 新機能の追加
- **fix**: バグ修正
- **docs**: ドキュメントのみの変更
- **style**: コードの意味に影響しない変更（空白、フォーマット、セミコロン等）
- **refactor**: バグ修正も機能追加も含まないコードの変更
- **perf**: パフォーマンスを向上させるコードの変更
- **test**: テストの追加や修正
- **chore**: ビルドプロセスやツールの変更、ライブラリの更新等
- **ci**: CI設定ファイルやスクリプトの変更

#### 3.3.3 Scope（スコープ）
プロジェクト内の変更箇所を明示（オプション）:
- **api**: APIゲートウェイ関連
- **stock**: 株価取得サービス関連  
- **frontend**: フロントエンド関連
- **db**: データベース関連
- **docker**: Docker設定関連

#### 3.3.4 Description（説明）
- **日本語**で記載すること
- 50文字以内で簡潔に記述
- 動詞は現在形を使用（"add" not "added"）
- 先頭文字は小文字
- 末尾にピリオド不要

#### 3.3.5 コミットメッセージ例
```bash
# 良い例
feat(api): add stock price fetching endpoint
fix(db): resolve connection timeout issue
docs: update installation guide
refactor(stock): simplify price calculation logic
test(api): add unit tests for authentication

# 悪い例
Added new feature
Fix bug
Update
stock price api
```

#### 3.3.6 Issue連携
コミットメッセージにIssue番号を含める:
```bash
feat(api): implement Yahoo Finance integration #123
fix(frontend): resolve responsive design issue #124

# 複数Issue対応の場合
fix(db): resolve connection issues #125 #126
```

### 3.4 開発フロー
```
1. Sprint開始: develop ← main (最新状態に同期)
2. 機能開発: feature/task-name ← develop
3. 機能完成: feature/task-name → develop (Pull Request)
4. Sprint完了: develop → main (Pull Request)
5. リリース: main ブランチからデプロイ
```

## 4. コーディング規約・品質基準

### 4.1 Python コーディング規約
- **フォーマット**: Black (88文字制限)
- **リンター**: Flake8
- **型ヒント**: 関数の引数・戻り値に型注釈を使用
- **docstring**: 関数・クラスにはGoogle形式のdocstringを記述

### 4.2 コード品質基準
- **可読性重視**: 変数名・関数名・コメントは日本語でも可（わかりやすさ優先）
- **DRY原則**: 重複コードの排除
- **SRP原則**: 関数・クラスは単一責任
- **適切なデザインパターンの使用**

### 4.3 API設計規約
- **RESTful API**: HTTPメソッド（GET, POST, PUT, DELETE）の適切な使用
- **レスポンス形式**: JSON統一
- **エラーハンドリング**: 適切なHTTPステータスコードの使用
- **API仕様**: OpenAPIドキュメント作成

## 5. テスト戦略・品質ゲート

### 5.1 テストピラミッド配分
- **Unit Tests**: 70% (高速・大量実行)
- **Integration Tests**: 20% (サービス連携確認)
- **E2E Tests**: 10% (重要シナリオのみ)

### 5.2 カバレッジ目標
- **Unit Tests**: 90%以上
- **Integration Tests**: 80%以上  
- **E2E Tests**: 60%以上（主要パス）

### 5.3 品質ゲート（ブランチ別）

#### feature → develop マージ条件
- [ ] 全単体テストが成功
- [ ] コードカバレッジ 85%以上
- [ ] 統合テストが成功
- [ ] セキュリティスキャンでクリティカル脆弱性なし
- [ ] コードレビュー完了

#### develop → main マージ条件（厳格）
- [ ] 全単体テストが成功
- [ ] コードカバレッジ 90%以上
- [ ] 統合テストが成功
- [ ] E2Eテストが成功
- [ ] パフォーマンステスト目標達成
- [ ] セキュリティスキャンでクリティカル・ハイ脆弱性なし
- [ ] コードレビュー完了

### 5.4 テスト実行トリガー
- **feature → develop PR時**: 単体テスト・統合テスト実行
- **develop → main PR時**: 全テストスイート実行（Unit + Integration + E2E）
- **main ブランチプッシュ時**: デプロイ前最終確認テスト
- **定期実行**: 毎日深夜に develop ブランチで回帰テスト実行

## 6. GitHub活用・Issue管理・ブランチ戦略・レビュープロセス

### 6.1 GitHub Issues によるラベル管理

#### 必須ラベルシステム
**優先度ラベル**
- `priority:critical` - 🚨 システムダウン・セキュリティ問題（即時対応）
- `priority:high` - ⬆️ リリースブロッカー・重要機能影響（当日対応）
- `priority:medium` - ➡️ 通常の機能開発・改善（1週間以内）
- `priority:low` - ⬇️ 将来的な改善・Nice to have（リリース後）

**タスク種別ラベル**
- `type:feature` - ✨ 新機能開発
- `type:bug` - 🐛 バグ修正
- `type:task` - 📋 技術的タスク・環境整備
- `type:enhancement` - 🚀 既存機能の改善・最適化
- `type:documentation` - 📚 ドキュメント作成・更新
- `type:refactor` - 🔧 リファクタリング・技術的負債解消

**進捗ステータスラベル**
- `status:todo` - 📋 未着手・バックログ
- `status:in-progress` - 🔄 作業中
- `status:review` - 👀 レビュー待ち・レビュー中
- `status:testing` - ✅ テスト中・QA中
- `status:blocked` - 🚧 ブロック状態・他タスク依存

**サービス別ラベル**
- `service:api-gateway` - 🌐 APIゲートウェイ関連
- `service:stock-service` - 📈 株価取得サービス関連
- `service:frontend` - 🖥️ フロントエンド関連
- `service:database` - 🗃️ データベース関連
- `service:infrastructure` - 🏗️ インフラ・DevOps関連

### 6.2 ブランチ戦略の詳細

#### ブランチ構成とルール
```
main (保護ブランチ)
├── develop (統合ブランチ)
│   ├── feature/issue-123-stock-api-integration
│   ├── feature/issue-124-ui-dashboard-design
│   ├── bugfix/issue-125-database-connection-error
│   └── hotfix/issue-126-critical-security-patch
```

**ブランチ命名規則（必須）**
- `feature/issue-{number}-{short-description}` - 新機能開発
- `bugfix/issue-{number}-{short-description}` - バグ修正
- `hotfix/issue-{number}-{short-description}` - 緊急修正
- `refactor/issue-{number}-{short-description}` - リファクタリング
- `docs/issue-{number}-{short-description}` - ドキュメント更新

**例：**
```bash
feature/issue-101-yahoo-finance-api-integration
bugfix/issue-102-portfolio-calculation-error
hotfix/issue-103-database-security-patch
```

#### ブランチ保護設定
**main ブランチ保護ルール（必須設定）**
- ✅ 直接プッシュを禁止
- ✅ Pull Request 必須
- ✅ レビュー必須（最低1名承認）
- ✅ ステータスチェック必須（CI/CDテスト通過）
- ✅ 最新状態での作業必須（Up-to-date before merge）
- ✅ 管理者もルール適用

**develop ブランチ保護ルール**
- ✅ Pull Request 必須
- ✅ レビュー推奨（最低1名承認）
- ✅ CI/CDテスト通過必須

### 6.3 Pull Request レビュープロセス

#### レビュー必須条件
**技術レビュー項目**
- ✅ **機能要件充足**: Issue要件を100%満たしているか
- ✅ **コード品質**: 可読性・保守性・DRY原則遵守
- ✅ **アーキテクチャ準拠**: 設計原則・技術スタックに準拠
- ✅ **テスト充実**: 単体・統合テストが85%以上のカバレッジ
- ✅ **エラーハンドリング**: 適切な例外処理・ログ出力
- ✅ **セキュリティ**: SQLインジェクション・XSS対策実装
- ✅ **パフォーマンス**: レスポンス時間・リソース使用量確認

**マージ承認ルール**
- **Feature → Develop**: 最低1名の承認必須
- **Develop → Main**: 最低2名の承認必須（リードエンジニア含む）
- **Hotfix → Main**: 緊急時は1名承認でも可（事後報告必須）

#### レビューア指定ルール
```markdown
## レビューア指定優先順位

### 1. Code Owner（必須レビューア）
- Frontend: @frontend-lead
- Backend API: @backend-lead  
- Database: @database-admin
- Infrastructure: @devops-lead

### 2. サブレビューア（推奨）
- 同じサービス開発者
- 関連機能の開発経験者
```

#### Pull Request テンプレート
```markdown
## 📋 変更内容
<!-- Issue番号とリンク -->
Closes #[Issue番号]

### 🎯 目的・背景
[なぜこの変更が必要か]

### 🔧 主な変更点
- [ ] 変更点1
- [ ] 変更点2
- [ ] 変更点3

### ✅ テスト実施内容
- [ ] 単体テスト実装・実行
- [ ] 統合テスト実行
- [ ] 手動動作確認
- [ ] パフォーマンステスト（必要に応じて）

### 🔍 レビューポイント
<!-- レビューアに特に確認してもらいたい点 -->

### 📸 スクリーンショット・動画（UI変更時）
<!-- Before/After の画像・動画 -->

### ⚠️ 破壊的変更・注意点
<!-- 既存機能への影響、設定変更の必要性など -->

### 📝 関連ドキュメント更新
- [ ] README.md更新
- [ ] API仕様書更新  
- [ ] 開発者ガイド更新
```

### 6.4 タスク管理戦略
**GitHub Issues + Projects を使用したアジャイル開発**

#### GitHub Projects 活用方法
**カンバンボード構成**
```
📋 Backlog → 🔄 Todo → 👷 In Progress → 👀 Review → ✅ Testing → 🎉 Done
```

**プロジェクトビュー設定**
- **Board View**: カンバン形式でタスク進捗管理
- **Table View**: 優先度・担当者・期限での並び替え
- **Calendar View**: リリーススケジュール・デッドライン管理
- **Roadmap View**: 中長期的な機能開発計画

#### マイルストーン管理
**マイルストーン設定例**
- `Sprint 1 - MVP Core` (期限: 2024-02-15)
- `Sprint 2 - UI Enhancement` (期限: 2024-03-01)  
- `v1.0.0 Release` (期限: 2024-03-15)
- `v1.1.0 Feature Update` (期限: 2024-04-30)

### 6.5 ブランチとIssueの連携

#### 自動化ルール設定
**Issue自動クローズ**
```bash
# PRタイトル・コメントでIssue自動クローズ
"Fix #123: 株価取得APIの実装"
"Resolve #456: ダッシュボードのレスポンシブ対応"  
"Close #789: データベース接続エラーの修正"
```

**PRとIssue連携パターン**
```markdown
<!-- PR説明欄 -->
## 関連Issue
- Closes #123 (メイン機能)
- Fixes #124 (バグ修正)  
- Resolves #125 (サブタスク)
- Relates to #126 (関連作業)
```

#### ブランチ作成からマージまでのフロー
```bash
# 1. Issue作成・ラベル設定・担当者アサイン
# 2. developブランチから作業ブランチ作成
git checkout develop
git pull origin develop
git checkout -b feature/issue-101-stock-api-integration

# 3. 開発・コミット（コミットメッセージにIssue番号含める）
git commit -m "feat: Implement Yahoo Finance API client #101"

# 4. PR作成（テンプレート使用・レビューア指定）
# 5. レビュー・修正・承認
# 6. マージ・ブランチ削除・Issue自動クローズ
```

このシステムにより、Issue・PR・ブランチが完全に連携し、アジャイル開発でのタスク追跡が自動化されます。

### 6.2 Issue発行基準
**以下の場合に必ずIssueを作成する:**
- **バグ発見時**: システムの異常動作・エラー、予期しない結果
- **新機能・改善要求**: User Storyに基づく機能開発、UI/UX改善提案
- **技術的課題**: 技術的負債の解消、パフォーマンス最適化
- **環境・設定問題**: 開発環境のセットアップ課題、CI/CD改善

### 6.3 GitHub Issue項目管理ルール

**Issueには以下の項目を必ず設定すること:**

#### Assignees（担当者）
- Issue作成時に担当者を必ず指定
- 複数人での作業の場合は主担当者を明確化
- 未アサインのIssueは放置されるリスクが高いため避ける

#### Labels（ラベル）
以下の分類でラベルを設定：
- **種類**: `bug`, `feature`, `enhancement`, `documentation`, `refactor`
- **優先度**: `priority:high`, `priority:medium`, `priority:low`, `priority:critical`
- **サービス**: `api-gateway`, `stock-service`, `frontend`, `database`
- **状態**: `in-progress`, `review-ready`, `blocked`, `duplicate`

#### Projects（プロジェクト）
- @TIMMY-WEST's Stock Data Microservicesを必ず設定する
- リリーススケジュールとの紐付けを明確化

#### Milestone（マイルストーン）
- リリースバージョンまたはスプリント目標に対応するマイルストーンを設定
- 例: `v1.0.0 MVP`, `Sprint 1`, `2024 Q1 Release`
- デッドラインを明確にすることで優先度付けを行う

#### Relationships（関連性）
- 依存関係がある他のIssueを明記
- 例: `Blocks #123`, `Depends on #456`, `Related to #789`
- ブロック関係を明確にして作業順序を最適化
- 大きなタスクの場合は子Issue（Sub-tasks）に分割

### 6.4 Issue作成テンプレート

#### バグ報告用
```markdown
## 🐛 バグ報告

### 現象
[発生している問題の詳細]

### 再現手順
1. [手順1]
2. [手順2]
3. [手順3]

### 期待される動作
[本来どうあるべきか]

### 実際の動作
[実際に何が起きているか]

### 環境情報
- OS: [Windows/macOS/Linux]
- ブラウザ: [Chrome/Firefox/Safari]
- Python: [バージョン]
- 関連サービス: [該当マイクロサービス]

### 優先度
- [ ] Critical (システム停止)
- [ ] High (主要機能に影響)
- [ ] Medium (一部機能に影響)
- [ ] Low (軽微な問題)
```

### 6.4 Pull Request運用

#### PR作成必須条件
**以下すべてを満たしてからPRを作成する:**
1. **コード完成**: 実装が完了し、動作確認済み
2. **テスト実装**: 単体テスト・結合テストが実装済み
3. **テスト通過**: すべてのテストがパスしている
4. **ドキュメント更新**: 必要に応じてREADME・APIドキュメント更新
5. **自己レビュー**: 自分でコードレビューを実施済み

#### コードレビュー基準

**必須レビュー項目**
- ✅ 要件・仕様を満たしているか
- ✅ アーキテクチャ方針に準拠しているか
- ✅ 既存機能への影響がないか
- ✅ エラーハンドリングが適切か
- ✅ 可読性が高いか（変数名・関数名・コメント）
- ✅ 重複コードがないか（DRY原則）
- ✅ セキュリティ対策が実装されているか
- ✅ テストカバレッジが十分か（80%以上）

#### マージ条件
- ✅ すべてのCIテストが通過
- ✅ 必要な承認数を獲得（最小1名、重要変更は2名）
- ✅ マージ競合が解決済み
- ✅ ブランチが最新状態

## 7. セキュリティガイドライン

### 7.1 セキュリティ要件（必須）
- **SQLインジェクション対策**: パラメータ化クエリの使用
- **XSS対策**: 適切なエスケープ処理
- **ファイルアップロード**: 許可された形式のみ受付
- **認証・認可**: 適切な実装

### 7.2 機密情報管理
- **環境変数使用**: API Key、パスワードは.envファイルで管理
- **Git管理対象外**: .envファイル、秘密鍵はコミット禁止
- **ログ出力**: 機密情報をログに出力しない

## 8. パフォーマンス・非機能要件

### 8.1 性能要件
- **同時取得**: 最大100銘柄の並列処理
- **レスポンス時間**: UI操作に対して1秒以内の応答
- **データ量**: 10万レコード程度まで対応

### 8.2 パフォーマンス指標
- **APIエンドポイント**: 平均 < 2秒, 95%ile < 5秒
- **データベースクエリ**: 平均 < 500ms, 95%ile < 1秒
- **Yahoo Finance API**: 平均 < 3秒, 95%ile < 8秒

## 9. トラブルシューティング

### 9.1 よくある問題と解決方法

#### ポート競合エラー
```bash
# Port 5432 is already in use
# 解決: docker-compose.yml の ports を "5433:5432" に変更
```

#### Python仮想環境の問題
```bash
# 仮想環境の再作成
rm -rf venv
python -m venv venv
```

#### データベース接続エラー
```bash
# Docker Desktop が起動していることを確認
docker --version
docker-compose up -d postgres
```

### 9.2 ログ確認方法
```bash
# Docker Compose ログ
docker-compose logs -f postgres

# アプリケーションログ
python run.py  # コンソール出力で確認
```

## 10. 開発支援ツール・Claude MCP連携

### 10.1 Claude MCP活用
Claude チャットで以下の開発支援を受けられます：
- "プロジェクトの状態を確認してください"
- "APIエンドポイントをチェックしてください"  
- "データベースの状況を教えてください"
- "テストを実行してください"

### 10.2 便利なコマンド
```bash
# 開発環境起動
python run.py

# テスト実行
pytest tests/ -v

# コードフォーマット
black app/ tests/

# リンターチェック
flake8 app/ tests/

# データベースマイグレーション
flask db migrate -m "migration message"
flask db upgrade
```

---

## 開発者チェックリスト

新しい機能開発時は以下を確認してください：

### ✅ 開発開始前
- [ ] feature ブランチを develop から作成
- [ ] Issue を作成・アサイン
- [ ] 要件・仕様を理解

### ✅ 開発中
- [ ] コーディング規約に準拠
- [ ] 単体テストを並行して作成
- [ ] セキュリティ要件を考慮
- [ ] 適切なエラーハンドリング実装

### ✅ 開発完了時
- [ ] 全テストがパス（Unit + Integration）
- [ ] コードカバレッジ85%以上
- [ ] 自己コードレビュー実施
- [ ] ドキュメント更新
- [ ] Pull Request作成

### ✅ レビュー・マージ後
- [ ] develop ブランチでの統合テスト確認
- [ ] feature ブランチ削除
- [ ] Issue クローズ

このガイドに従うことで、高品質で保守性の高いシステムを継続的に開発できます。