"""
AI 增强服务

使用大模型进行智能去重、内容聚类和总结
"""

import os
import json
import hashlib
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict
import requests


class AIEnhancedService:
    """AI 增强服务类"""
    
    def __init__(self):
        """初始化 AI 增强服务"""
        self.token = os.environ.get('CLAUDE_CODE_OAUTH_TOKEN')
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
    def _generate_content_hash(self, title: str) -> str:
        """生成内容哈希用于去重"""
        # 清理标题，移除时间戳、排名等变化部分
        cleaned_title = self._clean_title_for_hash(title)
        return hashlib.md5(cleaned_title.encode()).hexdigest()[:8]
    
    def _clean_title_for_hash(self, title: str) -> str:
        """清理标题，移除变化的部分"""
        import re
        # 移除数字和时间信息
        cleaned = re.sub(r'\d+', '', title)
        # 移除特殊字符，保留中文、英文、数字
        cleaned = re.sub(r'[^\w\s\u4e00-\u9fff]', '', cleaned)
        # 转换为小写并移除多余空格
        cleaned = ' '.join(cleaned.lower().split())
        return cleaned
    
    def _call_claude_api(self, prompt: str, max_tokens: int = 4000) -> Optional[str]:
        """调用 Claude API"""
        if not self.token:
            print("警告：未设置 CLAUDE_CODE_OAUTH_TOKEN 环境变量，跳过 AI 增强")
            return None
            
        try:
            payload = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": max_tokens,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("content", [{}])[0].get("text", "")
            else:
                print(f"API 调用失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"调用 Claude API 时出错: {e}")
            return None
    
    def deduplicate_news(self, news_items: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        智能去重新闻
        
        Args:
            news_items: 新闻列表
            
        Returns:
            (去重后的新闻列表, 重复信息统计)
        """
        if not news_items:
            return [], {}
            
        # 首先进行基于哈希的快速去重
        seen_hashes = {}
        unique_items = []
        duplicate_groups = defaultdict(list)
        
        for item in news_items:
            content_hash = self._generate_content_hash(item['title'])
            
            if content_hash in seen_hashes:
                # 添加到重复组
                existing_item = seen_hashes[content_hash]
                duplicate_key = f"{content_hash}_{existing_item['title'][:20]}"
                duplicate_groups[duplicate_key].append({
                    'original': existing_item,
                    'duplicate': item,
                    'similarity': self._calculate_text_similarity(
                        existing_item['title'], item['title']
                    )
                })
            else:
                seen_hashes[content_hash] = item
                unique_items.append(item)
        
        # 使用 AI 进一步优化去重结果
        if len(unique_items) > 1:
            unique_items = self._ai_deduplicate(unique_items)
            
        duplicate_stats = {
            'original_count': len(news_items),
            'unique_count': len(unique_items),
            'removed_count': len(news_items) - len(unique_items),
            'duplicate_groups': dict(duplicate_groups)
        }
        
        return unique_items, duplicate_stats
    
    def _ai_deduplicate(self, news_items: List[Dict]) -> List[Dict]:
        """使用 AI 进行更精确的去重"""
        # 如果新闻数量较少，直接返回
        if len(news_items) <= 5:
            return news_items
            
        # 构建新闻标题列表
        titles = [item['title'] for item in news_items]
        
        prompt = f"""
请分析以下新闻标题，识别并合并相似或重复的内容。返回去重后的标题索引列表。

新闻标题列表：
{json.dumps(titles, ensure_ascii=False, indent=2)}

请返回一个JSON格式的结果，包含：
1. "unique_indices": 保留的新闻标题索引列表（从0开始）
2. "reason": 简要说明去重的理由

示例返回格式：
{{
    "unique_indices": [0, 2, 4, 7],
    "reason": "去除了内容相似的重复报道"
}}

注意：
- 保留最重要、信息最完整的标题
- 同一事件的不同角度报道可以适当保留
- 优先保留排名较高的新闻
"""

        response = self._call_claude_api(prompt)
        if not response:
            return news_items
            
        try:
            # 解析 AI 响应
            result = json.loads(response)
            if 'unique_indices' in result:
                unique_indices = result['unique_indices']
                # 确保索引有效
                unique_indices = [i for i in unique_indices if 0 <= i < len(news_items)]
                return [news_items[i] for i in unique_indices]
        except (json.JSONDecodeError, KeyError) as e:
            print(f"解析 AI 去重结果时出错: {e}")
            
        return news_items
    
    def categorize_and_summarize(self, news_items: List[Dict]) -> Dict:
        """
        对新闻进行分类和总结
        
        Args:
            news_items: 新闻列表
            
        Returns:
            分类和总结结果
        """
        if not news_items:
            return {'categories': {}, 'summary': '', 'total_count': 0}
            
        # 按平台分组
        platform_groups = defaultdict(list)
        for item in news_items:
            platform_groups[item['platform_name']].append(item)
        
        # 构建分类提示
        news_content = []
        for i, item in enumerate(news_items):
            news_content.append(f"{i+1}. [{item['platform_name']}] {item['title']}")
        
        prompt = f"""
请对以下新闻进行智能分类和总结分析：

新闻内容：
{chr(10).join(news_content)}

请提供以下分析结果，返回JSON格式：

{{
    "categories": [
        {{
            "name": "分类名称",
            "count": 数量,
            "items": [索引1, 索引2, ...],
            "description": "简短描述"
        }}
    ],
    "summary": "整体总结，突出重要信息和趋势",
    "trending_topics": ["热门话题1", "热门话题2", ...],
    "key_insights": ["关键洞察1", "关键洞察2", ...]
}}

分类要求：
- 按内容主题分类（如科技、财经、社会等）
- 每个分类包含2-8条新闻
- 突出重要和热门的话题
- 总结要简洁明了，突出关键信息
"""

        response = self._call_claude_api(prompt, max_tokens=6000)
        if not response:
            # 返回基础分类结果
            return self._basic_categorization(news_items, platform_groups)
            
        try:
            result = json.loads(response)
            
            # 添加平台统计信息
            result['platform_stats'] = {
                name: len(items) for name, items in platform_groups.items()
            }
            result['total_count'] = len(news_items)
            
            return result
        except (json.JSONDecodeError, KeyError) as e:
            print(f"解析 AI 分类结果时出错: {e}")
            return self._basic_categorization(news_items, platform_groups)
    
    def _basic_categorization(self, news_items: List[Dict], platform_groups: Dict) -> Dict:
        """基础分类功能（AI 不可用时的后备方案）"""
        # 按平台简单分类
        categories = []
        for platform_name, items in platform_groups.items():
            categories.append({
                'name': f'{platform_name} 平台',
                'count': len(items),
                'items': [news_items.index(item) for item in items],
                'description': f'来自{platform_name}的新闻'
            })
        
        return {
            'categories': categories,
            'summary': f'共收集到 {len(news_items)} 条新闻，来自 {len(platform_groups)} 个平台。',
            'trending_topics': [],
            'key_insights': [],
            'platform_stats': {name: len(items) for name, items in platform_groups.items()},
            'total_count': len(news_items)
        }
    
    def generate_enhanced_message(self, news_items: List[Dict], categorization_result: Dict, duplicate_stats: Dict) -> str:
        """
        生成增强的推送消息
        
        Args:
            news_items: 去重后的新闻列表
            categorization_result: 分类结果
            duplicate_stats: 去重统计
            
        Returns:
            格式化的推送消息
        """
        if not categorization_result:
            return self._generate_basic_message(news_items)
            
        message_parts = []
        
        # 添加头部信息
        total_original = duplicate_stats.get('original_count', len(news_items))
        total_unique = duplicate_stats.get('unique_count', len(news_items))
        removed_count = duplicate_stats.get('removed_count', 0)
        
        if removed_count > 0:
            message_parts.append(f"🤖 **AI 智能去重**: {total_original} 条 → {total_unique} 条 (去除 {removed_count} 条重复)")
        
        # 添加总结
        summary = categorization_result.get('summary', '')
        if summary:
            message_parts.append(f"📝 **内容总结**: {summary}")
        
        # 添加热门话题
        trending_topics = categorization_result.get('trending_topics', [])
        if trending_topics:
            topics_str = '、'.join(trending_topics[:3])  # 最多显示3个
            message_parts.append(f"🔥 **热门话题**: {topics_str}")
        
        message_parts.append("━" * 25)
        
        # 添加分类新闻
        categories = categorization_result.get('categories', [])
        for i, category in enumerate(categories, 1):
            if i > 5:  # 限制显示5个分类
                break
                
            category_name = category['name']
            category_items = category['items'][:3]  # 每个分类最多显示3条
            
            message_parts.append(f"**[{i}] {category_name}** ({category['count']} 条)")
            
            for item_idx in category_items:
                if item_idx < len(news_items):
                    item = news_items[item_idx]
                    rank_display = self._format_rank(item.get('rank', 99))
                    platform_display = item.get('platform_name', item.get('platform', ''))
                    
                    # 保留 URL 信息
                    title = item['title']
                    url = item.get('url', '')
                    mobile_url = item.get('mobileUrl', '')
                    
                    # 格式化显示
                    if url:
                        # 如果有 URL，添加链接
                        title_with_link = f"[{title}]({url})"
                    else:
                        title_with_link = title
                    
                    message_parts.append(
                        f"  {rank_display} {platform_display}: {title_with_link}"
                    )
            
            message_parts.append("")  # 分类间空行
        
        # 添加统计信息
        platform_stats = categorization_result.get('platform_stats', {})
        if platform_stats:
            stats_str = ', '.join([f"{name}({count})" for name, count in platform_stats.items()])
            message_parts.append(f"📊 **平台分布**: {stats_str}")
        
        return '\n'.join(message_parts)
    
    def _generate_basic_message(self, news_items: List[Dict]) -> str:
        """生成基础消息（AI 不可用时）"""
        if not news_items:
            return "暂无新闻"
            
        message_parts = ["📊 **热点新闻汇总**"]
        
        # 按平台分组显示
        platform_groups = defaultdict(list)
        for item in news_items:
            platform_groups[item.get('platform_name', item.get('platform', ''))].append(item)
        
        for platform_name, items in platform_groups.items():
            message_parts.append(f"\n**{platform_name}**")
            for item in items[:5]:  # 每个平台最多5条
                rank_display = self._format_rank(item.get('rank', 99))
                title = item['title']
                url = item.get('url', '')
                
                if url:
                    title_with_link = f"[{title}]({url})"
                else:
                    title_with_link = title
                    
                message_parts.append(f"  {rank_display} {title_with_link}")
        
        return '\n'.join(message_parts)
    
    def _format_rank(self, rank: int) -> str:
        """格式化排名显示"""
        if rank <= 5:
            return f"**[{rank}]**"
        else:
            return f"[{rank}]"
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def is_enabled(self) -> bool:
        """检查 AI 增强服务是否可用"""
        return bool(self.token)