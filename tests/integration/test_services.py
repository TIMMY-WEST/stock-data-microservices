import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from app import create_app, db
from app.models.stock_data import StockData
from app.services.database import DatabaseService
from app.services.progress import ProgressService
from app.services.yahoo_finance import YahooFinanceService


@pytest.fixture
def app():
    """テスト用Flaskアプリケーション"""
    app = create_app("testing")

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def sample_yahoo_response():
    """Yahoo Finance APIレスポンスのモック"""
    return {
        "chart": {
            "result": [
                {
                    "meta": {
                        "symbol": "TEST.T",
                        "longName": "Test Company Ltd.",
                        "regularMarketPrice": 1500.0,
                        "currency": "JPY",
                        "marketState": "CLOSED",
                        "timezone": "JST",
                        "exchangeName": "Tokyo Stock Exchange",
                    },
                    "timestamp": [1609459200, 1609545600],
                    "indicators": {
                        "quote": [
                            {
                                "open": [1450.0, 1480.0],
                                "high": [1520.0, 1550.0],
                                "low": [1440.0, 1470.0],
                                "close": [1500.0, 1520.0],
                                "volume": [100000, 120000],
                            }
                        ]
                    },
                }
            ]
        }
    }


class TestYahooFinanceService:
    """Yahoo Finance サービスのテスト"""

    @patch("app.services.yahoo_finance.requests.get")
    def test_fetch_stock_data_success(self, mock_get, sample_yahoo_response):
        """株価データ取得成功テスト"""
        # リクエストモックの設定
        mock_response = Mock()
        mock_response.json.return_value = sample_yahoo_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = YahooFinanceService()
        result = service.fetch_stock_data("TEST.T")

        assert result is not None
        assert result["symbol"] == "TEST.T"
        assert result["company_name"] == "Test Company Ltd."
        assert result["current_price"] == 1500.0
        assert result["currency"] == "JPY"
        assert "historical_data" in result

        # APIが正しく呼ばれたか確認
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "TEST.T" in args[0]

    @patch("app.services.yahoo_finance.requests.get")
    def test_fetch_stock_data_api_error(self, mock_get):
        """APIエラー時のテスト"""
        mock_get.side_effect = Exception("Network error")

        service = YahooFinanceService()
        result = service.fetch_stock_data("INVALID")

        assert result is None

    @patch("app.services.yahoo_finance.requests.get")
    def test_validate_symbol_success(self, mock_get):
        """シンボル検証成功テスト"""
        mock_response = Mock()
        mock_response.json.return_value = {"quotes": [{"symbol": "TEST.T"}]}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = YahooFinanceService()
        result = service.validate_symbol("TEST.T")

        assert result is True

    @patch("app.services.yahoo_finance.requests.get")
    def test_validate_symbol_not_found(self, mock_get):
        """シンボル検証失敗テスト"""
        mock_response = Mock()
        mock_response.json.return_value = {"quotes": []}  # 空の結果
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = YahooFinanceService()
        result = service.validate_symbol("INVALID")

        assert result is False


