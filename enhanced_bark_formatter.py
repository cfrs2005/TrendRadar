#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强的Bark消息格式化器
Enhanced Bark message formatter with improved markdown and table support
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from enhanced_duplicate_detector import EnhancedDuplicateDetector


class EnhancedBarkFormatter:
    """增强的Bark消息格式化器"""
    
    def __init__(self, enable_duplicate_detection: bool = True):
        self.enable_duplicate_detection = enable_duplicate_detection
        if enable_duplicate_detection:
            self.duplicate_detector = EnhancedDuplicateDetector(enable_similarity_check=True)
        else:
            self.duplicate_detector = None
    
    def format_enhanced_message(self, report_data: Dict[str, Any], now: datetime, 
                             update_info: Optional[Dict[str, str]] = None) -> List[str]:
        """格式化增强的Bark消息"""
        
        # 去重处理
        if self.enable_duplicate_detection and self.duplicate_detector:
            filtered_report_data = self._remove_duplicates(report_data)
        else:
            filtered_report_data = report_data
        
        # 构建消息内容
        message_content = self._build_message_content(filtered_report_data, now, update_info)
        
        # 按Bark大小限制分批
        batches = self._create_batches_for_bark(message_content)
        
        return batches
    
    def _remove_duplicates(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """去除重复内容"""
        if not report_data.get("new_titles"):
            return report_data
        
        filtered_report_data = report_data.copy()
        filtered_new_titles = []
        
        for source_data in report_data["new_titles"]:
            filtered_titles = []
            
            for title_data in source_data["titles"]:
                title = title_data.get("title", "")
                platform = source_data["source_name"]
                
                # 检查重复
                is_unique = self.duplicate_detector.add_content(title, platform, title_data)
                
                if is_unique:
                    filtered_titles.append(title_data)
            
            if filtered_titles:  # 只保留有内容的平台
                filtered_source_data = source_data.copy()
                filtered_source_data["titles"] = filtered_titles
                filtered_new_titles.append(filtered_source_data)
        
        filtered_report_data["new_titles"] = filtered_new_titles
        
        # 更新统计信息
        if filtered_report_data.get("stats"):
            # 可以在这里更新统计信息，确保只包含去重后的内容
            pass
        
        return filtered_report_data
    
    def _build_message_content(self, report_data: Dict[str, Any], now: datetime, 
                              update_info: Optional[Dict[str, str]] = None) -> str:
        """构建消息内容"""
        content_parts = []
        
        # 添加头部信息
        content_parts.append(self._format_header(report_data, now))
        
        # 添加去重摘要（如果启用）
        if self.enable_duplicate_detection and self.duplicate_detector:
            duplicate_summary = self.duplicate_detector.get_duplicate_summary()
            content_parts.append(duplicate_summary)
            content_parts.append("---\n")
        
        # 添加热点词汇统计表格
        if report_data.get("stats"):
            stats_table = self._format_stats_table(report_data["stats"])
            content_parts.append(stats_table)
            content_parts.append("")
        
        # 添加新增热点新闻
        if report_data.get("new_titles"):
            news_section = self._format_news_section(report_data["new_titles"])
            content_parts.append(news_section)
        
        # 添加失败平台信息
        if report_data.get("failed_ids"):
            failed_section = self._format_failed_section(report_data["failed_ids"])
            content_parts.append(failed_section)
        
        # 添加重复内容详情（如果有且启用）
        if self.enable_duplicate_detection and self.duplicate_detector:
            duplicate_details = self.duplicate_detector.get_duplicate_details()
            if "未发现重复内容" not in duplicate_details:
                content_parts.append("---\n")
                content_parts.append(duplicate_details)
        
        # 添加底部信息
        content_parts.append(self._format_footer(now, update_info))
        
        return "\n\n".join(content_parts)
    
    def _format_header(self, report_data: Dict[str, Any], now: datetime) -> str:
        """格式化头部信息"""
        total_count = sum(len(source_data.get("titles", [])) 
                         for source_data in report_data.get("new_titles", []))
        
        header_parts = [
            "# 📰 TrendRadar 热点雷达",
            f"**推送时间:** {now.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**新闻总数:** {total_count} 条"
        ]
        
        return "\n".join(header_parts)
    
    def _format_stats_table(self, stats: List[Dict[str, Any]]) -> str:
        """格式化统计表格"""
        if not stats:
            return ""
        
        # 构建Markdown表格
        table_parts = [
            "## 📊 热点词汇统计",
            "",
            "| 排名 | 热点词汇 | 出现次数 | 平台分布 |",
            "|------|----------|----------|----------|"
        ]
        
        for i, stat in enumerate(stats[:10], 1):  # 限制显示前10个
            word = stat.get("word", "")
            count = stat.get("count", 0)
            platforms = " ".join(stat.get("platforms", []))
            
            # 截断过长的内容
            platforms = platforms[:20] + "..." if len(platforms) > 20 else platforms
            
            table_parts.append(f"| {i} | **{word}** | {count} | {platforms} |")
        
        return "\n".join(table_parts)
    
    def _format_news_section(self, new_titles: List[Dict[str, Any]]) -> str:
        """格式化新闻板块"""
        if not new_titles:
            return ""
        
        news_parts = ["## 🆕 新增热点新闻"]
        
        for source_data in new_titles:
            source_name = source_data.get("source_name", "未知平台")
            titles = source_data.get("titles", [])
            
            if not titles:
                continue
            
            news_parts.append("")
            news_parts.append(f"### 📱 {source_name} ({len(titles)} 条)")
            
            # 构建该平台的表格
            news_parts.append("")
            news_parts.append("| 序号 | 新闻标题 | 热度 | 时间范围 |")
            news_parts.append("|------|----------|------|----------|")
            
            for i, title_data in enumerate(titles[:15], 1):  # 限制每个平台最多15条
                title = title_data.get("title", "")
                ranks = title_data.get("ranks", [])
                first_time = title_data.get("first_time", "")
                last_time = title_data.get("last_time", "")
                
                # 截断过长的标题
                title = title[:40] + "..." if len(title) > 40 else title
                if not title:
                    title = "标题获取失败"
                
                # 处理热度信息
                heat_info = ""
                if ranks:
                    try:
                        heat_info = f"#{min(ranks)}"
                    except (ValueError, TypeError):
                        heat_info = "N/A"
                else:
                    heat_info = "N/A"
                
                # 处理时间信息
                time_range = ""
                if first_time and last_time and first_time != last_time:
                    time_range = f"{first_time} ~ {last_time}"
                elif first_time:
                    time_range = first_time
                else:
                    time_range = "未知时间"
                
                news_parts.append(f"| {i} | {title} | {heat_info} | {time_range} |")
            
            if len(titles) > 15:
                news_parts.append(f"| ... | **还有 {len(titles) - 15} 条** | ... | ... |")
        
        return "\n".join(news_parts)
    
    def _format_failed_section(self, failed_ids: List[str]) -> str:
        """格式化失败板块"""
        if not failed_ids:
            return ""
        
        failed_parts = [
            "## ⚠️ 数据获取异常",
            "",
            "以下平台本次数据获取失败："
        ]
        
        for i, platform_id in enumerate(failed_ids, 1):
            failed_parts.append(f"{i}. `{platform_id}`")
        
        return "\n".join(failed_parts)
    
    def _format_footer(self, now: datetime, update_info: Optional[Dict[str, str]] = None) -> str:
        """格式化底部信息"""
        footer_parts = [
            "---",
            f"📡 **TrendRadar智能热点推送** | {now.strftime('%Y-%m-%d %H:%M:%S')}"
        ]
        
        if update_info:
            footer_parts.append(
                f"🔄 发现新版本 **{update_info['remote_version']}** (当前: {update_info['current_version']})"
            )
        
        return "\n".join(footer_parts)
    
    def _create_batches_for_bark(self, content: str, max_size: int = 3500) -> List[str]:
        """为Bark创建消息批次"""
        if len(content.encode('utf-8')) <= max_size:
            return [content]
        
        batches = []
        lines = content.split('\n')
        current_batch = ""
        batch_num = 1
        
        for line in lines:
            # 尝试添加当前行到批次
            test_batch = current_batch + ("\n" if current_batch else "") + line
            
            if len(test_batch.encode('utf-8')) <= max_size:
                current_batch = test_batch
            else:
                # 如果当前批次不为空，先保存
                if current_batch:
                    batches.append(self._add_batch_header(current_batch, batch_num))
                    batch_num += 1
                
                # 如果单行就超过限制，需要截断
                if len(line.encode('utf-8')) > max_size - 100:  # 预留头部空间
                    truncated_line = line[:max_size//4] + "...[内容过长已截断]"
                    batches.append(self._add_batch_header(truncated_line, batch_num))
                    batch_num += 1
                    current_batch = ""
                else:
                    current_batch = line
        
        # 添加最后一个批次
        if current_batch:
            batches.append(self._add_batch_header(current_batch, batch_num))
        
        return batches
    
    def _add_batch_header(self, content: str, batch_num: int) -> str:
        """添加批次头部"""
        header = f"📦 **[第 {batch_num} 部分]**"
        return f"{header}\n\n{content}" if content else header
    
    def get_duplicate_stats(self) -> Optional[Dict[str, Any]]:
        """获取去重统计信息"""
        if self.duplicate_detector:
            return self.duplicate_detector.get_stats_dict()
        return None
    
    def reset_duplicate_stats(self):
        """重置去重统计"""
        if self.duplicate_detector:
            self.duplicate_detector.reset_stats()