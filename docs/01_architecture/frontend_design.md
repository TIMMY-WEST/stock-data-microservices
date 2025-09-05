# フロントエンド設計書 (Alpine.js + Tailwind CSS版)

## 1. 設計概要

### 1.1 設計方針
- **macOS風デザイン**: Apple Human Interface Guidelines準拠
- **レスポンシブ**: モバイル・タブレット・デスクトップ対応
- **シンプル構成**: CDN利用でビルドプロセス不要
- **アクセシブル**: 基本的なアクセシビリティ確保

### 1.2 技術スタック
- **JavaScript Framework**: Alpine.js 3.x (CDN)
- **CSS Framework**: Tailwind CSS 3.x (CDN)
- **Icons**: Heroicons (Tailwind公式)
- **Fonts**: システムフォント (San Francisco風)
- **Build Process**: なし（CDN利用）

### 1.3 ブラウザ対応
- **Chrome**: 90+
- **Firefox**: 90+
- **Safari**: 14+
- **Edge**: 90+

## 2. デザインシステム

### 2.1 カラーパレット（macOS風）

```css
:root {
  /* Primary Colors */
  --color-primary: #007AFF;        /* System Blue */
  --color-primary-dark: #0056D6;   /* Darker Blue */
  
  /* Background Colors */
  --color-bg-primary: #FFFFFF;     /* White */
  --color-bg-secondary: #F5F5F7;   /* Light Gray */
  --color-bg-tertiary: #E5E5EA;    /* Mid Gray */
  
  /* Text Colors */
  --color-text-primary: #1D1D1F;   /* Nearly Black */
  --color-text-secondary: #86868B; /* Mid Gray */
  --color-text-tertiary: #C7C7CC;  /* Light Gray */
  
  /* Status Colors */
  --color-success: #30D158;        /* Green */
  --color-error: #FF3B30;          /* Red */
  --color-warning: #FF9500;        /* Orange */
  
  /* Surface Colors */
  --color-card: rgba(255, 255, 255, 0.8);
  --color-overlay: rgba(0, 0, 0, 0.4);
}
```

### 2.2 タイポグラフィ

```css
/* Font Stack (San Francisco風) */
.font-system {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 
               Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
}

/* Text Sizes */
.text-display {    font-size: 3rem; font-weight: 700; line-height: 1.1; }
.text-headline {   font-size: 2rem; font-weight: 600; line-height: 1.2; }
.text-title {      font-size: 1.5rem; font-weight: 600; line-height: 1.3; }
.text-body {       font-size: 1rem; font-weight: 400; line-height: 1.5; }
.text-caption {    font-size: 0.875rem; font-weight: 400; line-height: 1.4; }
.text-footnote {   font-size: 0.75rem; font-weight: 400; line-height: 1.3; }
```

### 2.3 Spacing & Layout

```css
/* Spacing Scale */
.space-xs { margin: 0.25rem; }    /* 4px */
.space-sm { margin: 0.5rem; }     /* 8px */
.space-md { margin: 1rem; }       /* 16px */
.space-lg { margin: 1.5rem; }     /* 24px */
.space-xl { margin: 2rem; }       /* 32px */
.space-2xl { margin: 3rem; }      /* 48px */

/* Border Radius */
.rounded-card { border-radius: 12px; }
.rounded-button { border-radius: 8px; }
.rounded-input { border-radius: 6px; }
```

## 3. UI コンポーネント設計

### 3.1 基本コンポーネント

#### 3.1.1 Button Components

```html
<!-- Primary Button -->
<button class="btn-primary" type="button">
  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
  </svg>
  データ取得開始
</button>

<!-- Secondary Button -->  
<button class="btn-secondary" type="button">
  キャンセル
</button>

<!-- Danger Button -->
<button class="btn-danger" type="button">
  削除
</button>

<style>
/* Button Base Styles */
.btn-base {
  @apply px-4 py-2 rounded-button font-medium transition-all duration-200 
         focus:outline-none focus:ring-2 focus:ring-offset-2
         inline-flex items-center justify-center;
}

.btn-primary {
  @apply btn-base bg-blue-500 hover:bg-blue-600 text-white
         focus:ring-blue-500 transform hover:scale-105
         shadow-lg hover:shadow-xl;
}

.btn-secondary {
  @apply btn-base bg-gray-100 hover:bg-gray-200 text-gray-900
         focus:ring-gray-500;
}

.btn-danger {
  @apply btn-base bg-red-500 hover:bg-red-600 text-white
         focus:ring-red-500;
}
</style>
```

