-- PostgreSQL 初期化スクリプト
-- Stock Data App 用データベース初期設定

-- タイムゾーン設定
SET timezone = 'Asia/Tokyo';

-- 基本的な拡張機能の有効化
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- データベース接続確認用テーブル（テスト用）
CREATE TABLE IF NOT EXISTS system_status (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 初期データ投入
INSERT INTO system_status (service_name, status)
VALUES ('database', 'initialized')
ON CONFLICT DO NOTHING;

-- 基本的なインデックス
CREATE INDEX IF NOT EXISTS idx_system_status_service
ON system_status (service_name);

-- データベース初期化完了ログ
INSERT INTO system_status (service_name, status)
VALUES ('database_init', 'completed')
ON CONFLICT DO NOTHING;

-- 権限設定（セキュリティ強化）
GRANT ALL PRIVILEGES ON DATABASE stock_db TO stock_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO stock_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO stock_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO stock_user;

-- デフォルト権限設定（新規テーブル用）
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL PRIVILEGES ON TABLES TO stock_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL PRIVILEGES ON SEQUENCES TO stock_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL PRIVILEGES ON FUNCTIONS TO stock_user;
