# Data Management Service 仕様書

## 1. サービス概要

### 1.1 役割
- PostgreSQLデータベースでのデータ操作
- 株価データの永続化・検索・削除
- データ整合性の保証
- データベースパフォーマンスの最適化

### 1.2 技術スタック
- **Framework**: FastAPI (将来) / Flask内モジュール (MVP)
- **Port**: 8002 (将来) / internal (MVP)
- **Dependencies**: SQLAlchemy, psycopg2-binary, alembic
- **Database**: PostgreSQL
- **Current Implementation**: `services/database.py` + `models/`

## 2. 内部API仕様（マイクロサービス時）

### 2.1 データ保存

#### POST /internal/save-stock-data
株価データの保存

**リクエスト:**
```http
POST /internal/save-stock-data HTTP/1.1
Content-Type: application/json

{
  "symbol": "7203.T",
  "mode": "overwrite",
  "data": [
    {
      "symbol": "7203.T",
      "date": "2024-01-15",
      "open": 2520.00,
      "high": 2580.50,
      "low": 2510.25,
      "close": 2530.75,
      "adj_close": 2530.75,
      "volume": 1250000
    }
  ]
}
```

**リクエストパラメータ:**
| パラメータ | 型 | 必須 | 説明 | 例 |
|-----------|---|------|------|---|
| symbol | string | ✅ | 銘柄コード | "7203.T" |
| mode | string | ✅ | 保存モード | "overwrite", "skip", "append" |
| data | array | ✅ | 株価データ配列 | StockData[] |

**レスポンス:**
```json
{
  "status": "success",
  "symbol": "7203.T",
  "records_processed": 252,
  "records_saved": 252,
  "records_skipped": 0,
  "records_updated": 0,
  "processing_time_ms": 1500,
  "date_range": {
    "start": "2023-01-15",
    "end": "2024-01-15"
  }
}
```

### 2.2 データ取得

#### GET /internal/stocks
株価データ一覧の取得

**リクエスト:**
```http
GET /internal/stocks?page=1&limit=50&symbol=7203.T&start_date=2024-01-01 HTTP/1.1
```

**クエリパラメータ:**
| パラメータ | 型 | 必須 | デフォルト | 説明 |
|-----------|---|------|-----------|------|
| page | integer | ❌ | 1 | ページ番号 |
| limit | integer | ❌ | 50 | 1ページあたりの件数 |
| symbol | string | ❌ | - | 銘柄コードフィルター |
| start_date | string | ❌ | - | 開始日フィルター |
| end_date | string | ❌ | - | 終了日フィルター |

**レスポンス:**
```json
{
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
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 1,
    "pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

#### GET /internal/stocks/{symbol}/data
特定銘柄の詳細データ取得

**リクエスト:**
```http
GET /internal/stocks/7203.T/data?start_date=2024-01-01&end_date=2024-01-31 HTTP/1.1
```

**レスポンス:**
```json
{
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
    }
  }
}
```

### 2.3 データ削除

#### DELETE /internal/stocks/{symbol}
特定銘柄のデータ削除

**リクエスト:**
```http
DELETE /internal/stocks/7203.T HTTP/1.1
```

**レスポンス:**
```json
{
  "status": "success",
  "symbol": "7203.T",
  "deleted_records": 252,
  "operation_time_ms": 150
}
```

### 2.4 ヘルスチェック

#### GET /internal/health
データベース接続状況確認

**レスポンス:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": {
    "status": "connected",
    "response_time_ms": 15,
    "connection_pool": {
      "active": 2,
      "idle": 8,
      "total": 10
    }
  },
  "metrics": {
    "total_symbols": 45,
    "total_records": 11340,
    "disk_usage_mb": 125
  }
}
```

## 3. データベース設計

### 3.1 テーブル定義

```sql
-- 株価データテーブル
CREATE TABLE stock_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(10,2),
    high DECIMAL(10,2),
    low DECIMAL(10,2),
    close DECIMAL(10,2),
    adj_close DECIMAL(10,2),
    volume BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- インデックス・制約
    UNIQUE(symbol, date),
    INDEX idx_symbol_date (symbol, date),
    INDEX idx_date (date),
    INDEX idx_symbol (symbol)
);

-- 銘柄マスタテーブル
CREATE TABLE stock_symbols (
    symbol VARCHAR(10) PRIMARY KEY,
    company_name VARCHAR(255),
    market VARCHAR(50),
    sector VARCHAR(100),
    industry VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_company_name (company_name)
);

-- 取得ログテーブル  
CREATE TABLE fetch_logs (
    id SERIAL PRIMARY KEY,
    fetch_id UUID NOT NULL,
    symbol VARCHAR(10),
    status VARCHAR(20) CHECK (status IN ('success', 'error', 'skipped')),
    error_message TEXT,
    records_count INTEGER,
    processing_time_ms INTEGER,
    fetch_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_fetch_id (fetch_id),
    INDEX idx_symbol_status (symbol, status),
    INDEX idx_fetch_date (fetch_date)
);
```

