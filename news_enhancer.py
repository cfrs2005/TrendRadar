#!/usr/bin/env python3
"""
新闻内容增强处理器
实现 Hacker News 标题汉化和内容去重功能
"""

import re
import hashlib
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class NewsEnhancer:
    """新闻内容增强器"""
    
    def __init__(self):
        self.clude_token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
        self.enable_ai = bool(self.clude_token)
        
        # 简单的英文到中文翻译词典（用于常见的 Hacker News 标题词汇）
        self.translation_dict = {
            # 技术术语
            "AI": "人工智能", "API": "接口", "algorithm": "算法", "artificial": "人工", 
            "blockchain": "区块链", "bug": "漏洞", "code": "代码", "coding": "编程",
            "cybersecurity": "网络安全", "data": "数据", "database": "数据库",
            "debug": "调试", "development": "开发", "devops": "运维开发",
            "encryption": "加密", "framework": "框架", "git": "Git", "github": "GitHub",
            "hacker": "黑客", "hardware": "硬件", "internet": "互联网", "javascript": "JavaScript",
            "linux": "Linux", "machine": "机器", "malware": "恶意软件", "network": "网络",
            "open source": "开源", "programming": "编程", "python": "Python", "quantum": "量子",
            "repository": "仓库", "security": "安全", "server": "服务器", "software": "软件",
            "system": "系统", "technology": "技术", "testing": "测试", "tool": "工具",
            "update": "更新", "version": "版本", "vulnerability": "漏洞", "web": "网络",
            "website": "网站", "windows": "Windows", "app": "应用", "application": "应用程序",
            
            # 动作词
            "released": "发布", "launched": "推出", "announced": "宣布", "updated": "更新",
            "fixed": "修复", "improved": "改进", "added": "添加", "removed": "移除",
            "changed": "改变", "created": "创建", "developed": "开发", "designed": "设计",
            "built": "构建", "implemented": "实现", "discovered": "发现", "found": "发现",
            "reported": "报告", "revealed": "揭示", "showed": "显示", "tested": "测试",
            "analyzed": "分析", "compared": "比较", "reviewed": "审查", "evaluated": "评估",
            
            # 描述词
            "new": "新", "latest": "最新", "popular": "热门", "trending": "趋势", "viral": "病毒式",
            "free": "免费", "open": "开放", "closed": "关闭", "public": "公共", "private": "私有",
            "secure": "安全", "insecure": "不安全", "fast": "快速", "slow": "慢速",
            "easy": "简单", "complex": "复杂", "powerful": "强大", "useful": "有用",
            "better": "更好", "worse": "更差", "best": "最佳", "worst": "最差",
            "big": "大", "small": "小", "large": "大型", "tiny": "微小", "huge": "巨大",
            
            # 数字单位
            "million": "百万", "billion": "十亿", "trillion": "万亿", "k": "千", "m": "百万",
            
            # 公司名称
            "google": "谷歌", "microsoft": "微软", "apple": "苹果", "amazon": "亚马逊",
            "facebook": "Facebook", "meta": "Meta", "twitter": "Twitter", "tesla": "特斯拉",
            "netflix": "Netflix", "adobe": "Adobe", "oracle": "甲骨文", "samsung": "三星",
            "intel": "英特尔", "nvidia": "英伟达", "amd": "AMD", "ibm": "IBM",
            
            # 其他常见词
            "apple": "苹果", "iphone": "iPhone", "android": "安卓", "phone": "手机",
            "computer": "电脑", "laptop": "笔记本电脑", "desktop": "台式机",
            "browser": "浏览器", "chrome": "Chrome", "firefox": "Firefox", "safari": "Safari",
            "email": "邮件", "message": "消息", "chat": "聊天", "social": "社交",
            "media": "媒体", "video": "视频", "audio": "音频", "image": "图片",
            "photo": "照片", "file": "文件", "document": "文档", "text": "文本",
            "game": "游戏", "play": "玩", "player": "播放器", "music": "音乐",
            "movie": "电影", "book": "书", "news": "新闻", "article": "文章",
            "blog": "博客", "post": "帖子", "comment": "评论", "reply": "回复",
            "user": "用户", "account": "账户", "login": "登录", "password": "密码",
            "name": "名称", "title": "标题", "content": "内容", "page": "页面",
            "site": "网站", "link": "链接", "url": "网址", "address": "地址",
            "location": "位置", "place": "地方", "country": "国家", "city": "城市",
            "time": "时间", "date": "日期", "year": "年", "month": "月", "day": "天",
            "hour": "小时", "minute": "分钟", "second": "秒", "today": "今天", "yesterday": "昨天",
            "tomorrow": "明天", "now": "现在", "future": "未来", "past": "过去"
        }
    
    def translate_hackernews_title(self, title: str, source_id: str) -> str:
        """
        翻译 Hacker News 标题
        """
        if source_id != "hackernews":
            return title
        
        if not self.enable_ai:
            # 如果没有启用AI，使用简单的词典翻译
            return self._simple_translate(title)
        
        # 如果启用了AI，可以在这里调用大模型进行翻译
        # 目前暂时使用简单翻译
        return self._simple_translate(title)
    
    def _simple_translate(self, title: str) -> str:
        """
        简单的词典翻译
        """
        # 将标题转换为小写进行匹配
        title_lower = title.lower()
        
        # 替换词典中的词汇
        translated_title = title
        for en_word, zh_word in self.translation_dict.items():
            # 使用正则表达式进行单词边界匹配
            pattern = r'\b' + re.escape(en_word) + r'\b'
            translated_title = re.sub(pattern, zh_word, translated_title, flags=re.IGNORECASE)
        
        return translated_title
    
    def generate_content_hash(self, title: str, source_id: str) -> str:
        """
        生成内容哈希值用于去重
        """
        # 标准化标题：去除标点符号、转小写
        normalized_title = re.sub(r'[^\w\s]', '', title.lower())
        
        # 生成哈希
        content = f"{source_id}:{normalized_title}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def check_duplicate_content(self, all_results: Dict, title_info: Optional[Dict] = None) -> Tuple[Dict, Dict]:
        """
        检查并去除重复内容
        """
        seen_hashes = {}
        deduped_results = {}
        removed_items = {}
        total_removed = 0
        
        # 如果有历史title_info，先添加到seen_hashes中
        if title_info:
            for source_id, titles in title_info.items():
                for title in titles:
                    content_hash = self.generate_content_hash(title, source_id)
                    # 标记历史内容为已推送
                    seen_hashes[content_hash] = "historical"
        
        # 处理当前结果
        for source_id, titles_data in all_results.items():
            deduped_results[source_id] = {}
            
            for title, title_data in titles_data.items():
                content_hash = self.generate_content_hash(title, source_id)
                
                if content_hash in seen_hashes:
                    # 发现重复内容
                    if source_id not in removed_items:
                        removed_items[source_id] = {}
                    removed_items[source_id][title] = {
                        "title_data": title_data,
                        "reason": seen_hashes[content_hash]  # "historical" 或 "current"
                    }
                    total_removed += 1
                else:
                    # 保留不重复的内容
                    deduped_results[source_id][title] = title_data
                    seen_hashes[content_hash] = "current"
        
        print(f"🤖 智能去重: 原始内容 {sum(len(titles) for titles in all_results.values())} 条 → 去重后 {sum(len(titles) for titles in deduped_results.values())} 条 (去除 {total_removed} 条重复)")
        
        if removed_items:
            print(f"📋 去重详情: 各平台去除重复内容数量")
            for source_id, items in removed_items.items():
                if items:
                    print(f"  - {source_id}: 去除 {len(items)} 条")
        
        return deduped_results, removed_items
    
    def enhance_news_data(self, all_results: Dict, title_info: Optional[Dict] = None) -> Tuple[Dict, Dict]:
        """
        增强新闻数据：翻译 Hacker News 标题并去重
        """
        print(f"🚀 开始内容增强处理...")
        
        # 第一步：去重
        deduped_results, removed_items = self.check_duplicate_content(all_results, title_info)
        
        # 第二步：翻译 Hacker News 标题
        enhanced_results = {}
        translated_count = 0
        
        for source_id, titles_data in deduped_results.items():
            enhanced_results[source_id] = {}
            
            for title, title_data in titles_data.items():
                translated_title = self.translate_hackernews_title(title, source_id)
                
                # 如果标题被翻译了，更新标题
                if translated_title != title:
                    # 更新标题数据
                    enhanced_title_data = title_data.copy()
                    enhanced_title_data["original_title"] = title  # 保留原始标题
                    enhanced_results[source_id][translated_title] = enhanced_title_data
                    translated_count += 1
                else:
                    enhanced_results[source_id][title] = title_data
        
        if translated_count > 0:
            print(f"🈯️ Hacker News 标题翻译: 翻译了 {translated_count} 个标题")
        
        print(f"✅ 内容增强完成")
        
        return enhanced_results, removed_items


# 全局实例
_news_enhancer = NewsEnhancer()


def enhance_news_data(all_results: Dict, title_info: Optional[Dict] = None) -> Tuple[Dict, Dict]:
    """
    全局函数：增强新闻数据
    """
    return _news_enhancer.enhance_news_data(all_results, title_info)


def translate_hackernews_title(title: str, source_id: str) -> str:
    """
    全局函数：翻译 Hacker News 标题
    """
    return _news_enhancer.translate_hackernews_title(title, source_id)


def check_duplicate_content(all_results: Dict, title_info: Optional[Dict] = None) -> Tuple[Dict, Dict]:
    """
    全局函数：检查重复内容
    """
    return _news_enhancer.check_duplicate_content(all_results, title_info)