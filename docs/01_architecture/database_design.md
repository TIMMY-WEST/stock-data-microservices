# データベース設計書 (MVP版)

## 1. 設計概要

### 1.1 設計方針
- **シンプルファースト**: MVP に必要最小限のテーブル構成
- **正規化**: 基本的な正規化（第3正規形まで）
- **拡張性**: 将来の機能追加に対応可能な設計
- **パフォーマンス**: 基本的なインデックス設定

### 1.2 使用技術
- **RDBMS**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0+
- **Migration**: Alembic
- **開発環境**: Docker Compose (PostgreSQL コンテナ)

## 2. データベース構成

### 2.1 データベース情報
```yaml
データベース名: stock_data_db
文字エンコーディング: UTF-8
タイムゾーン: Asia/Tokyo
接続ポート: 5432
```

### 2.2 テーブル一覧

| テーブル名 | 用途 | 優先度 |
|-----------|------|--------|
| stock_data | 株価データ（日足） | 🔴 MVP必須 |
| fetch_logs | データ取得ログ | 🔴 MVP必須 |
| stock_symbols | 銘柄マスタ | 🟡 拡張時 |

## 3. テーブル設計詳細

### 3.1 stock_data テーブル（株価データ）

**用途**: Yahoo Finance から取得した日足株価データを格納

```sql
CREATE TABLE stock_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,                    -- 銘柄コード (例: 7203.T)
    date DATE NOT NULL,                            -- 取引日
    open DECIMAL(10, 2),                           -- 始値
    high DECIMAL(10, 2),                           -- 高値  
    low DECIMAL(10, 2),                            -- 安値
    close DECIMAL(10, 2) NOT NULL,                 -- 終値
    adj_close DECIMAL(10, 2),                      -- 調整後終値
    volume BIGINT,                                 -- 出来高
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 作成日時
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 更新日時
    
    -- 制約
    CONSTRAINT uk_stock_data_symbol_date UNIQUE (symbol, date)
);

-- インデックス
CREATE INDEX idx_stock_data_symbol ON stock_data (symbol);
CREATE INDEX idx_stock_data_date ON stock_data (date);
CREATE INDEX idx_stock_data_symbol_date ON stock_data (symbol, date);
```

#### カラム詳細

| カラム名 | データ型 | NULL | 説明 | 例 |
|---------|---------|------|------|---|
| id | SERIAL | NOT NULL | 主キー（自動採番） | 1, 2, 3... |
| symbol | VARCHAR(20) | NOT NULL | 銘柄コード | "7203.T", "6758.T" |
| date | DATE | NOT NULL | 取引日 | "2024-01-15" |
| open | DECIMAL(10,2) | NULL | 始値 | 2500.50 |
| high | DECIMAL(10,2) | NULL | 高値 | 2580.00 |
| low | DECIMAL(10,2) | NULL | 安値 | 2480.25 |
| close | DECIMAL(10,2) | NOT NULL | 終値 | 2530.75 |
| adj_close | DECIMAL(10,2) | NULL | 調整後終値 | 2530.75 |
| volume | BIGINT | NULL | 出来高 | 1500000 |
| created_at | TIMESTAMP | NOT NULL | 作成日時 | "2024-01-15 10:30:00" |
| updated_at | TIMESTAMP | NOT NULL | 更新日時 | "2024-01-15 10:30:00" |

### 3.2 fetch_logs テーブル（取得ログ）

**用途**: データ取得処理の実行履歴・結果を記録

```sql
CREATE TABLE fetch_logs (
    id SERIAL PRIMARY KEY,
    fetch_id UUID NOT NULL,                        -- 取得処理ID（バッチ識別用）
    symbol VARCHAR(20),                            -- 対象銘柄コード
    status VARCHAR(20) NOT NULL,                   -- 処理結果 ('success', 'error', 'skipped')
    start_date DATE,                               -- 取得開始日
    end_date DATE,                                 -- 取得終了日  
    records_count INTEGER DEFAULT 0,              -- 取得レコード数
    error_message TEXT,                           -- エラーメッセージ
    processing_time_ms INTEGER,                   -- 処理時間（ミリ秒）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- 実行日時
);

-- インデックス
CREATE INDEX idx_fetch_logs_fetch_id ON fetch_logs (fetch_id);
CREATE INDEX idx_fetch_logs_symbol ON fetch_logs (symbol);  
CREATE INDEX idx_fetch_logs_status ON fetch_logs (status);
CREATE INDEX idx_fetch_logs_created_at ON fetch_logs (created_at);
```

#### カラム詳細