### 3.2 SQLAlchemy モデル定義

```python
# models/stock.py - データモデル定義
from sqlalchemy import Column, Integer, String, Date, DECIMAL, BigInteger, DateTime, Text, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional

Base = declarative_base()

class StockData(Base):
    __tablename__ = 'stock_data'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open = Column(DECIMAL(10, 2))
    high = Column(DECIMAL(10, 2))
    low = Column(DECIMAL(10, 2))
    close = Column(DECIMAL(10, 2))
    adj_close = Column(DECIMAL(10, 2))
    volume = Column(BigInteger)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint('symbol', 'date', name='unique_symbol_date'),
        Index('idx_symbol_date', 'symbol', 'date'),
    )
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
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

class StockSymbol(Base):
    __tablename__ = 'stock_symbols'
    
    symbol = Column(String(10), primary_key=True)
    company_name = Column(String(255), index=True)
    market = Column(String(50))
    sector = Column(String(100))
    industry = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class FetchLog(Base):
    __tablename__ = 'fetch_logs'
    
    id = Column(Integer, primary_key=True)
    fetch_id = Column(String(36), nullable=False, index=True)  # UUID
    symbol = Column(String(10), index=True)
    status = Column(String(20), CheckConstraint("status IN ('success', 'error', 'skipped')"))
    error_message = Column(Text)
    records_count = Column(Integer)
    processing_time_ms = Column(Integer)
    fetch_date = Column(DateTime, default=func.now(), index=True)
```

## 4. データベース操作実装

### 4.1 データ保存サービス