#### 3.1.2 Input Components

```html
<!-- Text Input -->
<div class="input-group">
  <label class="input-label" for="symbol">銘柄コード</label>
  <input 
    class="input-field" 
    type="text" 
    id="symbol" 
    placeholder="例: 7203.T"
    x-model="symbol">
  <p class="input-help">東証銘柄コードを入力してください</p>
</div>

<!-- Select Input -->
<div class="input-group">
  <label class="input-label" for="period">取得期間</label>
  <select class="input-field" id="period" x-model="period">
    <option value="1y">過去1年</option>
    <option value="5y">過去5年</option>
    <option value="max">全期間</option>
  </select>
</div>

<style>
.input-group {
  @apply mb-4;
}

.input-label {
  @apply block text-sm font-medium text-gray-700 mb-1;
}

.input-field {
  @apply w-full px-3 py-2 border border-gray-300 rounded-input
         focus:outline-none focus:ring-2 focus:ring-blue-500 
         focus:border-transparent transition-all duration-200
         bg-white text-gray-900;
}

.input-help {
  @apply mt-1 text-sm text-gray-500;
}

.input-error {
  @apply mt-1 text-sm text-red-600;
}
</style>
```

#### 3.1.3 Card Components

```html
<!-- Basic Card -->
<div class="card">
  <div class="card-header">
    <h3 class="card-title">トヨタ自動車 (7203.T)</h3>
    <span class="card-badge">252件</span>
  </div>
  <div class="card-body">
    <p class="text-sm text-gray-600">2024/01/01 〜 2024/12/31</p>
    <div class="mt-4 flex space-x-2">
      <button class="btn-secondary btn-sm">詳細</button>
      <button class="btn-danger btn-sm">削除</button>
    </div>
  </div>
</div>

<style>
.card {
  @apply bg-white rounded-card shadow-md border border-gray-100
         hover:shadow-lg transition-all duration-200 overflow-hidden;
}

.card-header {
  @apply px-4 py-3 border-b border-gray-100 flex items-center justify-between;
}

.card-title {
  @apply text-lg font-semibold text-gray-900;
}

.card-badge {
  @apply px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full;
}

.card-body {
  @apply p-4;
}

.btn-sm {
  @apply px-3 py-1 text-sm;
}
</style>
```

### 3.2 プログレスバーコンポーネント

```html
<!-- Progress Bar -->
<div x-show="isLoading" class="progress-container">
  <div class="progress-header">
    <h4 class="progress-title">データ取得中...</h4>
    <span class="progress-percentage" x-text="`${progress}%`"></span>
  </div>
  
  <div class="progress-bar">
    <div class="progress-fill" :style="`width: ${progress}%`"></div>
  </div>
  
  <p class="progress-status" x-text="currentStatus"></p>
</div>

<style>
.progress-container {
  @apply mb-6 p-4 bg-blue-50 rounded-card border border-blue-200;
}

.progress-header {
  @apply flex justify-between items-center mb-2;
}

.progress-title {
  @apply text-sm font-medium text-blue-900;
}

.progress-percentage {
  @apply text-sm font-bold text-blue-600;
}

.progress-bar {
  @apply w-full bg-blue-200 rounded-full h-2 mb-2;
}

.progress-fill {
  @apply bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full 
         transition-all duration-300 ease-out;
}

.progress-status {
  @apply text-xs text-blue-700;
}
</style>
```

## 4. Alpine.js 設計

### 4.1 メインアプリケーション

