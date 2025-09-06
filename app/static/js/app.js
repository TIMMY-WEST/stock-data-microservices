// Alpine.js アプリケーション
function stockApp() {
    return {
        // 状態管理
        symbolInput: '',
        stocks: [],
        pagination: null,
        currentTask: null,
        isLoading: false,
        isLoadingData: false,
        
        // 初期化
        async init() {
            console.log('📈 株価データアプリを初期化中...');
            await this.refreshData();
        },
        
        // データ取得開始
        async fetchData() {
            if (!this.symbolInput.trim()) {
                this.showAlert('シンボルを入力してください', 'error');
                return;
            }
            
            this.isLoading = true;
            
            try {
                // シンボルをパース
                const symbols = this.symbolInput.split(',').map(s => s.trim().toUpperCase()).filter(s => s);
                
                console.log('📊 データ取得開始:', symbols);
                
                const response = await fetch('/api/fetch-data', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ symbols })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const data = await response.json();
                console.log('✅ データ取得タスク開始:', data);
                
                this.showAlert(`${symbols.length}件のシンボルのデータ取得を開始しました`, 'success');
                
                // プログレス監視開始
                await this.monitorProgress(data.task_id);
                
            } catch (error) {
                console.error('❌ データ取得エラー:', error);
                this.showAlert(`データ取得エラー: ${error.message}`, 'error');
            } finally {
                this.isLoading = false;
            }
        },
        
        // プログレス監視
        async monitorProgress(taskId) {
            const monitorInterval = setInterval(async () => {
                try {
                    const response = await fetch(`/api/fetch-status/${taskId}`);
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    const status = await response.json();
                    this.currentTask = status;
                    
                    console.log('📊 プログレス更新:', status);
                    
                    // タスク完了確認
                    if (status.status === 'completed') {
                        clearInterval(monitorInterval);
                        this.showAlert('データ取得が完了しました！', 'success');
                        await this.refreshData();
                        this.currentTask = null;
                    } else if (status.status === 'error') {
                        clearInterval(monitorInterval);
                        this.showAlert(`データ取得エラー: ${status.error}`, 'error');
                        this.currentTask = null;
                    }
                    
                } catch (error) {
                    console.error('❌ プログレス取得エラー:', error);
                    clearInterval(monitorInterval);
                    this.currentTask = null;
                }
            }, 2000); // 2秒間隔で確認
            
            // 5分でタイムアウト
            setTimeout(() => {
                clearInterval(monitorInterval);
                if (this.currentTask && this.currentTask.status === 'running') {
                    this.showAlert('データ取得がタイムアウトしました', 'error');
                    this.currentTask = null;
                }
            }, 300000);
        },
        
        // データ一覧更新
        async refreshData(page = 1) {
            this.isLoadingData = true;
            
            try {
                console.log(`📋 データ一覧を取得中... (ページ: ${page})`);
                
                const response = await fetch(`/api/stocks?page=${page}&per_page=12`);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const data = await response.json();
                this.stocks = data.stocks;
                this.pagination = data.pagination;
                
                console.log('✅ データ一覧取得完了:', data);
                
            } catch (error) {
                console.error('❌ データ取得エラー:', error);
                this.showAlert(`データ取得エラー: ${error.message}`, 'error');
            } finally {
                this.isLoadingData = false;
            }
        },
        
        // ページ変更
        async loadPage(page) {
            if (page < 1 || (this.pagination && page > this.pagination.pages)) {
                return;
            }
            await this.refreshData(page);
        },
        
        // ページ番号生成
        getPageNumbers() {
            if (!this.pagination) return [];
            
            const current = this.pagination.page;
            const total = this.pagination.pages;
            const pages = [];
            
            // 最大5ページ表示
            let start = Math.max(1, current - 2);
            let end = Math.min(total, start + 4);
            
            if (end - start < 4) {
                start = Math.max(1, end - 4);
            }
            
            for (let i = start; i <= end; i++) {
                pages.push(i);
            }
            
            return pages;
        },
        
        // 日時フォーマット
        formatDate(dateString) {
            if (!dateString) return '未設定';
            
            try {
                const date = new Date(dateString);
                return date.toLocaleString('ja-JP', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit'
                });
            } catch (error) {
                return '無効な日時';
            }
        },
        
        // アラート表示
        showAlert(message, type = 'info') {
            // 簡易アラート実装（実際にはよりリッチなUI実装を推奨）
            const alertClass = {
                'success': '✅',
                'error': '❌',
                'info': 'ℹ️',
                'warning': '⚠️'
            };
            
            console.log(`${alertClass[type] || 'ℹ️'} ${message}`);
            
            // ブラウザネイティブのアラート（実際の実装ではtoastライブラリ等を使用）
            if (type === 'error') {
                alert(`エラー: ${message}`);
            } else if (type === 'success') {
                // 成功メッセージは控えめに
                console.log(`成功: ${message}`);
            }
        },
        
        // エラーハンドリング
        handleError(error, context = 'unknown') {
            console.error(`❌ エラー (${context}):`, error);
            
            let message = '予期しないエラーが発生しました';
            
            if (error.name === 'NetworkError') {
                message = 'ネットワークエラー: サーバーに接続できません';
            } else if (error.message) {
                message = error.message;
            }
            
            this.showAlert(message, 'error');
        }
    };
}

// ページ読み込み完了後の初期化
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 ページ読み込み完了 - Alpine.js初期化待機中');
});

// グローバルエラーハンドラー
window.addEventListener('error', function(event) {
    console.error('🔥 グローバルエラー:', event.error);
});

// 未処理のPromise拒否
window.addEventListener('unhandledrejection', function(event) {
    console.error('🔥 未処理のPromise拒否:', event.reason);
    event.preventDefault();
});

// デバッグ用関数
window.debugApp = {
    getAppState: () => {
        const app = document.getElementById('app');
        return app ? app._x_dataStack : 'アプリが見つかりません';
    },
    
    testAPI: async (endpoint, options = {}) => {
        try {
            const response = await fetch(`/api/${endpoint}`, options);
            const data = await response.json();
            console.log('🔍 API テスト結果:', data);
            return data;
        } catch (error) {
            console.error('🔍 API テストエラー:', error);
            return null;
        }
    }
};