| カラム名 | データ型 | NULL | 説明 | 例 |
|---------|---------|------|------|---|
| id | SERIAL | NOT NULL | 主キー | 1, 2, 3... |
| fetch_id | UUID | NOT NULL | バッチ処理ID | "550e8400-e29b-41d4-a716-446655440000" |
| symbol | VARCHAR(20) | NULL | 銘柄コード | "7203.T" |
| status | VARCHAR(20) | NOT NULL | 処理結果 | "success", "error", "skipped" |
| start_date | DATE | NULL | 取得期間開始日 | "2023-01-15" |
| end_date | DATE | NULL | 取得期間終了日 | "2024-01-15" |
| records_count | INTEGER | NOT NULL | 取得件数 | 252 |
| error_message | TEXT | NULL | エラー内容 | "Invalid symbol" |
| processing_time_ms | INTEGER | NULL | 処理時間 | 1500 |
| created_at | TIMESTAMP | NOT NULL | 実行時刻 | "2024-01-15 10:30:00" |

## 4. SQLAlchemy モデル定義

### 4.1 models/stock_data.py

```python
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, BigInteger, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class StockData(Base):
    """株価データモデル"""
    __tablename__ = 'stock_data'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open = Column(Numeric(10, 2))
    high = Column(Numeric(10, 2))
    low = Column(Numeric(10, 2))
    close = Column(Numeric(10, 2), nullable=False)
    adj_close = Column(Numeric(10, 2))
    volume = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ユニーク制約
    __table_args__ = (
        {'schema': None}
    )
    
    def __repr__(self):
        return f"<StockData(symbol='{self.symbol}', date='{self.date}', close={self.close})>"
    
    def to_dict(self):
        """辞書形式での出力"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'date': self.date.isoformat() if self.date else None,
            'open': float(self.open) if self.open else None,
            'high': float(self.high) if self.high else None,
            'low': float(self.low) if self.low else None,
            'close': float(self.close) if self.close else None,
            'adj_close': float(self.adj_close) if self.adj_close else None,
            'volume': self.volume,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class FetchLog(Base):
    """取得ログモデル"""
    __tablename__ = 'fetch_logs'
    
    id = Column(Integer, primary_key=True)
    fetch_id = Column(String(36), nullable=False, index=True)  # UUID string
    symbol = Column(String(20), index=True)
    status = Column(String(20), nullable=False, index=True)
    start_date = Column(Date)
    end_date = Column(Date)
    records_count = Column(Integer, default=0)
    error_message = Column(Text)
    processing_time_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<FetchLog(fetch_id='{self.fetch_id}', symbol='{self.symbol}', status='{self.status}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'fetch_id': self.fetch_id,
            'symbol': self.symbol,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'records_count': self.records_count,
            'error_message': self.error_message,
            'processing_time_ms': self.processing_time_ms,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
```

## 5. データベース操作

### 5.1 基本的なCRUD操作

#### 株価データの保存
```python
def save_stock_data(symbol: str, data: list, mode: str = 'overwrite'):
    """
    株価データを保存
    
    Args:
        symbol: 銘柄コード
        data: 株価データリスト
        mode: 'overwrite' | 'skip'
    """
    session = Session()
    try:
        for record in data:
            if mode == 'skip':
                # 既存データがあればスキップ
                existing = session.query(StockData).filter(
                    StockData.symbol == symbol,
                    StockData.date == record['date']
                ).first()
                if existing:
                    continue
            
            # データ保存（上書きモード）
            stock_data = StockData(
                symbol=symbol,
                date=record['date'],
                open=record['open'],
                high=record['high'],
                low=record['low'],
                close=record['close'],
                adj_close=record.get('adj_close'),
                volume=record.get('volume')
            )
            session.merge(stock_data)  # INSERT または UPDATE
            
        session.commit()
        
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
```

#### 株価データの取得
```python
def get_stock_data(symbol: str = None, start_date: date = None, end_date: date = None, 
                  page: int = 1, per_page: int = 100):
    """
    株価データを取得
    
    Args:
        symbol: 銘柄コード（指定時は該当銘柄のみ）
        start_date: 開始日
        end_date: 終了日
        page: ページ番号
        per_page: 1ページあたりの件数
    
    Returns:
        dict: {'data': [...], 'total': 件数, 'page': ページ, 'per_page': 件数}
    """
    session = Session()
    
    query = session.query(StockData)
    
    # フィルター適用
    if symbol:
        query = query.filter(StockData.symbol == symbol)
    if start_date:
        query = query.filter(StockData.date >= start_date)
    if end_date:
        query = query.filter(StockData.date <= end_date)
    
    # 並び順
    query = query.order_by(StockData.symbol, StockData.date.desc())
    
    # 総件数
    total = query.count()
    
    # ページネーション
    offset = (page - 1) * per_page
    data = query.offset(offset).limit(per_page).all()
    
    session.close()
    
    return {
        'data': [item.to_dict() for item in data],
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    }
```

