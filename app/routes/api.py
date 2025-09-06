from flask import Blueprint, jsonify, request
from app.services.yahoo_finance import YahooFinanceService
from app.services.database import DatabaseService
from app.services.progress import ProgressService

api = Blueprint('api', __name__)

# サービスのインスタンス化
yahoo_service = YahooFinanceService()
db_service = DatabaseService()
progress_service = ProgressService()


@api.route('/fetch-data', methods=['POST'])
def fetch_stock_data():
    """株価データ取得API"""
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        
        if not symbols:
            return jsonify({'error': 'シンボルが指定されていません'}), 400
            
        # 非同期でデータ取得開始
        task_id = yahoo_service.fetch_multiple_symbols(symbols)
        
        return jsonify({
            'message': 'データ取得を開始しました',
            'task_id': task_id,
            'symbols': symbols
        }), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/fetch-status/<task_id>')
def get_fetch_status(task_id):
    """データ取得状況確認API"""
    try:
        status = progress_service.get_status(task_id)
        return jsonify(status), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/stocks')
def get_stocks():
    """取得済み株価データ一覧API"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        
        stocks = db_service.get_stocks_paginated(page, per_page)
        
        return jsonify({
            'stocks': stocks['items'],
            'pagination': {
                'page': stocks['page'],
                'per_page': stocks['per_page'],
                'total': stocks['total'],
                'pages': stocks['pages']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/stocks/<symbol>')
def get_stock_detail(symbol):
    """個別株価データ詳細API"""
    try:
        stock_data = db_service.get_stock_by_symbol(symbol)
        
        if not stock_data:
            return jsonify({'error': '指定されたシンボルのデータが見つかりません'}), 404
            
        return jsonify(stock_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500