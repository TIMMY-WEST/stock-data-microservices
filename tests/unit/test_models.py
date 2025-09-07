"""
単体テスト: モデルクラスのテスト
外部依存関係なし（データベース接続なし）
"""
from datetime import datetime
from unittest.mock import Mock

from app.models.stock_data import StockData


class TestStockData:
    """StockDataモデルの単体テスト"""

    def test_init(self):
        """初期化テスト"""
        stock_data = StockData(
            symbol="TEST.T",
            company_name="Test Company",
            current_price=1500.0,
            currency="JPY"
        )
        
        assert stock_data.symbol == "TEST.T"
        assert stock_data.company_name == "Test Company"
        assert stock_data.current_price == 1500.0
        assert stock_data.currency == "JPY"

    def test_to_dict(self):
        """辞書形式変換テスト"""
        stock_data = StockData(
            symbol="TEST.T",
            company_name="Test Company",
            current_price=1500.0,
            currency="JPY",
            market_state="CLOSED",
            timezone="JST",
            exchange="TSE"
        )
        
        result = stock_data.to_dict()
        
        assert isinstance(result, dict)
        assert result["symbol"] == "TEST.T"
        assert result["company_name"] == "Test Company"
        assert result["current_price"] == 1500.0
        assert result["currency"] == "JPY"

    def test_repr(self):
        """文字列表現テスト"""
        stock_data = StockData(symbol="TEST.T")
        result = repr(stock_data)
        assert "TEST.T" in result