```python
# services/database.py - データベース操作実装
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
from models.stock import Base, StockData, StockSymbol, FetchLog
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime, date

class DatabaseService:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, pool_size=10, max_overflow=20)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.logger = logging.getLogger(__name__)
        
        # テーブル作成
        Base.metadata.create_all(bind=self.engine)
    
    async def save_stock_data(
        self, 
        symbol: str, 
        data: List[Dict], 
        mode: str = "overwrite"
    ) -> Dict:
        """
        株価データの保存
        
        Args:
            symbol: 銘柄コード
            data: 株価データのリスト
            mode: 保存モード ("overwrite", "skip", "append")
            
        Returns:
            保存結果
        """
        start_time = datetime.now()
        
        with self.SessionLocal() as session:
            try:
                # 既存データの処理
                if mode == "overwrite":
                    deleted_count = session.query(StockData).filter(
                        StockData.symbol == symbol
                    ).delete()
                    self.logger.info(f"Deleted {deleted_count} existing records for {symbol}")
                
                saved_count = 0
                skipped_count = 0
                updated_count = 0
                
                for record in data:
                    existing_record = None
                    
                    if mode != "overwrite":
                        existing_record = session.query(StockData).filter(
                            StockData.symbol == symbol,
                            StockData.date == record["date"]
                        ).first()
                    
                    if existing_record:
                        if mode == "skip":
                            skipped_count += 1
                            continue
                        elif mode == "append":
                            # 既存レコードを更新
                            for key, value in record.items():
                                if key != "symbol" and key != "date" and value is not None:
                                    setattr(existing_record, key, value)
                            existing_record.updated_at = datetime.now()
                            updated_count += 1
                    else:
                        # 新規レコード作成
                        stock_data = StockData(
                            symbol=record["symbol"],
                            date=datetime.strptime(record["date"], "%Y-%m-%d").date(),
                            open=record.get("open"),
                            high=record.get("high"),
                            low=record.get("low"),
                            close=record.get("close"),
                            adj_close=record.get("adj_close"),
                            volume=record.get("volume")
                        )
                        session.add(stock_data)
                        saved_count += 1
                
                session.commit()
                
                processing_time = (datetime.now() - start_time).total_seconds() * 1000
                
                # 日付範囲の計算
                date_range = self._get_date_range(session, symbol)
                
                return {
                    "status": "success",
                    "symbol": symbol,
                    "records_processed": len(data),
                    "records_saved": saved_count,
                    "records_skipped": skipped_count,
                    "records_updated": updated_count,
                    "processing_time_ms": int(processing_time),
                    "date_range": date_range
                }
                
            except Exception as e:
                session.rollback()
                self.logger.error(f"Error saving data for {symbol}: {str(e)}")
                raise
    
    async def get_stocks_list(
        self,
        page: int = 1,
        limit: int = 50,
        symbol: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict:
        """株価データ一覧の取得"""
        
        with self.SessionLocal() as session:
            # ベースクエリ
            query = session.query(StockData.symbol, func.count().label('data_count'))
            
            # フィルター条件
            if symbol:
                query = query.filter(StockData.symbol.ilike(f"%{symbol}%"))
            
            if start_date:
                query = query.filter(StockData.date >= start_date)
            
            if end_date:
                query = query.filter(StockData.date <= end_date)
            
            # グループ化とページング
            query = query.group_by(StockData.symbol)
            total = query.count()
            
            offset = (page - 1) * limit
            results = query.offset(offset).limit(limit).all()
            
            # 詳細情報の取得
            stocks = []
            for result in results:
                stock_info = self._get_stock_summary(session, result.symbol)
                stock_info["data_count"] = result.data_count
                stocks.append(stock_info)
            
            return {
                "stocks": stocks,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "pages": (total + limit - 1) // limit,
                    "has_next": page * limit < total,
                    "has_prev": page > 1
                }
            }
    
    async def get_stock_data(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        limit: int = 100
    ) -> Dict:
        """特定銘柄の詳細データ取得"""
        
        with self.SessionLocal() as session:
            # ベースクエリ
            query = session.query(StockData).filter(StockData.symbol == symbol)
            
            # 日付フィルター
            if start_date:
                query = query.filter(StockData.date >= start_date)
            if end_date:
                query = query.filter(StockData.date <= end_date)
            
            # 並び順
            query = query.order_by(StockData.date.desc())
            
            # ページング
            total = query.count()
            offset = (page - 1) * limit
            records = query.offset(offset).limit(limit).all()
            
            if not records:
                raise ValueError(f"No data found for symbol {symbol}")
            
            # 統計情報の計算
            summary_query = session.query(
                func.min(StockData.date).label('start'),
                func.max(StockData.date).label('end'),
                func.count().label('total_records'),
                func.max(StockData.high).label('highest'),
                func.min(StockData.low).label('lowest')
            ).filter(StockData.symbol == symbol)
            
            if start_date:
                summary_query = summary_query.filter(StockData.date >= start_date)
            if end_date:
                summary_query = summary_query.filter(StockData.date <= end_date)
            
            summary = summary_query.first()
            
            return {
                "symbol": symbol,
                "company_name": self._get_company_name(session, symbol),
                "price_data": [record.to_dict() for record in records],
                "summary": {
                    "period": {
                        "start": summary.start.isoformat() if summary.start else None,
                        "end": summary.end.isoformat() if summary.end else None
                    },
                    "total_records": summary.total_records,
                    "price_range": {
                        "high": float(summary.highest) if summary.highest else None,
                        "low": float(summary.lowest) if summary.lowest else None
                    }
                },
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "pages": (total + limit - 1) // limit,
                    "has_next": page * limit < total,
                    "has_prev": page > 1
                }
            }
    
    async def delete_stock_data(self, symbol: str) -> Dict:
        """特定銘柄のデータ削除"""
        start_time = datetime.now()
        
        with self.SessionLocal() as session:
            try:
                deleted_count = session.query(StockData).filter(
                    StockData.symbol == symbol
                ).delete()
                
                session.commit()
                
                processing_time = (datetime.now() - start_time).total_seconds() * 1000
                
                return {
                    "status": "success",
                    "symbol": symbol,
                    "deleted_records": deleted_count,
                    "operation_time_ms": int(processing_time)
                }
                
            except Exception as e:
                session.rollback()
                self.logger.error(f"Error deleting data for {symbol}: {str(e)}")
                raise
    
    def _get_stock_summary(self, session, symbol: str) -> Dict:
        """銘柄サマリー情報の取得"""
        
        # 最新データの取得
        latest = session.query(StockData).filter(
            StockData.symbol == symbol
        ).order_by(StockData.date.desc()).first()
        
        # 日付範囲の取得
        date_range = self._get_date_range(session, symbol)
        
        # 会社名の取得
        company_name = self._get_company_name(session, symbol)
        
        return {
            "symbol": symbol,
            "company_name": company_name,
            "date_range": date_range,
            "latest_close": float(latest.close) if latest and latest.close else None,
            "latest_date": latest.date.isoformat() if latest else None,
            "created_at": latest.created_at.isoformat() if latest else None,
            "updated_at": latest.updated_at.isoformat() if latest else None
        }
    
    def _get_date_range(self, session, symbol: str) -> Dict:
        """日付範囲の取得"""
        result = session.query(
            func.min(StockData.date).label('start'),
            func.max(StockData.date).label('end')
        ).filter(StockData.symbol == symbol).first()
        
        return {
            "start": result.start.isoformat() if result.start else None,
            "end": result.end.isoformat() if result.end else None
        }
    
    def _get_company_name(self, session, symbol: str) -> Optional[str]:
        """会社名の取得"""
        stock_symbol = session.query(StockSymbol).filter(
            StockSymbol.symbol == symbol
        ).first()
        
        return stock_symbol.company_name if stock_symbol else None
```