### 5.2 ログ記録

```python
def log_fetch_result(fetch_id: str, symbol: str, status: str, 
                    records_count: int = 0, error_message: str = None,
                    processing_time_ms: int = None):
    """取得結果をログに記録"""
    session = Session()
    try:
        log = FetchLog(
            fetch_id=fetch_id,
            symbol=symbol,
            status=status,
            records_count=records_count,
            error_message=error_message,
            processing_time_ms=processing_time_ms
        )
        session.add(log)
        session.commit()
    finally:
        session.close()
```

## 6. データベースセットアップ

### 6.1 Docker Compose設定

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: stock_postgres
    environment:
      POSTGRES_DB: stock_data_db
      POSTGRES_USER: stock_user
      POSTGRES_PASSWORD: stock_password
      TZ: Asia/Tokyo
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped

volumes:
  postgres_data:
```

### 6.2 初期化SQL

```sql
-- init.sql
-- データベース作成後の初期設定

-- タイムゾーン設定
SET timezone = 'Asia/Tokyo';

-- 拡張機能有効化
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- インデックス作成（テーブル作成後）
-- stock_data テーブル用
CREATE INDEX IF NOT EXISTS idx_stock_data_symbol ON stock_data (symbol);
CREATE INDEX IF NOT EXISTS idx_stock_data_date ON stock_data (date);
CREATE INDEX IF NOT EXISTS idx_stock_data_symbol_date ON stock_data (symbol, date);

-- fetch_logs テーブル用
CREATE INDEX IF NOT EXISTS idx_fetch_logs_fetch_id ON fetch_logs (fetch_id);
CREATE INDEX IF NOT EXISTS idx_fetch_logs_symbol ON fetch_logs (symbol);
CREATE INDEX IF NOT EXISTS idx_fetch_logs_status ON fetch_logs (status);
CREATE INDEX IF NOT EXISTS idx_fetch_logs_created_at ON fetch_logs (created_at);
```

### 6.3 Alembic Migration設定

```python
# alembic/env.py
import os
from alembic import context
from sqlalchemy import engine_from_config, pool
from app.models.stock_data import Base

# データベース接続URL
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://stock_user:stock_password@localhost:5432/stock_data_db')

config = context.config
config.set_main_option('sqlalchemy.url', DATABASE_URL)

target_metadata = Base.metadata

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
```

## 7. パフォーマンス考慮事項

### 7.1 インデックス戦略

**必須インデックス:**
- `stock_data(symbol)` - 銘柄別検索用
- `stock_data(date)` - 日付範囲検索用  
- `stock_data(symbol, date)` - 複合検索用

**将来追加予定:**
- `stock_data(symbol, date DESC)` - 最新データ取得用
- パーティショニング（年別）

### 7.2 クエリ最適化

```sql
-- 良いクエリ例：インデックスを活用
SELECT * FROM stock_data 
WHERE symbol = '7203.T' 
  AND date >= '2024-01-01' 
ORDER BY date DESC 
LIMIT 100;

-- 避けるべきクエリ：フルスキャン発生
SELECT * FROM stock_data 
WHERE EXTRACT(YEAR FROM date) = 2024;  -- 関数使用でインデックス無効化
```

## 8. バックアップ・復旧

### 8.1 バックアップスクリプト

```bash
#!/bin/bash
# backup.sh - データベースバックアップ

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup"
DB_NAME="stock_data_db"

# フルバックアップ
docker exec stock_postgres pg_dump -U stock_user $DB_NAME > $BACKUP_DIR/stock_db_$DATE.sql

# 圧縮
gzip $BACKUP_DIR/stock_db_$DATE.sql

echo "Backup completed: stock_db_$DATE.sql.gz"
```

### 8.2 復旧手順

```bash
# 1. バックアップファイルの復元
gunzip stock_db_20240115_100000.sql.gz

# 2. データベース復旧
docker exec -i stock_postgres psql -U stock_user -d stock_data_db < stock_db_20240115_100000.sql
```

## まとめ

このMVP版データベース設計では：

### ✅ **実装範囲**
- 株価データ保存（stock_data）
- 取得ログ管理（fetch_logs）
- 基本的なCRUD操作
- Docker でのローカル環境構築

### 🚀 **拡張準備**
- 銘柄マスタテーブル（将来追加）
- パーティショニング対応
- レプリケーション準備
- 監視・メトリクス収集

この設計により、シンプルで実用的なデータ管理が可能です。