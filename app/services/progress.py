import json
import os
from datetime import UTC, datetime
from typing import Any, Dict, Optional


class ProgressService:
    """プログレス管理サービス（MVP版：メモリ＆ファイルベース）"""

    def __init__(self) -> None:
        self.progress_file = "progress_data.json"
        self.tasks: Dict[Any, Any] = {}
        self._load_tasks()

    def _load_tasks(self) -> None:
        """タスクデータをファイルから読み込み"""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, "r", encoding="utf-8") as f:
                    self.tasks = json.load(f)
        except Exception as e:
            print(f"プログレスファイル読み込みエラー: {e}")
            self.tasks = {}

    def _save_tasks(self) -> None:
        """タスクデータをファイルに保存"""
        try:
            with open(self.progress_file, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"プログレスファイル保存エラー: {e}")

    def initialize_task(self, task_id: str, total_items: int) -> None:
        """タスクを初期化"""
        self.tasks[task_id] = {
            "status": "running",
            "progress": 0,
            "total": total_items,
            "current_item": 0,
            "message": "タスクを開始しました",
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat(),
            "completed_at": None,
            "error": None,
            "details": [],
        }
        self._save_tasks()

    def update_progress(
        self, task_id: str, current_item: int, message: str = ""
    ) -> bool:
        """プログレスを更新"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        task["current_item"] = current_item
        task["progress"] = int((current_item / task["total"]) * 100)
        task["message"] = message or f"{current_item}/{task['total']} 完了"
        task["updated_at"] = datetime.now(UTC).isoformat()

        # 詳細履歴を追加
        task["details"].append(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "message": message,
                "item": current_item,
            }
        )

        # 最新20件のみ保持
        if len(task["details"]) > 20:
            task["details"] = task["details"][-20:]

        self._save_tasks()
        return True

    def complete_task(self, task_id: str) -> bool:
        """タスクを完了状態にする"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        task["status"] = "completed"
        task["progress"] = 100
        task["message"] = "タスクが完了しました"
        task["completed_at"] = datetime.now(UTC).isoformat()
        task["updated_at"] = datetime.now(UTC).isoformat()

        self._save_tasks()
        return True

    def error_task(self, task_id: str, error_message: str) -> bool:
        """タスクをエラー状態にする"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        task["status"] = "error"
        task["message"] = "エラーが発生しました"
        task["error"] = error_message
        task["updated_at"] = datetime.now(UTC).isoformat()

        self._save_tasks()
        return True

    def get_status(self, task_id: str) -> Optional[Dict[Any, Any]]:
        """タスクの状態を取得"""
        if task_id not in self.tasks:
            return None

        return dict(self.tasks[task_id].copy())

    def get_all_tasks(self) -> Dict[Any, Any]:
        """全タスクの状態を取得"""
        return dict(self.tasks.copy())

    def cleanup_old_tasks(self, days: int = 7) -> int:
        """古いタスクデータをクリーンアップ"""
        try:
            cutoff_date = datetime.utcnow().timestamp() - (days * 24 * 60 * 60)

            tasks_to_remove = []
            for task_id, task in self.tasks.items():
                created_at = datetime.fromisoformat(
                    task["created_at"].replace("Z", "+00:00")
                )
                if created_at.timestamp() < cutoff_date:
                    tasks_to_remove.append(task_id)

            for task_id in tasks_to_remove:
                del self.tasks[task_id]

            if tasks_to_remove:
                self._save_tasks()

            return len(tasks_to_remove)

        except Exception as e:
            print(f"タスククリーンアップエラー: {e}")
            return 0
