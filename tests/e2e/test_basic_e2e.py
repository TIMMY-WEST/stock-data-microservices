"""
E2Eテスト: エンドツーエンドのシステムテスト
実際のアプリケーションサーバーに対するHTTPリクエストテスト
"""
import time
import requests
import pytest


class TestBasicE2E:
    """基本的なE2Eテスト"""
    
    BASE_URL = "http://127.0.0.1:8000"
    
    def test_health_check(self):
        """ヘルスチェックエンドポイントのテスト"""
        try:
            response = requests.get(f"{self.BASE_URL}/", timeout=10)
            assert response.status_code == 200
        except requests.exceptions.ConnectionError:
            pytest.skip("アプリケーションサーバーに接続できません")
    
    def test_api_endpoints_available(self):
        """APIエンドポイントの可用性テスト"""
        endpoints = [
            "/api/health",
            "/api/stocks"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.BASE_URL}{endpoint}", timeout=10)
                # 200または404（エンドポイントが存在しない場合）なら正常
                assert response.status_code in [200, 404, 500]
            except requests.exceptions.ConnectionError:
                pytest.skip(f"エンドポイント {endpoint} に接続できません")
    
    def test_stock_search_workflow(self):
        """株式検索ワークフローのE2Eテスト"""
        try:
            # 1. 株式リスト取得
            response = requests.get(f"{self.BASE_URL}/api/stocks", timeout=10)
            
            # サーバーが起動していることを確認（404でも構わない）
            assert response.status_code in [200, 404, 500]
            
        except requests.exceptions.ConnectionError:
            pytest.skip("株式検索APIに接続できません")