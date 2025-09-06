import pytest
import json
from app import create_app, db
from app.models.stock_data import StockData


@pytest.fixture
def app():
    """テスト用Flaskアプリケーション"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """テスト用クライアント"""
    return app.test_client()


@pytest.fixture
def sample_stock_data():
    """テスト用サンプルデータ"""
    return {
        'symbol': 'TEST.T',
        'company_name': 'Test Company',
        'current_price': 1500.0,
        'currency': 'JPY',
        'market_state': 'CLOSED',
        'timezone': 'JST',
        'exchange': 'Tokyo Stock Exchange',
        'historical_data': {
            'timestamps': [1609459200, 1609545600],
            'open': [1450.0, 1480.0],
            'high': [1520.0, 1550.0],
            'low': [1440.0, 1470.0],
            'close': [1500.0, 1520.0],
            'volume': [100000, 120000]
        }
    }


class TestMainRoutes:
    """メインルートのテスト"""
    
    def test_index_page(self, client):
        """インデックスページのテスト"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'株価データ取得システム' in response.data
    
    def test_health_check(self, client):
        """ヘルスチェックのテスト"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'stock-data-app'


class TestAPIRoutes:
    """APIルートのテスト"""
    
    def test_fetch_data_success(self, client):
        """データ取得APIの成功テスト"""
        payload = {'symbols': ['TEST.T', 'SAMPLE.T']}
        
        response = client.post('/api/fetch-data', 
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 202
        
        data = json.loads(response.data)
        assert 'task_id' in data
        assert data['symbols'] == ['TEST.T', 'SAMPLE.T']
        assert 'データ取得を開始しました' in data['message']
    
    def test_fetch_data_no_symbols(self, client):
        """シンボル未指定時のエラーテスト"""
        payload = {'symbols': []}
        
        response = client.post('/api/fetch-data',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'シンボルが指定されていません' in data['error']
    
    def test_get_stocks_empty(self, client):
        """空のデータ一覧取得テスト"""
        response = client.get('/api/stocks')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['stocks'] == []
        assert data['pagination']['total'] == 0
    
    def test_get_stocks_with_data(self, app, client, sample_stock_data):
        """データありの一覧取得テスト"""
        with app.app_context():
            # テストデータ作成
            stock = StockData(
                symbol=sample_stock_data['symbol'],
                company_name=sample_stock_data['company_name'],
                current_price=sample_stock_data['current_price'],
                currency=sample_stock_data['currency'],
                market_state=sample_stock_data['market_state'],
                timezone=sample_stock_data['timezone'],
                exchange=sample_stock_data['exchange'],
                historical_data=sample_stock_data['historical_data']
            )
            db.session.add(stock)
            db.session.commit()
        
        response = client.get('/api/stocks')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['stocks']) == 1
        assert data['stocks'][0]['symbol'] == 'TEST.T'
        assert data['pagination']['total'] == 1
    
    def test_get_stock_detail_not_found(self, client):
        """存在しないシンボルの詳細取得テスト"""
        response = client.get('/api/stocks/NOTEXIST.T')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert '指定されたシンボルのデータが見つかりません' in data['error']
    
    def test_get_stock_detail_success(self, app, client, sample_stock_data):
        """シンボル詳細取得成功テスト"""
        with app.app_context():
            # テストデータ作成
            stock = StockData(
                symbol=sample_stock_data['symbol'],
                company_name=sample_stock_data['company_name'],
                current_price=sample_stock_data['current_price'],
                currency=sample_stock_data['currency'],
                market_state=sample_stock_data['market_state'],
                timezone=sample_stock_data['timezone'],
                exchange=sample_stock_data['exchange'],
                historical_data=sample_stock_data['historical_data']
            )
            db.session.add(stock)
            db.session.commit()
        
        response = client.get('/api/stocks/TEST.T')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['symbol'] == 'TEST.T'
        assert data['company_name'] == 'Test Company'
        assert data['current_price'] == 1500.0
        assert 'historical_data' in data
    
    def test_pagination_parameters(self, client):
        """ページネーションパラメータのテスト"""
        response = client.get('/api/stocks?page=2&per_page=5')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['pagination']['page'] == 2
        assert data['pagination']['per_page'] == 5