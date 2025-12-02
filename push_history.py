#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
推送历史记录管理模块

解决 incremental 模式的核心问题：
1. 记录已推送的新闻ID/标题
2. 确保真正的增量推送
3. 跨运行周期的持久化历史记录
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Set, Optional


class PushHistory:
    """推送历史记录管理器"""
    
    def __init__(self, base_dir: str = "output"):
        self.base_dir = Path(base_dir)
        self.history_file = self.base_dir / "push_history.json"
        self._ensure_history_file()
    
    def _ensure_history_file(self):
        """确保历史记录文件存在"""
        self.base_dir.mkdir(exist_ok=True)
        if not self.history_file.exists():
            self._save_history({"pushed_items": {}, "last_cleanup": None})
    
    def _load_history(self) -> Dict:
        """加载历史记录"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"pushed_items": {}, "last_cleanup": None}
    
    def _save_history(self, data: Dict):
        """保存历史记录"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _generate_content_hash(self, title: str, source_id: str, url: str = "") -> str:
        """生成内容哈希，用于去重判断"""
        content = f"{source_id}:{title}:{url}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def has_been_pushed(self, title: str, source_id: str, url: str = "") -> bool:
        """检查内容是否已推送过"""
        history = self._load_history()
        content_hash = self._generate_content_hash(title, source_id, url)
        return content_hash in history["pushed_items"]
    
    def mark_as_pushed(self, title: str, source_id: str, url: str = "", 
                      push_time: Optional[str] = None):
        """标记内容为已推送"""
        if push_time is None:
            push_time = datetime.now().isoformat()
        
        history = self._load_history()
        content_hash = self._generate_content_hash(title, source_id, url)
        
        history["pushed_items"][content_hash] = {
            "title": title,
            "source_id": source_id,
            "url": url,
            "push_time": push_time,
            "hash": content_hash
        }
        
        self._save_history(history)
    
    def get_new_items(self, all_items: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        获取未推送过的项目
        all_items: {source_id: {title: title_data}}
        返回: {source_id: {title: title_data}}
        """
        new_items = {}
        
        for source_id, source_items in all_items.items():
            new_source_items = {}
            
            for title, title_data in source_items.items():
                url = title_data.get("url", "")
                
                if not self.has_been_pushed(title, source_id, url):
                    new_source_items[title] = title_data
            
            if new_source_items:
                new_items[source_id] = new_source_items
        
        return new_items
    
    def mark_items_as_pushed(self, items: Dict[str, Dict], 
                              push_time: Optional[str] = None):
        """
        批量标记项目为已推送
        items: {source_id: {title: title_data}}
        """
        if push_time is None:
            push_time = datetime.now().isoformat()
        
        for source_id, source_items in items.items():
            for title, title_data in source_items.items():
                url = title_data.get("url", "")
                self.mark_as_pushed(title, source_id, url, push_time)
    
    def cleanup_old_records(self, days_to_keep: int = 30):
        """清理旧的历史记录，只保留指定天数内的记录"""
        history = self._load_history()
        
        cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 3600)
        
        cleaned_items = {}
        for content_hash, item_data in history["pushed_items"].items():
            try:
                item_time = datetime.fromisoformat(item_data["push_time"]).timestamp()
                if item_time >= cutoff_time:
                    cleaned_items[content_hash] = item_data
            except (ValueError, KeyError):
                # 如果时间格式有问题，保留该记录
                cleaned_items[content_hash] = item_data
        
        history["pushed_items"] = cleaned_items
        history["last_cleanup"] = datetime.now().isoformat()
        
        self._save_history(history)
    
    def get_statistics(self) -> Dict:
        """获取历史记录统计信息"""
        history = self._load_history()
        
        pushed_items = history["pushed_items"]
        total_pushed = len(pushed_items)
        
        # 按来源统计
        source_stats = {}
        for item_data in pushed_items.values():
            source_id = item_data["source_id"]
            source_stats[source_id] = source_stats.get(source_id, 0) + 1
        
        # 按日期统计
        date_stats = {}
        for item_data in pushed_items.values():
            try:
                push_time = datetime.fromisoformat(item_data["push_time"])
                date_key = push_time.strftime("%Y-%m-%d")
                date_stats[date_key] = date_stats.get(date_key, 0) + 1
            except ValueError:
                continue
        
        return {
            "total_pushed": total_pushed,
            "source_distribution": source_stats,
            "date_distribution": date_stats,
            "last_cleanup": history.get("last_cleanup"),
            "history_file_path": str(self.history_file)
        }