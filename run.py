import os
from app import create_app
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

# アプリケーション作成
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('FLASK_PORT', 8000)),
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )