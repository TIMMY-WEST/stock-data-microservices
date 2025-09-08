# Notification Service 仕様書

## 1. サービス概要

### 1.1 役割
- データ取得処理の進捗管理
- リアルタイム進捗通知
- タスク状態の追跡・更新
- フロントエンドへのステータス配信

### 1.2 技術スタック
- **Framework**: FastAPI (将来) / Flask内モジュール (MVP)
- **Port**: 8004 (将来) / internal (MVP)
- **Dependencies**: Redis (将来), asyncio, websockets (将来)
- **Current Implementation**: `services/progress.py`

## 2. 内部API仕様（マイクロサービス時）

### 2.1 タスク管理

#### POST /internal/create-task
新しいタスクの作成

**リクエスト:**
```http
POST /internal/create-task HTTP/1.1
Content-Type: application/json

{
  "task_type": "fetch_data",
  "symbol": "7203.T",
  "total_items": 252,
  "metadata": {
    "period": "1y",
    "requester": "api_gateway"
  }
}
```

**リクエストパラメータ:**
| パラメータ | 型 | 必須 | 説明 | 例 |
|-----------|---|------|------|---|
| task_type | string | ✅ | タスクの種類 | "fetch_data", "bulk_import" |
| symbol | string | ❌ | 銘柄コード | "7203.T" |
| total_items | integer | ✅ | 予定処理件数 | 252 |
| metadata | object | ❌ | 追加情報 | {...} |

**レスポンス:**
```json
{
  "task_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "created",
  "task_type": "fetch_data",
  "symbol": "7203.T",
  "total_items": 252,
  "created_at": "2024-01-15T10:30:00+09:00",
  "estimated_completion": "2024-01-15T10:30:45+09:00"
}
```

#### PUT /internal/task/{task_id}/update
タスクの進捗更新

**リクエスト:**
```http
PUT /internal/task/f47ac10b-58cc-4372-a567-0e02b2c3d479/update HTTP/1.1
Content-Type: application/json

{
  "status": "running",
  "current_items": 150,
  "message": "データを処理しています... (150/252)",
  "details": {
    "processing_rate": "10 items/sec",
    "estimated_remaining": "10 seconds"
  }
}
```

**リクエストパラメータ:**
| パラメータ | 型 | 必須 | 説明 |
|-----------|---|------|------|
| status | string | ✅ | タスク状態 ("running", "completed", "error", "paused") |
| current_items | integer | ❌ | 現在の処理件数 |
| message | string | ❌ | 表示メッセージ |
| details | object | ❌ | 詳細情報 |
| error_message | string | ❌ | エラーメッセージ（status="error"時） |

**レスポンス:**
```json
{
  "task_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "running",
  "progress": {
    "current": 150,
    "total": 252,
    "percentage": 59.5
  },
  "updated_at": "2024-01-15T10:30:30+09:00"
}
```

#### GET /internal/task/{task_id}/status
タスク状況の取得

**リクエスト:**
```http
GET /internal/task/f47ac10b-58cc-4372-a567-0e02b2c3d479/status HTTP/1.1
```

**レスポンス (処理中):**
```json
{
  "task_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "running",
  "task_type": "fetch_data",
  "symbol": "7203.T",
  "progress": {
    "current": 150,
    "total": 252,
    "percentage": 59.5
  },
  "current_status": "データを処理しています... (150/252)",
  "start_time": "2024-01-15T10:30:00+09:00",
  "updated_at": "2024-01-15T10:30:30+09:00",
  "estimated_completion": "2024-01-15T10:30:45+09:00",
  "processing_details": {
    "processing_rate": "10 items/sec",
    "estimated_remaining": "10 seconds"
  }
}
```

**レスポンス (完了):**
```json
{
  "task_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "completed",
  "task_type": "fetch_data",
  "symbol": "7203.T",
  "progress": {
    "current": 252,
    "total": 252,
    "percentage": 100
  },
  "current_status": "データ取得が完了しました",
  "start_time": "2024-01-15T10:30:00+09:00",
  "end_time": "2024-01-15T10:30:45+09:00",
  "processing_time_ms": 45000,
  "results": {
    "records_saved": 252,
    "records_skipped": 0,
    "success_rate": 100
  }
}
```

### 2.2 タスク一覧・履歴

#### GET /internal/tasks
タスク一覧の取得

**リクエスト:**
```http
GET /internal/tasks?status=running&task_type=fetch_data&page=1&limit=20 HTTP/1.1
```

**クエリパラメータ:**
| パラメータ | 型 | 必須 | 説明 |
|-----------|---|------|------|
| status | string | ❌ | ステータスフィルター |
| task_type | string | ❌ | タスク種別フィルター |
| symbol | string | ❌ | 銘柄フィルター |
| page | integer | ❌ | ページ番号 (default: 1) |
| limit | integer | ❌ | 1ページあたりの件数 (default: 20) |

**レスポンス:**
```json
{
  "tasks": [
    {
      "task_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "status": "running",
      "task_type": "fetch_data",
      "symbol": "7203.T",
      "progress": {
        "current": 150,
        "total": 252,
        "percentage": 59.5
      },
      "start_time": "2024-01-15T10:30:00+09:00"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "pages": 1
  },
  "summary": {
    "running": 1,
    "completed": 15,
    "error": 0
  }
}
```

### 2.3 WebSocket通知 (将来実装)

#### WebSocket /internal/ws/task/{task_id}
タスク進捗のリアルタイム通知

**接続:**
```javascript
const ws = new WebSocket('ws://notification:8004/internal/ws/task/f47ac10b-58cc-4372-a567-0e02b2c3d479');

ws.onmessage = (event) => {
    const update = JSON.parse(event.data);
    console.log('Progress update:', update);
};
```

**通知メッセージ:**
```json
{
  "type": "progress_update",
  "task_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "running",
  "progress": {
    "current": 150,
    "total": 252,
    "percentage": 59.5
  },
  "message": "データを処理しています... (150/252)",
  "timestamp": "2024-01-15T10:30:30+09:00"
}
```

### 2.4 ヘルスチェック

#### GET /internal/health
サービス稼働状況確認

**レスポンス:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "active_tasks": 3,
  "total_tasks_today": 25,
  "memory_usage": {
    "tasks_in_memory": 100,
    "memory_usage_mb": 32
  },
  "dependencies": {
    "redis": {
      "status": "connected",
      "response_time_ms": 5
    }
  }
}
```

## 3. タスク管理実装

### 3.1 タスク管理クラス

```python
# services/progress.py - プログレス管理実装
import asyncio
import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

class TaskStatus:
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class Task:
    def __init__(
        self,
        task_id: str,
        task_type: str,
        total_items: int,
        symbol: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        self.task_id = task_id
        self.task_type = task_type
        self.symbol = symbol
        self.total_items = total_items
        self.current_items = 0
        self.status = TaskStatus.CREATED
        self.message = ""
        self.error_message = None
        self.metadata = metadata or {}

        self.created_at = datetime.now()
        self.started_at = None
        self.updated_at = None
        self.completed_at = None

        self.results = {}
        self.processing_details = {}

    def to_dict(self) -> Dict[str, Any]:
        """タスクオブジェクトを辞書に変換"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "symbol": self.symbol,
            "status": self.status,
            "progress": {
                "current": self.current_items,
                "total": self.total_items,
                "percentage": (self.current_items / self.total_items * 100) if self.total_items > 0 else 0
            },
            "current_status": self.message,
            "start_time": self.started_at.isoformat() if self.started_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "end_time": self.completed_at.isoformat() if self.completed_at else None,
            "processing_time_ms": self._get_processing_time_ms(),
            "results": self.results,
            "processing_details": self.processing_details,
            "error_message": self.error_message,
            "metadata": self.metadata
        }

    def _get_processing_time_ms(self) -> Optional[int]:
        """処理時間をミリ秒で計算"""
        if not self.started_at:
            return None

        end_time = self.completed_at or datetime.now()
        return int((end_time - self.started_at).total_seconds() * 1000)

class ProgressService:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.logger = logging.getLogger(__name__)

        # WebSocket接続管理（将来実装）
        self.websocket_connections = {}

        # タスク履歴の自動削除（24時間後）
        self._start_cleanup_task()

    async def create_task(
        self,
        task_type: str,
        total_items: int,
        symbol: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """新しいタスクを作成"""

        task_id = str(uuid.uuid4())
        task = Task(task_id, task_type, total_items, symbol, metadata)

        self.tasks[task_id] = task

        self.logger.info(f"Created task {task_id}: {task_type}")

        # WebSocket通知（将来実装）
        # await self._notify_websocket_subscribers(task_id, "task_created", task.to_dict())

        return task_id

    async def update_progress(
        self,
        task_id: str,
        status: str,
        current_items: Optional[int] = None,
        message: Optional[str] = None,
        error_message: Optional[str] = None,
        results: Optional[Dict] = None,
        processing_details: Optional[Dict] = None
    ) -> Dict:
        """タスクの進捗を更新"""

        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")

        task = self.tasks[task_id]

        # ステータス更新
        old_status = task.status
        task.status = status
        task.updated_at = datetime.now()

        # 開始時刻の記録
        if old_status == TaskStatus.CREATED and status == TaskStatus.RUNNING:
            task.started_at = datetime.now()

        # 完了時刻の記録
        if status in [TaskStatus.COMPLETED, TaskStatus.ERROR, TaskStatus.CANCELLED]:
            task.completed_at = datetime.now()

        # 進捗情報の更新
        if current_items is not None:
            task.current_items = current_items

        if message:
            task.message = message

        if error_message:
            task.error_message = error_message

        if results:
            task.results.update(results)

        if processing_details:
            task.processing_details.update(processing_details)

        self.logger.info(f"Updated task {task_id}: {status} ({current_items}/{task.total_items})")

        # WebSocket通知（将来実装）
        # await self._notify_websocket_subscribers(task_id, "progress_update", task.to_dict())

        return task.to_dict()

    async def get_task_status(self, task_id: str) -> Optional[Dict]:
        """タスクの状況を取得"""

        if task_id not in self.tasks:
            return None

        return self.tasks[task_id].to_dict()

    async def get_tasks_list(
        self,
        status: Optional[str] = None,
        task_type: Optional[str] = None,
        symbol: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> Dict:
        """タスク一覧を取得"""

        # フィルタリング
        filtered_tasks = []
        for task in self.tasks.values():
            if status and task.status != status:
                continue
            if task_type and task.task_type != task_type:
                continue
            if symbol and task.symbol != symbol:
                continue

            filtered_tasks.append(task)

        # ソート（作成日時降順）
        filtered_tasks.sort(key=lambda t: t.created_at, reverse=True)

        # ページング
        total = len(filtered_tasks)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        page_tasks = filtered_tasks[start_idx:end_idx]

        # ステータス集計
        status_summary = {}
        for task in self.tasks.values():
            status_summary[task.status] = status_summary.get(task.status, 0) + 1

        return {
            "tasks": [task.to_dict() for task in page_tasks],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit if total > 0 else 1
            },
            "summary": status_summary
        }

    async def cancel_task(self, task_id: str) -> Dict:
        """タスクをキャンセル"""

        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")

        task = self.tasks[task_id]

        if task.status in [TaskStatus.COMPLETED, TaskStatus.ERROR, TaskStatus.CANCELLED]:
            raise ValueError(f"Cannot cancel task in status: {task.status}")

        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now()
        task.message = "タスクがキャンセルされました"

        self.logger.info(f"Cancelled task {task_id}")

        return task.to_dict()

    def _start_cleanup_task(self):
        """古いタスクの自動削除タスクを開始"""
        asyncio.create_task(self._cleanup_old_tasks())

    async def _cleanup_old_tasks(self):
        """24時間以上前のタスクを削除"""
        while True:
            try:
                cutoff_time = datetime.now() - timedelta(hours=24)

                tasks_to_remove = []
                for task_id, task in self.tasks.items():
                    if (task.completed_at or task.created_at) < cutoff_time:
                        tasks_to_remove.append(task_id)

                for task_id in tasks_to_remove:
                    del self.tasks[task_id]
                    self.logger.info(f"Cleaned up old task {task_id}")

                # 1時間ごとに実行
                await asyncio.sleep(3600)

            except Exception as e:
                self.logger.error(f"Error in cleanup task: {str(e)}")
                await asyncio.sleep(3600)
```

### 3.2 進捗通知ユーティリティ

```python
# services/progress.py - 進捗通知ユーティリティ
class ProgressNotifier:
    """進捗通知のためのヘルパークラス"""

    def __init__(self, task_id: str, progress_service: ProgressService):
        self.task_id = task_id
        self.progress_service = progress_service
        self.last_update = datetime.now()
        self.update_interval = 1.0  # 1秒間隔で更新

    async def update(
        self,
        current: int,
        total: int,
        message: str = "",
        details: Optional[Dict] = None
    ):
        """進捗を更新（間隔制限付き）"""

        now = datetime.now()
        if (now - self.last_update).total_seconds() < self.update_interval:
            return

        await self.progress_service.update_progress(
            self.task_id,
            TaskStatus.RUNNING,
            current_items=current,
            message=message or f"処理中... ({current}/{total})",
            processing_details=details
        )

        self.last_update = now

    async def complete(self, results: Optional[Dict] = None, message: str = "完了しました"):
        """完了通知"""
        await self.progress_service.update_progress(
            self.task_id,
            TaskStatus.COMPLETED,
            message=message,
            results=results or {}
        )

    async def error(self, error_message: str):
        """エラー通知"""
        await self.progress_service.update_progress(
            self.task_id,
            TaskStatus.ERROR,
            error_message=error_message,
            message="エラーが発生しました"
        )

# 使用例
async def example_data_fetch_with_progress():
    """進捗通知付きのデータ取得例"""

    progress_service = ProgressService()

    # タスク作成
    task_id = await progress_service.create_task(
        "fetch_data",
        total_items=100,
        symbol="7203.T"
    )

    notifier = ProgressNotifier(task_id, progress_service)

    try:
        # 処理実行
        for i in range(100):
            # 何らかの処理
            await asyncio.sleep(0.1)

            # 進捗通知
            await notifier.update(
                current=i+1,
                total=100,
                message=f"データ処理中... ({i+1}/100)",
                details={"processing_rate": "10 items/sec"}
            )

        # 完了通知
        await notifier.complete(
            results={"processed": 100, "success": 100},
            message="すべてのデータ処理が完了しました"
        )

    except Exception as e:
        # エラー通知
        await notifier.error(f"処理中にエラーが発生しました: {str(e)}")
```

## 4. 現在のMVP実装

### 4.1 MVP時のファイル構造
```
services/
└── progress.py         # 現在の実装ファイル
    ├── ProgressService クラス
    ├── Task モデル
    └── 進捗管理メソッド
```

### 4.2 マイクロサービス移行準備

```python
# services/progress.py - 移行準備の実装
from abc import ABC, abstractmethod

class NotificationServiceInterface(ABC):
    """Notification Service インターフェース"""

    @abstractmethod
    async def create_task(self, task_type: str, total_items: int, **kwargs) -> str:
        pass

    @abstractmethod
    async def update_progress(self, task_id: str, **kwargs) -> Dict:
        pass

    @abstractmethod
    async def get_task_status(self, task_id: str) -> Optional[Dict]:
        pass

    @abstractmethod
    async def health_check(self) -> Dict:
        pass

class ProgressService(NotificationServiceInterface):
    """進捗管理実装（MVP時の内部実装）"""

    async def handle_request(self, endpoint: str, method: str, data: dict):
        """統一リクエストハンドラ（将来のHTTP API用）"""

        if endpoint == '/internal/create-task' and method == 'POST':
            return await self.create_task(
                data['task_type'],
                data['total_items'],
                symbol=data.get('symbol'),
                metadata=data.get('metadata')
            )

        elif endpoint.startswith('/internal/task/') and endpoint.endswith('/update') and method == 'PUT':
            task_id = endpoint.split('/')[-2]
            return await self.update_progress(task_id, **data)

        elif endpoint.startswith('/internal/task/') and endpoint.endswith('/status') and method == 'GET':
            task_id = endpoint.split('/')[-2]
            return await self.get_task_status(task_id)

        elif endpoint == '/internal/tasks' and method == 'GET':
            return await self.get_tasks_list(**data)

        elif endpoint == '/internal/health' and method == 'GET':
            return await self.health_check()

        else:
            raise ValueError(f"Unknown endpoint: {endpoint}")

    async def health_check(self) -> Dict:
        """ヘルスチェック"""
        return {
            "status": "healthy",
            "version": "1.0.0",
            "active_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.RUNNING]),
            "total_tasks_today": len(self.tasks),
            "memory_usage": {
                "tasks_in_memory": len(self.tasks),
                "memory_usage_mb": len(str(self.tasks)) // 1024 // 1024  # 概算
            }
        }
```

## 5. 将来の拡張機能

### 5.1 WebSocket通知
```python
# 将来実装予定のWebSocket機能
import websockets
import json

class WebSocketManager:
    def __init__(self):
        self.connections = {}  # task_id -> list of websockets

    async def add_connection(self, task_id: str, websocket):
        if task_id not in self.connections:
            self.connections[task_id] = []
        self.connections[task_id].append(websocket)

    async def remove_connection(self, task_id: str, websocket):
        if task_id in self.connections:
            self.connections[task_id].remove(websocket)

    async def notify_subscribers(self, task_id: str, message: Dict):
        if task_id in self.connections:
            disconnected = []
            for websocket in self.connections[task_id]:
                try:
                    await websocket.send(json.dumps(message))
                except websockets.exceptions.ConnectionClosed:
                    disconnected.append(websocket)

            # 切断された接続を削除
            for websocket in disconnected:
                self.connections[task_id].remove(websocket)
```

### 5.2 Redis活用
```python
# 将来のRedis連携機能
import redis.asyncio as redis

class RedisProgressService(ProgressService):
    def __init__(self, redis_url: str):
        super().__init__()
        self.redis = redis.from_url(redis_url)

    async def create_task(self, **kwargs) -> str:
        task_id = await super().create_task(**kwargs)

        # Redisに永続化
        task_data = self.tasks[task_id].to_dict()
        await self.redis.setex(
            f"task:{task_id}",
            86400,  # 24時間
            json.dumps(task_data)
        )

        return task_id

    async def update_progress(self, task_id: str, **kwargs) -> Dict:
        result = await super().update_progress(task_id, **kwargs)

        # Redisに更新を保存
        await self.redis.setex(
            f"task:{task_id}",
            86400,
            json.dumps(result)
        )

        # Pub/Sub でリアルタイム通知
        await self.redis.publish(
            f"task_update:{task_id}",
            json.dumps(result)
        )

        return result
```

---

## まとめ

このNotification Service仕様書では：

### ✅ **現在のMVP対応**
- `services/progress.py` での実装
- インメモリでの進捗管理
- 基本的なタスク状態追跡

### 🚀 **将来のマイクロサービス対応**
- FastAPI による独立サービス化準備
- Redis による永続化・Pub/Sub
- WebSocket によるリアルタイム通知

### 📊 **高度な機能**
- 自動タスククリーンアップ
- 進捗更新の間隔制限
- 詳細な統計情報提供

この設計により、ユーザーフレンドリーな進捗表示と、将来の高度な通知機能に対応できます。
