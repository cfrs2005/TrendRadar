# coding=utf-8

import json
import os
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import hashlib


class BigModelService:
    """BigModel AI 智能去重和内容分析服务"""
    
    def __init__(self):
        self.api_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        self.model = "glm-4.6"
        self.api_token = os.getenv("CLAUDE_CODE_OAUTH_TOKEN")
        
    def _hash_title(self, title: str) -> str:
        """生成标题的哈希值用于快速去重"""
        return hashlib.md5(title.encode('utf-8')).hexdigest()
    
    def _prepare_bigmodel_request(self, messages: List[Dict]) -> Dict:
        """准备 BigModel API 请求"""
        return {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 8192,
            "stream": False
        }
    
    def _call_bigmodel_api(self, messages: List[Dict]) -> Optional[Dict]:
        """调用 BigModel API"""
        if not self.api_token:
            print("⚠️  未设置 CLAUDE_CODE_OAUTH_TOKEN，跳过 AI 分析")
            return None
            
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        request_data = self._prepare_bigmodel_request(messages)
        
        try:
            response = requests.post(
                self.api_url, 
                headers=headers, 
                json=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ BigModel API 调用失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ BigModel API 调用异常: {str(e)}")
            return None
    
    def _parse_bigmodel_response(self, response: Dict) -> Dict:
        """解析 BigModel API 响应"""
        try:
            if "choices" in response and len(response["choices"]) > 0:
                content = response["choices"][0]["message"]["content"]
                # 尝试解析 JSON 内容
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # 如果不是 JSON 格式，返回文本内容
                    return {
                        "analysis": content,
                        "duplicate_indices": [],
                        "categories": {},
                        "hot_topics": [],
                        "summary": "AI 分析完成，但格式解析失败"
                    }
        except Exception as e:
            print(f"❌ BigModel 响应解析失败: {str(e)}")
            return {
                "analysis": "",
                "duplicate_indices": [],
                "categories": {},
                "hot_topics": [],
                "summary": "AI 响应解析失败"
            }
    
    def smart_deduplicate_and_analyze(
        self, 
        titles_data: List[Dict]
    ) -> Tuple[List[Dict], Dict]:
        """
        智能去重和内容分析
        
        Args:
            titles_data: 包含标题信息的字典列表
            每个字典包含: title, source_name, url, mobile_url, ranks, is_new
            
        Returns:
            Tuple[去重后的标题列表, 分析结果字典]
        """
        if not self.api_token:
            # 降级到基础哈希去重
            return self._basic_deduplicate(titles_data), {}
        
        # 第一步：基础哈希去重
        hash_deduplicated = self._basic_deduplicate(titles_data)
        
        # 第二步：AI 语义去重和分析
        return self._ai_smart_analysis(hash_deduplicated)
    
    def _basic_deduplicate(self, titles_data: List[Dict]) -> List[Dict]:
        """基础哈希去重"""
        seen_hashes = set()
        deduplicated = []
        
        for item in titles_data:
            title = item.get("title", "")
            title_hash = self._hash_title(title)
            
            if title_hash not in seen_hashes:
                seen_hashes.add(title_hash)
                deduplicated.append(item)
        
        return deduplicated
    
    def _ai_smart_analysis(
        self, 
        titles_data: List[Dict]
    ) -> Tuple[List[Dict], Dict]:
        """AI 智能分析"""
        if not titles_data:
            return [], {}
        
        # 准备 AI 分析请求
        titles_text = "\n".join([
            f"{i+1}. {item.get('title', '')} (来源: {item.get('source_name', '')})"
            for i, item in enumerate(titles_data)
        ])
        
        system_prompt = """你是一个专业的新闻内容分析师。请对以下新闻标题进行智能分析：

1. 识别重复或高度相似的新闻标题，返回需要去重的标题索引
2. 对新闻进行分类（如：科技、财经、社会、国际、体育、娱乐等）
3. 提取热门话题和关键事件
4. 生成简要的内容总结

请严格按照以下 JSON 格式返回：
{
    "duplicate_indices": [1, 3, 5],
    "categories": {
        "科技": [2, 4, 7],
        "财经": [6, 8],
        "社会": [1, 9]
    },
    "hot_topics": ["AI发展", "经济政策", "科技创新"],
    "summary": "今日新闻主要集中在科技创新和经济发展方面..."
}

注意：
- duplicate_indices: 需要移除的重复标题索引（从1开始计数）
- categories: 分类名称和对应的标题索引列表
- hot_topics: 3-5个热门话题
- summary: 50字以内的内容总结"""

        user_prompt = f"""请分析以下新闻标题：

{titles_text}

请返回 JSON 格式的分析结果。"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # 调用 AI API
        api_response = self._call_bigmodel_api(messages)
        
        if not api_response:
            # API 失败时返回原始数据
            return titles_data, {}
        
        # 解析 AI 响应
        analysis_result = self._parse_bigmodel_response(api_response)
        
        # 根据 AI 分析结果去重
        duplicate_indices = set(analysis_result.get("duplicate_indices", []))
        
        # 保留未被标记为重复的标题
        deduplicated_titles = [
            title for i, title in enumerate(titles_data) 
            if (i + 1) not in duplicate_indices  # AI 索引从1开始
        ]
        
        # 添加分类信息到标题数据中
        categories = analysis_result.get("categories", {})
        for category, indices in categories.items():
            for idx in indices:
                if 1 <= idx <= len(deduplicated_titles):
                    # 找到对应的标题（需要考虑去重后的索引变化）
                    original_idx = idx - 1
                    if original_idx < len(titles_data):
                        # 在去重后的列表中找到这个标题
                        for title_item in deduplicated_titles:
                            if title_item.get("title") == titles_data[original_idx].get("title"):
                                title_item["ai_category"] = category
                                break
        
        # 添加统计信息
        original_count = len(titles_data)
        deduplicated_count = len(deduplicated_titles)
        
        analysis_result.update({
            "original_count": original_count,
            "deduplicated_count": deduplicated_count,
            "removed_count": original_count - deduplicated_count,
            "deduplication_rate": f"{((original_count - deduplicated_count) / original_count * 100):.1f}%" if original_count > 0 else "0%"
        })
        
        return deduplicated_titles, analysis_result
    
    def format_ai_enhanced_message(self, titles_data: List[Dict], analysis_result: Dict) -> str:
        """格式化 AI 增强的消息"""
        if not analysis_result:
            return ""
        
        message_parts = []
        
        # 去重统计
        original_count = analysis_result.get("original_count", 0)
        deduplicated_count = analysis_result.get("deduplicated_count", 0) 
        removed_count = analysis_result.get("removed_count", 0)
        deduplication_rate = analysis_result.get("deduplication_rate", "0%")
        
        if removed_count > 0:
            message_parts.append(
                f"🤖 **AI智能去重**: {original_count}条 → {deduplicated_count}条 "
                f"(去除{removed_count}条重复，去重率{deduplication_rate})"
            )
        
        # 内容总结
        summary = analysis_result.get("summary", "")
        if summary:
            message_parts.append(f"📝 **内容总结**: {summary}")
        
        # 热门话题
        hot_topics = analysis_result.get("hot_topics", [])
        if hot_topics:
            topics_text = "、".join(hot_topics[:5])  # 最多显示5个
            message_parts.append(f"🔥 **热门话题**: {topics_text}")
        
        # 分类统计
        categories = analysis_result.get("categories", {})
        if categories:
            category_stats = []
            for category, indices in categories.items():
                count = len(indices)
                if count > 0:
                    category_stats.append(f"{category}{count}条")
            
            if category_stats:
                stats_text = "、".join(category_stats)
                message_parts.append(f"🏷️ **智能分类**: {stats_text}")
        
        # 平台统计
        platform_stats = {}
        for item in titles_data:
            source_name = item.get("source_name", "")
            platform_stats[source_name] = platform_stats.get(source_name, 0) + 1
        
        if platform_stats:
            platform_items = [f"{platform}({count})" for platform, count in sorted(platform_stats.items(), key=lambda x: x[1], reverse=True)[:8]]
            platforms_text = "、".join(platform_items)
            message_parts.append(f"📊 **平台分布**: {platforms_text}")
        
        return "\n\n" + "\n".join(message_parts) if message_parts else ""