from app import db
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import JSON


class StockData(db.Model):
    """株価データモデル"""
    
    __tablename__ = 'stock_data'
    
    # 主キー
    id = db.Column(db.Integer, primary_key=True)
    
    # 基本情報
    symbol = db.Column(db.String(20), unique=True, nullable=False, index=True)
    company_name = db.Column(db.String(200), nullable=False)
    
    # 現在価格情報
    current_price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False, default='JPY')
    
    # マーケット情報
    market_state = db.Column(db.String(20), nullable=True)
    timezone = db.Column(db.String(50), nullable=True)
    exchange = db.Column(db.String(100), nullable=True)
    
    # 履歴データ（JSON形式）
    historical_data = db.Column(JSON, nullable=True)
    
    # タイムスタンプ
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<StockData {self.symbol}: {self.company_name}>'
    
    def to_dict(self):
        """辞書形式でデータを返す"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'company_name': self.company_name,
            'current_price': self.current_price,
            'currency': self.currency,
            'market_state': self.market_state,
            'timezone': self.timezone,
            'exchange': self.exchange,
            'historical_data': self.historical_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class FetchLog(db.Model):
    """データ取得ログモデル"""
    
    __tablename__ = 'fetch_logs'
    
    # 主キー
    id = db.Column(db.Integer, primary_key=True)
    
    # タスク情報
    task_id = db.Column(db.String(36), nullable=False, index=True)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    
    # 実行状況
    status = db.Column(db.String(20), nullable=False)  # success, error, pending
    message = db.Column(db.Text, nullable=True)
    error_detail = db.Column(db.Text, nullable=True)
    
    # 実行時間
    started_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # 取得データへのリンク
    stock_data_id = db.Column(db.Integer, db.ForeignKey('stock_data.id'), nullable=True)
    stock_data = db.relationship('StockData', backref=db.backref('fetch_logs', lazy=True))
    
    def __repr__(self):
        return f'<FetchLog {self.task_id}: {self.symbol} - {self.status}>'
    
    def to_dict(self):
        """辞書形式でデータを返す"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'symbol': self.symbol,
            'status': self.status,
            'message': self.message,
            'error_detail': self.error_detail,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'stock_data_id': self.stock_data_id
        }