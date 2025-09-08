from typing import Any, Dict, Tuple

from flask import Blueprint, render_template

main = Blueprint("main", __name__)


@main.route("/")
def index() -> str:
    """フロントエンドページの配信"""
    return render_template("index.html")


@main.route("/health")
def health_check() -> Tuple[Dict[str, Any], int]:
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy", "service": "stock-data-app"}, 200
