from flask import Blueprint, render_template

main = Blueprint('main', __name__)


@main.route('/')
def index():
    """フロントエンドページの配信"""
    return render_template('index.html')


@main.route('/health')
def health_check():
    """ヘルスチェックエンドポイント"""
    return {'status': 'healthy', 'service': 'stock-data-app'}, 200