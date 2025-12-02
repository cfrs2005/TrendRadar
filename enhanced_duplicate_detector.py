#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强的重复内容检测和日志系统
Enhanced duplicate content detection and logging system
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class DuplicateRecord:
    """重复记录数据类"""
    original_title: str
    original_platform: str
    duplicate_title: str
    duplicate_platform: str
    similarity_score: float
    hash_match: bool
    detection_time: str


@dataclass
class DuplicateStats:
    """重复统计数据类"""
    total_processed: int
    total_duplicates: int
    unique_content: int
    platform_duplicates: Dict[str, int]
    cross_platform_duplicates: int
    hash_based_duplicates: int
    similarity_based_duplicates: int
    duplicate_records: List[DuplicateRecord]


class EnhancedDuplicateDetector:
    """增强的重复内容检测器"""
    
    def __init__(self, enable_similarity_check: bool = True):
        self.enable_similarity_check = enable_similarity_check
        self.seen_hashes = set()
        self.seen_titles = set()
        self.duplicate_stats = DuplicateStats(
            total_processed=0,
            total_duplicates=0,
            unique_content=0,
            platform_duplicates={},
            cross_platform_duplicates=0,
            hash_based_duplicates=0,
            similarity_based_duplicates=0,
            duplicate_records=[]
        )
        
        # 配置日志
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _generate_content_hash(self, title: str, platform: str = "") -> str:
        """生成内容哈希"""
        # 标准化标题：去除多余空格、统一大小写、去除特殊字符
        normalized_title = self._normalize_title(title)
        content = f"{normalized_title}|{platform}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def _normalize_title(self, title: str) -> str:
        """标准化标题"""
        # 去除多余空格、统一大小写、去除常见无意义字符
        normalized = " ".join(title.split()).lower()
        # 移除常见的标点符号和表情符号（可根据需要扩展）
        import re
        normalized = re.sub(r'[^\w\s\u4e00-\u9fff]', '', normalized)
        return normalized.strip()

    def _calculate_similarity(self, title1: str, title2: str) -> float:
        """计算两个标题的相似度（简化版）"""
        # 使用简单的字符重叠度作为相似度指标
        # 实际使用中可以集成更复杂的语义相似度算法
        norm1 = self._normalize_title(title1)
        norm2 = self._normalize_title(title2)
        
        if not norm1 or not norm2:
            return 0.0
            
        # 计算字符重叠度
        set1 = set(norm1)
        set2 = set(norm2)
        intersection = set1 & set2
        union = set1 | set2
        
        return len(intersection) / len(union) if union else 0.0

    def _is_duplicate(self, title: str, platform: str, original_data: Dict[str, Any]) -> Tuple[bool, Optional[DuplicateRecord]]:
        """检查是否为重复内容"""
        content_hash = self._generate_content_hash(title, platform)
        normalized_title = self._normalize_title(title)
        
        # 1. 精确哈希匹配
        if content_hash in self.seen_hashes:
            # 查找原始记录
            for seen_hash, (orig_title, orig_platform) in getattr(self, '_hash_mapping', {}).items():
                if seen_hash == content_hash:
                    record = DuplicateRecord(
                        original_title=orig_title,
                        original_platform=orig_platform,
                        duplicate_title=title,
                        duplicate_platform=platform,
                        similarity_score=1.0,
                        hash_match=True,
                        detection_time=datetime.now().strftime('%H:%M:%S')
                    )
                    return True, record
        
        # 2. 标准化标题匹配
        if normalized_title in self.seen_titles:
            # 查找原始记录
            for seen_title, (orig_title, orig_platform) in getattr(self, '_title_mapping', {}).items():
                if seen_title == normalized_title:
                    record = DuplicateRecord(
                        original_title=orig_title,
                        original_platform=orig_platform,
                        duplicate_title=title,
                        duplicate_platform=platform,
                        similarity_score=1.0,
                        hash_match=False,
                        detection_time=datetime.now().strftime('%H:%M:%S')
                    )
                    return True, record
        
        # 3. 相似度匹配（如果启用）
        if self.enable_similarity_check:
            similarity_threshold = 0.8  # 可配置的相似度阈值
            for seen_title, (orig_title, orig_platform) in getattr(self, '_title_mapping', {}).items():
                similarity = self._calculate_similarity(title, orig_title)
                if similarity >= similarity_threshold:
                    record = DuplicateRecord(
                        original_title=orig_title,
                        original_platform=orig_platform,
                        duplicate_title=title,
                        duplicate_platform=platform,
                        similarity_score=similarity,
                        hash_match=False,
                        detection_time=datetime.now().strftime('%H:%M:%S')
                    )
                    return True, record
        
        return False, None

    def add_content(self, title: str, platform: str, data: Dict[str, Any]) -> bool:
        """添加内容并检测重复"""
        self.duplicate_stats.total_processed += 1
        
        # 初始化映射字典
        if not hasattr(self, '_hash_mapping'):
            self._hash_mapping = {}
        if not hasattr(self, '_title_mapping'):
            self._title_mapping = {}
        
        # 检查重复
        is_duplicate, duplicate_record = self._is_duplicate(title, platform, data)
        
        if is_duplicate and duplicate_record:
            # 记录重复
            self.duplicate_stats.total_duplicates += 1
            self.duplicate_stats.duplicate_records.append(duplicate_record)
            
            # 统计平台重复
            if duplicate_record.original_platform == duplicate_record.duplicate_platform:
                self.duplicate_stats.platform_duplicates[duplicate_record.original_platform] = \
                    self.duplicate_stats.platform_duplicates.get(duplicate_record.original_platform, 0) + 1
            else:
                self.duplicate_stats.cross_platform_duplicates += 1
            
            # 统计检测方式
            if duplicate_record.hash_match:
                self.duplicate_stats.hash_based_duplicates += 1
            else:
                self.duplicate_stats.similarity_based_duplicates += 1
            
            # 记录详细日志
            self.logger.info(
                f"🔄 发现重复内容 | "
                f"原始: [{duplicate_record.original_platform}] {duplicate_record.original_title} | "
                f"重复: [{duplicate_record.duplicate_platform}] {duplicate_record.duplicate_title} | "
                f"相似度: {duplicate_record.similarity_score:.2f} | "
                f"哈希匹配: {'是' if duplicate_record.hash_match else '否'}"
            )
            
            return False  # 是重复内容，不添加到最终结果
        
        # 添加到已记录内容
        content_hash = self._generate_content_hash(title, platform)
        normalized_title = self._normalize_title(title)
        
        self.seen_hashes.add(content_hash)
        self.seen_titles.add(normalized_title)
        self._hash_mapping[content_hash] = (title, platform)
        self._title_mapping[normalized_title] = (title, platform)
        
        self.duplicate_stats.unique_content += 1
        
        # 记录新增内容日志
        self.logger.debug(
            f"✅ 新增内容 | [{platform}] {title}"
        )
        
        return True  # 非重复内容

    def get_duplicate_summary(self) -> str:
        """获取去重摘要"""
        stats = self.duplicate_stats
        
        if stats.total_duplicates == 0:
            return (
                f"🎯 **去重摘要**\n"
                f"• 处理总数: {stats.total_processed} 条\n"
                f"• 重复内容: 0 条\n"
                f"• 保留内容: {stats.unique_content} 条\n"
                f"• 去重率: 0%"
            )
        
        duplicate_rate = (stats.total_duplicates / stats.total_processed * 100) if stats.total_processed > 0 else 0
        
        summary = [
            f"🎯 **去重摘要**",
            f"• 处理总数: {stats.total_processed} 条",
            f"• 重复内容: {stats.total_duplicates} 条",
            f"• 保留内容: {stats.unique_content} 条", 
            f"• 去重率: {duplicate_rate:.1f}%",
            "",
            f"🔍 **检测方式分布**",
            f"• 哈希匹配: {stats.hash_based_duplicates} 条",
            f"• 相似度匹配: {stats.similarity_based_duplicates} 条",
            "",
            f"📱 **平台重复分析**"
        ]
        
        if stats.platform_duplicates:
            for platform, count in stats.platform_duplicates.items():
                summary.append(f"• {platform}: {count} 条")
        
        if stats.cross_platform_duplicates > 0:
            summary.append(f"• 跨平台重复: {stats.cross_platform_duplicates} 条")
        
        return "\n".join(summary)

    def get_duplicate_details(self) -> str:
        """获取重复内容详细信息"""
        if not self.duplicate_stats.duplicate_records:
            return "🎉 恭喜！本次未发现重复内容。"
        
        details = [
            "🔍 **重复内容详情**",
            ""
        ]
        
        # 按平台分组显示
        platform_groups = {}
        for record in self.duplicate_stats.duplicate_records:
            key = f"{record.original_platform} → {record.duplicate_platform}"
            if key not in platform_groups:
                platform_groups[key] = []
            platform_groups[key].append(record)
        
        for platform_pair, records in platform_groups.items():
            details.append(f"**{platform_pair}** ({len(records)} 条):")
            for i, record in enumerate(records[:5], 1):  # 最多显示5条
                details.append(
                    f"  {i}. {record.duplicate_title}\n"
                    f"     原始: {record.original_title} "
                    f"(相似度: {record.similarity_score:.2f}, "
                    f"时间: {record.detection_time})"
                )
            
            if len(records) > 5:
                details.append(f"  ... 还有 {len(records) - 5} 条重复内容")
            details.append("")
        
        return "\n".join(details)

    def get_stats_dict(self) -> Dict[str, Any]:
        """获取统计信息字典"""
        return asdict(self.duplicate_stats)

    def reset_stats(self):
        """重置统计信息"""
        self.duplicate_stats = DuplicateStats(
            total_processed=0,
            total_duplicates=0,
            unique_content=0,
            platform_duplicates={},
            cross_platform_duplicates=0,
            hash_based_duplicates=0,
            similarity_based_duplicates=0,
            duplicate_records=[]
        )
        self.seen_hashes.clear()
        self.seen_titles.clear()
        if hasattr(self, '_hash_mapping'):
            self._hash_mapping.clear()
        if hasattr(self, '_title_mapping'):
            self._title_mapping.clear()