```html
<!-- app/templates/index.html -->
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Data Manager</title>
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Tailwind Config -->
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        'system': ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif']
                    },
                    colors: {
                        'primary': '#007AFF',
                        'success': '#30D158',
                        'error': '#FF3B30',
                        'warning': '#FF9500'
                    }
                }
            }
        }
    </script>
    
    <!-- Alpine.js -->
    <script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
</head>

<body class="bg-gray-50 font-system" x-data="stockApp()">
    <!-- App Container -->
    <div class="min-h-screen">
        <!-- Header -->
        <header class="bg-white shadow-sm border-b border-gray-200">
            <div class="max-w-6xl mx-auto px-4 py-4">
                <h1 class="text-2xl font-bold text-gray-900 flex items-center">
                    🏦 Stock Data Manager
                </h1>
            </div>
        </header>
        
        <!-- Main Content -->
        <main class="max-w-6xl mx-auto px-4 py-8 space-y-8">
            <!-- Data Fetch Section -->
            <section class="bg-white rounded-card shadow-md p-6">
                <h2 class="text-xl font-semibold text-gray-900 mb-6">データ取得</h2>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <!-- Symbol Input -->
                    <div class="input-group">
                        <label class="input-label" for="symbol">銘柄コード</label>
                        <input 
                            class="input-field" 
                            type="text" 
                            id="symbol" 
                            placeholder="例: 7203.T"
                            x-model="formData.symbol"
                            :disabled="isLoading">
                    </div>
                    
                    <!-- Period Select -->
                    <div class="input-group">
                        <label class="input-label" for="period">取得期間</label>
                        <select class="input-field" id="period" x-model="formData.period" :disabled="isLoading">
                            <option value="1y">過去1年</option>
                            <option value="5y">過去5年</option>
                            <option value="max">全期間</option>
                        </select>
                    </div>
                </div>
                
                <!-- Action Button -->
                <div class="mt-6">
                    <button 
                        class="btn-primary"
                        @click="fetchStockData()"
                        :disabled="isLoading || !formData.symbol.trim()">
                        
                        <svg x-show="!isLoading" class="w-4 h-4 mr-2" fill="none" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"/>
                        </svg>
                        
                        <svg x-show="isLoading" class="animate-spin w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24">
                            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" class="opacity-25"/>
                            <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" class="opacity-75"/>
                        </svg>
                        
                        <span x-text="isLoading ? '取得中...' : 'データ取得開始'"></span>
                    </button>
                </div>
                
                <!-- Error Display -->
                <div x-show="error" class="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                    <p class="text-sm text-red-800" x-text="error"></p>
                </div>
            </section>
            
            <!-- Progress Section -->
            <section x-show="isLoading">
                <div class="progress-container">
                    <div class="progress-header">
                        <h4 class="progress-title">データ取得中...</h4>
                        <span class="progress-percentage" x-text="`${progress}%`"></span>
                    </div>
                    
                    <div class="progress-bar">
                        <div class="progress-fill" :style="`width: ${progress}%`"></div>
                    </div>
                    
                    <p class="progress-status" x-text="statusMessage"></p>
                </div>
            </section>
            
            <!-- Stock Data List -->
            <section class="bg-white rounded-card shadow-md p-6">
                <h2 class="text-xl font-semibold text-gray-900 mb-6">取得済みデータ</h2>
                
                <!-- Loading State -->
                <div x-show="stocks.loading" class="text-center py-8">
                    <div class="animate-spin inline-block w-8 h-8 border-4 border-gray-300 border-t-blue-500 rounded-full"></div>
                    <p class="mt-2 text-gray-600">データを読み込んでいます...</p>
                </div>
                
                <!-- Empty State -->
                <div x-show="!stocks.loading && stocks.data.length === 0" class="text-center py-12">
                    <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"/>
                    </svg>
                    <h3 class="mt-2 text-sm font-medium text-gray-900">データがありません</h3>
                    <p class="mt-1 text-sm text-gray-500">最初のデータを取得してください</p>
                </div>
                
                <!-- Data Grid -->
                <div x-show="!stocks.loading && stocks.data.length > 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                    <template x-for="stock in stocks.data" :key="stock.symbol">
                        <div class="card">
                            <div class="card-header">
                                <h3 class="card-title" x-text="stock.symbol"></h3>
                                <span class="card-badge" x-text="`${stock.count}件`"></span>
                            </div>
                            <div class="card-body">
                                <p class="text-sm text-gray-600" x-text="`${stock.date_range}`"></p>
                                <div class="mt-4 flex space-x-2">
                                    <button class="btn-secondary btn-sm" @click="viewStockDetail(stock.symbol)">
                                        詳細
                                    </button>
                                    <button class="btn-danger btn-sm" @click="deleteStock(stock.symbol)">
                                        削除
                                    </button>
                                </div>
                            </div>
                        </div>
                    </template>
                </div>
                
                <!-- Pagination -->
                <div x-show="stocks.pages > 1" class="mt-6 flex justify-center">
                    <nav class="flex items-center space-x-2">
                        <button 
                            class="btn-secondary btn-sm"
                            @click="loadStocks(stocks.page - 1)"
                            :disabled="stocks.page <= 1">
                            前へ
                        </button>
                        
                        <span class="text-sm text-gray-600">
                            Page <span x-text="stocks.page"></span> of <span x-text="stocks.pages"></span>
                        </span>
                        
                        <button 
                            class="btn-secondary btn-sm"
                            @click="loadStocks(stocks.page + 1)"
                            :disabled="stocks.page >= stocks.pages">
                            次へ
                        </button>
                    </nav>
                </div>
            </section>
        </main>
    </div>
</body>
</html>
```

