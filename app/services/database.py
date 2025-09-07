from datetime import UTC, datetime
from typing import Dict, Optional

from sqlalchemy import desc

from app import db
from app.models.stock_data import StockData


class DatabaseService:
    """データベース操作サービス"""

    def save_stock_data(self, stock_data: Dict) -> bool:
        """株価データをデータベースに保存"""
        try:
            # 既存データの確認
            existing = StockData.query.filter_by(symbol=stock_data["symbol"]).first()

            if existing:
                # 既存データを更新
                existing.company_name = stock_data["company_name"]
                existing.current_price = stock_data["current_price"]
                existing.currency = stock_data["currency"]
                existing.market_state = stock_data["market_state"]
                existing.timezone = stock_data["timezone"]
                existing.exchange = stock_data["exchange"]
                existing.historical_data = stock_data["historical_data"]
                existing.updated_at = datetime.now(UTC)
            else:
                # 新規データを作成
                new_stock = StockData(
                    symbol=stock_data["symbol"],
                    company_name=stock_data["company_name"],
                    current_price=stock_data["current_price"],
                    currency=stock_data["currency"],
                    market_state=stock_data["market_state"],
                    timezone=stock_data["timezone"],
                    exchange=stock_data["exchange"],
                    historical_data=stock_data["historical_data"],
                )
                db.session.add(new_stock)

            db.session.commit()
            return True

        except Exception as e:
            db.session.rollback()
            print(f"データベース保存エラー: {e}")
            return False

    def get_stocks_paginated(self, page: int = 1, per_page: int = 12) -> Dict:
        """ページネーション付きで株価データを取得"""
        try:
            pagination = StockData.query.order_by(desc(StockData.updated_at)).paginate(
                page=page, per_page=per_page, error_out=False
            )

            items = []
            for stock in pagination.items:
                items.append(
                    {
                        "id": stock.id,
                        "symbol": stock.symbol,
                        "company_name": stock.company_name,
                        "current_price": stock.current_price,
                        "currency": stock.currency,
                        "market_state": stock.market_state,
                        "exchange": stock.exchange,
                        "updated_at": (
                            stock.updated_at.isoformat() if stock.updated_at else None
                        ),
                    }
                )

            return {
                "items": items,
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "pages": pagination.pages,
            }

        except Exception as e:
            print(f"データベース取得エラー: {e}")
            return {
                "items": [],
                "page": 1,
                "per_page": per_page,
                "total": 0,
                "pages": 0,
            }

    def get_stock_by_symbol(self, symbol: str) -> Optional[Dict]:
        """シンボルで株価データを取得"""
        try:
            stock = StockData.query.filter_by(symbol=symbol).first()

            if not stock:
                return None

            return {
                "id": stock.id,
                "symbol": stock.symbol,
                "company_name": stock.company_name,
                "current_price": stock.current_price,
                "currency": stock.currency,
                "market_state": stock.market_state,
                "timezone": stock.timezone,
                "exchange": stock.exchange,
                "historical_data": stock.historical_data,
                "created_at": (
                    stock.created_at.isoformat() if stock.created_at else None
                ),
                "updated_at": (
                    stock.updated_at.isoformat() if stock.updated_at else None
                ),
            }

        except Exception as e:
            print(f"データベース取得エラー: {e}")
            return None

    def delete_stock(self, symbol: str) -> bool:
        """株価データを削除"""
        try:
            stock = StockData.query.filter_by(symbol=symbol).first()

            if stock:
                db.session.delete(stock)
                db.session.commit()
                return True

            return False

        except Exception as e:
            db.session.rollback()
            print(f"データベース削除エラー: {e}")
            return False

    def get_stock_count(self) -> int:
        """保存されている株価データの総数を取得"""
        try:
            count: int = StockData.query.count()
            return count
        except Exception as e:
            print(f"データベースカウントエラー: {e}")
            return 0
