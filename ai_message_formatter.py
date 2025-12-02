"""
AI增强的消息格式化器

提供智能去重和内容分类总结功能
"""

from typing import Dict, List, Optional
from ai_enhanced_service import AIEnhancedService


def format_message_with_ai_enhancement(
    report_data: Dict,
    mode: str = "daily",
    enable_ai: bool = True
) -> Dict:
    """
    使用AI增强功能格式化消息
    
    Args:
        report_data: 原始报告数据
        mode: 报告模式
        enable_ai: 是否启用AI功能
        
    Returns:
        增强后的报告数据
    """
    if not enable_ai:
        return report_data
    
    ai_service = AIEnhancedService()
    if not ai_service.is_enabled():
        print("🤖 AI增强功能未启用，使用原始格式")
        return report_data
    
    print("🤖 应用AI智能增强...")
    
    # 提取所有新闻项
    all_news_items = extract_news_items(report_data)
    
    if not all_news_items:
        print("📝 没有找到新闻项，使用原始格式")
        return report_data
    
    # AI智能去重
    unique_news, duplicate_stats = ai_service.deduplicate_news(all_news_items)
    
    # AI分类和总结
    categorization_result = ai_service.categorize_and_summarize(unique_news)
    
    # 生成增强消息
    enhanced_message = ai_service.generate_enhanced_message(
        unique_news, categorization_result, duplicate_stats
    )
    
    # 创建增强的报告数据
    enhanced_report_data = {
        **report_data,
        'ai_enhanced': True,
        'ai_stats': {
            'original_count': len(all_news_items),
            'unique_count': len(unique_news),
            'duplicate_removed': len(all_news_items) - len(unique_news),
            'categories_count': len(categorization_result.get('categories', [])),
        },
        'enhanced_message': enhanced_message,
        'categorization': categorization_result,
        'duplicate_stats': duplicate_stats
    }
    
    print(f"📊 AI增强完成: {len(all_news_items)} → {len(unique_news)} 条新闻")
    print(f"🏷️ 分类数量: {len(categorization_result.get('categories', []))}")
    
    return enhanced_report_data


def extract_news_items(report_data: Dict) -> List[Dict]:
    """
    从报告数据中提取所有新闻项
    
    Args:
        report_data: 报告数据
        
    Returns:
        新闻项列表
    """
    news_items = []
    stats = report_data.get('stats', [])
    
    for stat in stats:
        if stat.get('count', 0) > 0:
            titles = stat.get('titles', [])
            for title_info in titles:
                # 构建新闻项
                news_item = {
                    'title': title_info.get('title', ''),
                    'platform': title_info.get('platform', ''),
                    'platform_name': title_info.get('source_name', ''),
                    'rank': title_info.get('rank', 99),
                    'url': title_info.get('url', ''),
                    'mobileUrl': title_info.get('mobile_url', ''),
                    'is_new': title_info.get('is_new', False),
                    'count': title_info.get('count', 1),
                    'ranks': title_info.get('ranks', []),
                    'word_group': stat.get('word', '')
                }
                
                if news_item['title']:  # 只添加有标题的新闻
                    news_items.append(news_item)
    
    return news_items


def prepare_enhanced_content_for_platform(
    enhanced_report_data: Dict,
    platform: str = "feishu",
    original_content: str = ""
) -> str:
    """
    为特定平台准备增强内容
    
    Args:
        enhanced_report_data: 增强的报告数据
        platform: 平台名称
        original_content: 原始内容
        
    Returns:
        格式化后的内容
    """
    if not enhanced_report_data.get('ai_enhanced', False):
        return original_content
    
    enhanced_message = enhanced_report_data.get('enhanced_message', '')
    if not enhanced_message:
        return original_content
    
    # 根据平台进行格式调整
    if platform == "feishu":
        # 飞书支持Markdown格式
        return enhanced_message
    elif platform == "dingtalk":
        # 钉钉支持Markdown格式
        return enhanced_message
    elif platform == "wework":
        # 企业微信支持Markdown格式
        return enhanced_message
    elif platform == "telegram":
        # Telegram支持Markdown格式
        return enhanced_message
    elif platform == "email":
        # 邮件使用HTML格式，需要转换
        return convert_markdown_to_html(enhanced_message)
    elif platform == "slack":
        # Slack需要特殊格式
        return format_for_slack(enhanced_message)
    elif platform == "bark":
        # Bark只支持纯文本
        return convert_markdown_to_plain_text(enhanced_message)
    elif platform == "ntfy":
        # ntfy支持Markdown
        return enhanced_message
    else:
        # 默认使用原始内容
        return original_content


def convert_markdown_to_html(markdown_text: str) -> str:
    """简单的Markdown到HTML转换"""
    if not markdown_text:
        return ""
        
    # 简单的替换规则
    html = markdown_text
    
    # 粗体
    html = html.replace('**', '<strong>').replace('**', '</strong>')
    
    # 链接
    import re
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
    
    # 换行
    html = html.replace('\n', '<br>')
    
    return html


def convert_markdown_to_plain_text(markdown_text: str) -> str:
    """Markdown到纯文本转换"""
    if not markdown_text:
        return ""
        
    # 简单的替换规则
    plain = markdown_text
    
    # 移除Markdown格式
    plain = plain.replace('**', '')
    plain = plain.replace('*', '')
    
    # 链接转换
    import re
    plain = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1', plain)
    
    return plain


def format_for_slack(markdown_text: str) -> str:
    """为Slack格式化文本"""
    if not markdown_text:
        return ""
        
    # Slack使用mrkdwn格式
    slack_text = markdown_text
    
    # 粗体格式转换
    slack_text = slack_text.replace('**', '*')
    
    # 链接格式
    import re
    slack_text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<\2|\1>', slack_text)
    
    return slack_text