### 4.2 Alpine.js アプリケーションロジック

```javascript
// app/static/js/stock-app.js
function stockApp() {
    return {
        // State
        formData: {
            symbol: '',
            period: '1y'
        },
        
        isLoading: false,
        progress: 0,
        statusMessage: '',
        error: null,
        
        stocks: {
            data: [],
            loading: false,
            page: 1,
            pages: 1,
            total: 0
        },
        
        // Lifecycle
        init() {
            console.log('Stock App initialized');
            this.loadStocks();
        },
        
        // Methods
        async fetchStockData() {
            if (!this.formData.symbol.trim()) {
                this.error = '銘柄コードを入力してください';
                return;
            }
            
            // 銘柄コードフォーマットチェック
            if (!this.validateSymbol(this.formData.symbol)) {
                this.error = '正しい銘柄コード形式で入力してください (例: 7203.T)';
                return;
            }
            
            this.isLoading = true;
            this.progress = 0;
            this.error = null;
            this.statusMessage = 'データ取得を開始しています...';
            
            try {
                // データ取得API呼び出し
                const response = await fetch('/api/fetch-data', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        symbol: this.formData.symbol.toUpperCase(),
                        period: this.formData.period
                    })
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'データ取得に失敗しました');
                }
                
                const result = await response.json();
                
                // プログレス監視
                await this.monitorProgress(result.fetch_id);
                
                // 完了後にリスト更新
                await this.loadStocks();
                
            } catch (error) {
                console.error('Fetch error:', error);
                this.error = error.message;
            } finally {
                this.isLoading = false;
                this.progress = 0;
                this.statusMessage = '';
            }
        },
        
        async monitorProgress(fetchId) {
            return new Promise((resolve, reject) => {
                const checkStatus = async () => {
                    try {
                        const response = await fetch(`/api/fetch-status?fetch_id=${fetchId}`);
                        const status = await response.json();
                        
                        this.progress = status.progress?.percentage || 0;
                        this.statusMessage = status.current_status || '';
                        
                        if (status.status === 'completed') {
                            this.statusMessage = 'データ取得が完了しました';
                            setTimeout(() => resolve(), 1000);
                        } else if (status.status === 'error') {
                            reject(new Error('データ取得中にエラーが発生しました'));
                        } else {
                            // 継続監視
                            setTimeout(checkStatus, 1000);
                        }
                    } catch (error) {
                        reject(error);
                    }
                };
                
                checkStatus();
            });
        },
        
        async loadStocks(page = 1) {
            this.stocks.loading = true;
            
            try {
                const response = await fetch(`/api/stocks?page=${page}&per_page=12`);
                const data = await response.json();
                
                this.stocks.data = data.data || [];
                this.stocks.page = data.page || 1;
                this.stocks.pages = data.pages || 1;
                this.stocks.total = data.total || 0;
                
            } catch (error) {
                console.error('Load stocks error:', error);
                this.error = 'データの読み込みに失敗しました';
            } finally {
                this.stocks.loading = false;
            }
        },
        
        async deleteStock(symbol) {
            if (!confirm(`${symbol} のデータを削除しますか？`)) {
                return;
            }
            
            try {
                const response = await fetch(`/api/stocks/${symbol}`, {
                    method: 'DELETE'
                });
                
                if (!response.ok) {
                    throw new Error('削除に失敗しました');
                }
                
                // リスト更新
                await this.loadStocks();
                
            } catch (error) {
                console.error('Delete error:', error);
                this.error = error.message;
            }
        },
        
        viewStockDetail(symbol) {
            // 詳細表示（将来実装）
            alert(`${symbol} の詳細表示機能は今後実装予定です`);
        },
        
        validateSymbol(symbol) {
            // 基本的な銘柄コードフォーマット検証
            const pattern = /^[0-9]{4}\.T$/;
            return pattern.test(symbol);
        }
    }
}
```

## 5. レスポンシブデザイン

### 5.1 ブレークポイント戦略