class TestDatabaseService:
    """データベースサービスのテスト"""

    def test_save_stock_data_new(self, app):
        """新規データ保存テスト"""
        with app.app_context():
            service = DatabaseService()

            stock_data = {
                "symbol": "NEW.T",
                "company_name": "New Company",
                "current_price": 2000.0,
                "currency": "JPY",
                "market_state": "OPEN",
                "timezone": "JST",
                "exchange": "Tokyo",
                "historical_data": {"test": "data"},
            }

            result = service.save_stock_data(stock_data)
            assert result is True

            # データベースに保存されたか確認
            saved = StockData.query.filter_by(symbol="NEW.T").first()
            assert saved is not None
            assert saved.company_name == "New Company"
            assert saved.current_price == 2000.0

    def test_save_stock_data_update(self, app):
        """既存データ更新テスト"""
        with app.app_context():
            # 既存データを作成
            existing = StockData(
                symbol="UPDATE.T",
                company_name="Old Company",
                current_price=1000.0,
                currency="JPY",
            )
            db.session.add(existing)
            db.session.commit()

            service = DatabaseService()

            # 更新データ
            stock_data = {
                "symbol": "UPDATE.T",
                "company_name": "Updated Company",
                "current_price": 1100.0,
                "currency": "JPY",
                "market_state": "CLOSED",
                "timezone": "JST",
                "exchange": "Tokyo",
                "historical_data": {"updated": "data"},
            }

            result = service.save_stock_data(stock_data)
            assert result is True

            # 更新されたか確認
            updated = StockData.query.filter_by(symbol="UPDATE.T").first()
            assert updated.company_name == "Updated Company"
            assert updated.current_price == 1100.0

    def test_get_stocks_paginated(self, app):
        """ページネーション取得テスト"""
        with app.app_context():
            # テストデータ作成
            for i in range(15):
                stock = StockData(
                    symbol=f"TEST{i}.T",
                    company_name=f"Company {i}",
                    current_price=1000.0 + i,
                    currency="JPY",
                )
                db.session.add(stock)
            db.session.commit()

            service = DatabaseService()

            # 1ページ目取得（per_page=10）
            result = service.get_stocks_paginated(page=1, per_page=10)

            assert len(result["items"]) == 10
            assert result["total"] == 15
            assert result["pages"] == 2
            assert result["page"] == 1

    def test_get_stock_by_symbol(self, app):
        """シンボル検索テスト"""
        with app.app_context():
            # テストデータ作成
            stock = StockData(
                symbol="SEARCH.T",
                company_name="Search Company",
                current_price=1500.0,
                currency="JPY",
            )
            db.session.add(stock)
            db.session.commit()

            service = DatabaseService()

            # 存在するシンボル
            result = service.get_stock_by_symbol("SEARCH.T")
            assert result is not None
            assert result["symbol"] == "SEARCH.T"
            assert result["company_name"] == "Search Company"

            # 存在しないシンボル
            result = service.get_stock_by_symbol("NOTFOUND.T")
            assert result is None

    def test_delete_stock(self, app):
        """株価データ削除テスト"""
        with app.app_context():
            # テストデータ作成
            stock = StockData(
                symbol="DELETE.T",
                company_name="Delete Company",
                current_price=1000.0,
                currency="JPY",
            )
            db.session.add(stock)
            db.session.commit()

            service = DatabaseService()

            # 削除実行
            result = service.delete_stock("DELETE.T")
            assert result is True

            # 削除されたか確認
            deleted = StockData.query.filter_by(symbol="DELETE.T").first()
            assert deleted is None

            # 存在しないデータの削除
            result = service.delete_stock("NOTEXIST.T")
            assert result is False


class TestProgressService:
    """プログレスサービスのテスト"""

    def test_initialize_task(self):
        """タスク初期化テスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 一時ファイルを使用
            progress_file = os.path.join(tmpdir, "test_progress.json")

            service = ProgressService()
            service.progress_file = progress_file

            service.initialize_task("test-123", 5)

            # タスクが作成されたか確認
            status = service.get_status("test-123")
            assert status is not None
            assert status["status"] == "running"
            assert status["total"] == 5
            assert status["progress"] == 0

    def test_update_progress(self):
        """プログレス更新テスト"""
        service = ProgressService()
        service.initialize_task("test-456", 10)

        # プログレス更新
        result = service.update_progress("test-456", 3, "3件完了")
        assert result is True

        # 更新結果確認
        status = service.get_status("test-456")
        assert status["current_item"] == 3
        assert status["progress"] == 30  # 3/10 * 100
        assert status["message"] == "3件完了"

    def test_complete_task(self):
        """タスク完了テスト"""
        service = ProgressService()
        service.initialize_task("test-789", 5)

        # タスク完了
        result = service.complete_task("test-789")
        assert result is True

        # 完了状態確認
        status = service.get_status("test-789")
        assert status["status"] == "completed"
        assert status["progress"] == 100
        assert status["completed_at"] is not None

    def test_error_task(self):
        """タスクエラーテスト"""
        service = ProgressService()
        service.initialize_task("test-error", 5)

        # エラー設定
        result = service.error_task("test-error", "テストエラー")
        assert result is True

        # エラー状態確認
        status = service.get_status("test-error")
        assert status["status"] == "error"
        assert status["error"] == "テストエラー"

    def test_get_status_not_found(self):
        """存在しないタスク取得テスト"""
        service = ProgressService()

        status = service.get_status("not-exist")
        assert status is None