## 5. パフォーマンス最適化

### 5.1 インデックス戦略

```sql
-- パフォーマンス改善のためのインデックス
CREATE INDEX CONCURRENTLY idx_stock_data_symbol_date_desc ON stock_data (symbol, date DESC);
CREATE INDEX CONCURRENTLY idx_stock_data_date_range ON stock_data (date) WHERE date >= '2020-01-01';
CREATE INDEX CONCURRENTLY idx_fetch_logs_symbol_status_date ON fetch_logs (symbol, status, fetch_date);

-- パーティション化（大量データ対応）
CREATE TABLE stock_data_2024 PARTITION OF stock_data 
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

### 5.2 クエリ最適化

```python
# services/database.py - パフォーマンス最適化
class DatabaseService:
    
    async def bulk_insert_stock_data(self, data: List[Dict]) -> Dict:
        """バルクインサートによる高速データ挿入"""
        
        with self.SessionLocal() as session:
            try:
                # バルクインサート用のデータ準備
                bulk_data = []
                for record in data:
                    bulk_data.append({
                        'symbol': record['symbol'],
                        'date': datetime.strptime(record['date'], "%Y-%m-%d").date(),
                        'open': record.get('open'),
                        'high': record.get('high'),
                        'low': record.get('low'),
                        'close': record.get('close'),
                        'adj_close': record.get('adj_close'),
                        'volume': record.get('volume'),
                        'created_at': datetime.now(),
                        'updated_at': datetime.now()
                    })
                
                # バルクインサート実行
                session.bulk_insert_mappings(StockData, bulk_data)
                session.commit()
                
                return {"status": "success", "records_inserted": len(bulk_data)}
                
            except Exception as e:
                session.rollback()
                raise
    
    async def get_stock_data_cached(self, symbol: str, **kwargs) -> Dict:
        """キャッシュ機能付きデータ取得"""
        
        cache_key = f"stock_data:{symbol}:{hash(frozenset(kwargs.items()))}"
        
        # キャッシュから取得を試行（Redis使用時）
        # cached_result = await self.redis_client.get(cache_key)
        # if cached_result:
        #     return json.loads(cached_result)
        
        # データベースから取得
        result = await self.get_stock_data(symbol, **kwargs)
        
        # キャッシュに保存（5分間）
        # await self.redis_client.setex(cache_key, 300, json.dumps(result))
        
        return result
```

## 6. 現在のMVP実装

### 6.1 MVP時のファイル構造
```
services/
└── database.py         # 現在の実装ファイル
models/
└── stock.py           # SQLAlchemy モデル
```

### 6.2 マイクロサービス移行準備

```python
# services/database.py - 移行準備の実装
from abc import ABC, abstractmethod

class DataManagementServiceInterface(ABC):
    """Data Management Service インターフェース"""
    
    @abstractmethod
    async def save_stock_data(self, symbol: str, data: List[Dict], mode: str) -> Dict:
        pass
    
    @abstractmethod
    async def get_stocks_list(self, **kwargs) -> Dict:
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict:
        pass

class DatabaseService(DataManagementServiceInterface):
    """データベース操作実装（MVP時の内部実装）"""
    
    async def handle_request(self, endpoint: str, method: str, data: dict):
        """統一リクエストハンドラ（将来のHTTP API用）"""
        
        if endpoint == '/internal/save-stock-data' and method == 'POST':
            return await self.save_stock_data(
                data['symbol'], data['data'], data['mode']
            )
        
        elif endpoint == '/internal/stocks' and method == 'GET':
            return await self.get_stocks_list(**data)
        
        elif endpoint.startswith('/internal/stocks/') and method == 'GET':
            symbol = endpoint.split('/')[-2]  # Extract symbol from path
            return await self.get_stock_data(symbol, **data)
        
        elif endpoint.startswith('/internal/stocks/') and method == 'DELETE':
            symbol = endpoint.split('/')[-1]
            return await self.delete_stock_data(symbol)
        
        elif endpoint == '/internal/health' and method == 'GET':
            return await self.health_check()
        
        else:
            raise ValueError(f"Unknown endpoint: {endpoint}")
```

---

## まとめ

このData Management Service仕様書では：

### ✅ **現在のMVP対応**
- `services/database.py` + `models/` での実装
- SQLAlchemy による ORM
- PostgreSQL データベース操作

### 🚀 **将来のマイクロサービス対応**
- FastAPI による独立サービス化準備
- 統一されたAPI設計
- キャッシュとパフォーマンス最適化

### 🛡️ **データ整合性・信頼性**
- トランザクション処理
- エラーハンドリング
- データベース制約の活用

この設計により、安全で高パフォーマンスなデータ管理を実現し、将来の拡張に対応できます。