```css
/* Tailwind Default Breakpoints */
/* sm: 640px */
/* md: 768px */  
/* lg: 1024px */
/* xl: 1280px */
/* 2xl: 1536px */

/* Mobile First Approach */
.container {
    @apply px-4;           /* Mobile: 16px padding */
}

@media (min-width: 640px) {
    .container {
        @apply px-6;       /* Tablet: 24px padding */
    }
}

@media (min-width: 1024px) {
    .container {
        @apply px-8;       /* Desktop: 32px padding */
    }
}
```

### 5.2 グリッドシステム

```html
<!-- Responsive Grid -->
<div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 md:gap-6">
    <!-- Mobile: 1 column -->
    <!-- Tablet: 2 columns -->
    <!-- Desktop: 3 columns -->
</div>

<!-- Form Layout -->
<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <!-- Mobile: Stacked -->
    <!-- Tablet+: Side by side -->
</div>
```

## 6. パフォーマンス最適化

### 6.1 遅延読み込み

```javascript
// 画像の遅延読み込み
function lazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}
```

### 6.2 Alpine.js 最適化

```javascript
// 大きなリストの仮想化（将来実装）
function virtualList() {
    return {
        items: [],
        visibleItems: [],
        itemHeight: 80,
        containerHeight: 400,
        
        init() {
            this.updateVisibleItems();
        },
        
        updateVisibleItems() {
            const startIndex = Math.floor(this.scrollTop / this.itemHeight);
            const endIndex = Math.min(
                startIndex + Math.ceil(this.containerHeight / this.itemHeight) + 1,
                this.items.length
            );
            
            this.visibleItems = this.items.slice(startIndex, endIndex);
        }
    }
}
```

## 7. アクセシビリティ

### 7.1 キーボードナビゲーション

```html
<!-- Focus Management -->
<button 
    class="btn-primary"
    @keydown.enter="fetchStockData()"
    @keydown.space.prevent="fetchStockData()">
    データ取得開始
</button>

<!-- Skip Links -->
<a href="#main-content" class="skip-link">
    メインコンテンツにスキップ
</a>

<style>
.skip-link {
    @apply absolute -top-full left-4 z-50 bg-blue-600 text-white px-4 py-2 rounded
           focus:top-4 transition-all duration-200;
}
</style>
```

### 7.2 ARIAラベル

```html
<!-- Progress Bar -->
<div 
    role="progressbar" 
    aria-valuenow="65" 
    aria-valuemin="0" 
    aria-valuemax="100"
    aria-label="データ取得進捗">
    <div class="progress-fill" style="width: 65%"></div>
</div>

<!-- Loading State -->
<div aria-live="polite" aria-label="読み込み状況">
    <span x-text="statusMessage"></span>
</div>
```

## 8. テスト戦略

### 8.1 手動テスト項目

**基本機能:**
- [ ] 銘柄コード入力・バリデーション
- [ ] データ取得・プログレス表示  
- [ ] 取得データ一覧表示
- [ ] ページネーション
- [ ] レスポンシブ表示

**ブラウザ別:**
- [ ] Chrome (最新版)
- [ ] Firefox (最新版)  
- [ ] Safari (最新版)
- [ ] Edge (最新版)

**デバイス別:**
- [ ] スマートフォン (375px)
- [ ] タブレット (768px)
- [ ] デスクトップ (1024px+)

### 8.2 将来のE2Eテスト

```javascript
// Playwright E2E Test Example
test('株価データ取得フロー', async ({ page }) => {
    await page.goto('/');
    
    // 銘柄コード入力
    await page.fill('#symbol', '7203.T');
    await page.selectOption('#period', '1y');
    
    // データ取得開始
    await page.click('button:has-text("データ取得開始")');
    
    // プログレスバー表示確認
    await expect(page.locator('.progress-container')).toBeVisible();
    
    // 完了まで待機
    await page.waitForSelector('.card', { timeout: 30000 });
    
    // 結果確認
    await expect(page.locator('.card')).toContainText('7203.T');
});
```

## まとめ

この MVP版 フロントエンド設計では：

### ✅ **実装範囲**
- macOS風デザインシステム
- Alpine.js による SPA風操作感
- レスポンシブ対応
- 基本的なアクセシビリティ
- プログレス表示・エラーハンドリング

### 🚀 **拡張準備** 
- コンポーネント化による再利用性
- 仮想化対応（大量データ）
- PWA対応準備
- 詳細画面・チャート表示への拡張

この設計により、**美しく使いやすい UI** を **シンプルな技術スタック** で実現できます。