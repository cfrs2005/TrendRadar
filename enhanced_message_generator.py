"""
增强的消息内容生成器

支持AI增强和传统格式的消息生成
"""

from typing import Dict, List, Optional
from ai_message_formatter import prepare_enhanced_content_for_platform


def generate_enhanced_message_content(
    report_data: Dict,
    format_type: str,
    report_type: str,
    update_info: Optional[Dict] = None,
    mode: str = "daily"
) -> List[str]:
    """
    生成增强的消息内容
    
    Args:
        report_data: 报告数据
        format_type: 格式类型 (feishu, dingtalk, telegram, etc.)
        report_type: 报告类型
        update_info: 更新信息
        mode: 模式
        
    Returns:
        消息批次列表
    """
    # 检查是否启用AI增强
    if report_data.get('ai_enhanced', False):
        enhanced_message = report_data.get('enhanced_message', '')
        if enhanced_message:
            # 使用AI增强的消息
            platform_content = prepare_enhanced_content_for_platform(
                report_data, format_type, enhanced_message
            )
            
            # 添加头部信息
            header_content = generate_header_content(
                report_data, format_type, report_type, update_info, mode
            )
            
            # 添加尾部信息
            footer_content = generate_footer_content(
                report_data, format_type, update_info
            )
            
            full_message = f"{header_content}{platform_content}{footer_content}"
            
            # 根据平台分批
            return split_message_for_platform(full_message, format_type, report_data)
    
    # 使用传统格式
    return generate_traditional_message_content(
        report_data, format_type, report_type, update_info, mode
    )


def generate_header_content(
    report_data: Dict,
    format_type: str,
    report_type: str,
    update_info: Optional[Dict] = None,
    mode: str = "daily"
) -> str:
    """生成消息头部"""
    from main import get_beijing_time
    
    total_titles = sum(
        len(stat.get("titles", [])) for stat in report_data.get("stats", []) 
        if stat.get("count", 0) > 0
    )
    
    now = get_beijing_time()
    
    if format_type == "feishu":
        header_parts = []
        if report_data.get('ai_enhanced', False):
            ai_stats = report_data.get('ai_stats', {})
            original_count = ai_stats.get('original_count', total_titles)
            unique_count = ai_stats.get('unique_count', total_titles)
            removed_count = original_count - unique_count
            
            if removed_count > 0:
                header_parts.append(f"🤖 **AI智能去重**: {original_count} 条 → {unique_count} 条")
        
        header_parts.append(f"📊 **热点词汇统计**")
        return '\n'.join(header_parts) + '\n\n'
    
    elif format_type == "dingtalk":
        header_parts = []
        if report_data.get('ai_enhanced', False):
            ai_stats = report_data.get('ai_stats', {})
            original_count = ai_stats.get('original_count', total_titles)
            unique_count = ai_stats.get('unique_count', total_titles)
            removed_count = original_count - unique_count
            
            if removed_count > 0:
                header_parts.append(f"🤖 AI智能去重: {original_count} 条 → {unique_count} 条")
        
        header_parts.append(f"📊 热点词汇统计")
        return '\n'.join(header_parts) + '\n\n'
    
    elif format_type == "telegram":
        header_parts = []
        if report_data.get('ai_enhanced', False):
            ai_stats = report_data.get('ai_stats', {})
            original_count = ai_stats.get('original_count', total_titles)
            unique_count = ai_stats.get('unique_count', total_titles)
            removed_count = original_count - unique_count
            
            if removed_count > 0:
                header_parts.append(f"🤖 AI智能去重: {original_count} 条 → {unique_count} 条")
        
        header_parts.append(f"📊 热点词汇统计")
        return '\n'.join(header_parts) + '\n\n'
    
    # 其他平台使用传统头部
    return generate_traditional_header(report_data, format_type, report_type, update_info, mode)


def generate_footer_content(
    report_data: Dict,
    format_type: str,
    update_info: Optional[Dict] = None
) -> str:
    """生成消息尾部"""
    from main import get_beijing_time
    
    if format_type in ["feishu", "dingtalk", "telegram", "ntfy"]:
        footer_parts = []
        
        # AI增强统计
        if report_data.get('ai_enhanced', False):
            ai_stats = report_data.get('ai_stats', {})
            categories_count = ai_stats.get('categories_count', 0)
            if categories_count > 0:
                footer_parts.append(f"🏷️ **智能分类**: {categories_count} 个类别")
        
        # 版本更新信息
        if update_info:
            footer_parts.append(f"📢 TrendRadar 发现新版本 **{update_info['remote_version']}**，当前 **{update_info['current_version']}**")
        
        # 时间戳
        now = get_beijing_time()
        if format_type == "feishu":
            footer_parts.append(f"更新时间：{now.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            footer_parts.append(f"更新时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if footer_parts:
            return '\n\n' + '\n'.join(footer_parts)
    
    return ""


def split_message_for_platform(
    message: str,
    format_type: str,
    report_data: Dict
) -> List[str]:
    """根据平台特性分割消息"""
    from main import CONFIG
    
    # 获取平台特定的批次大小
    if format_type == "dingtalk":
        max_bytes = CONFIG.get("DINGTALK_BATCH_SIZE", 20000)
    elif format_type == "feishu":
        max_bytes = CONFIG.get("FEISHU_BATCH_SIZE", 29000)
    elif format_type == "ntfy":
        max_bytes = 3800
    elif format_type == "bark":
        max_bytes = CONFIG.get("BARK_BATCH_SIZE", 3600)
    elif format_type == "slack":
        max_bytes = CONFIG.get("SLACK_BATCH_SIZE", 4000)
    else:
        max_bytes = CONFIG.get("MESSAGE_BATCH_SIZE", 4000)
    
    # 如果消息不长，直接返回
    if len(message.encode('utf-8')) <= max_bytes:
        return [message]
    
    # 分割长消息
    batches = []
    lines = message.split('\n')
    current_batch = ""
    
    for line in lines:
        test_batch = current_batch + '\n' + line if current_batch else line
        
        if len(test_batch.encode('utf-8')) <= max_bytes:
            current_batch = test_batch
        else:
            if current_batch:
                batches.append(current_batch)
                current_batch = line
            else:
                # 单行太长，强制分割
                batches.append(line)
    
    if current_batch:
        batches.append(current_batch)
    
    return batches


def generate_traditional_message_content(
    report_data: Dict,
    format_type: str,
    report_type: str,
    update_info: Optional[Dict] = None,
    mode: str = "daily"
) -> List[str]:
    """生成传统格式的消息内容（保持兼容性）"""
    # 这里调用原有的消息生成逻辑
    # 为了简化，这里返回一个基本的传统格式
    stats = report_data.get("stats", [])
    
    total_titles = sum(
        len(stat.get("titles", [])) for stat in stats 
        if stat.get("count", 0) > 0
    )
    
    from main import get_beijing_time
    now = get_beijing_time()
    
    message_parts = []
    
    if format_type == "feishu":
        message_parts.append(f"📊 **热点词汇统计**")
        message_parts.append(f"**总新闻数**: {total_titles}")
        message_parts.append(f"**时间**: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        message_parts.append("---")
        
        # 添加各词组统计
        for stat in stats:
            if stat.get("count", 0) > 0:
                word = stat.get("word", "")
                count = stat.get("count", 0)
                percentage = stat.get("percentage", 0)
                
                message_parts.append(f"🔥 **{word}**: {count} 条 ({percentage:.1f}%)")
                
                # 添加前几条新闻
                titles = stat.get("titles", [])[:3]  # 只显示前3条
                for title_info in titles:
                    title = title_info.get("title", "")
                    source_name = title_info.get("source_name", "")
                    rank = title_info.get("rank", 99)
                    
                    if title:
                        rank_display = f"[{rank}]" if rank <= 5 else f"[{rank}]"
                        message_parts.append(f"  {rank_display} {source_name}: {title}")
                
                message_parts.append("")
    
    return ['\n'.join(message_parts)]


def generate_traditional_header(
    report_data: Dict,
    format_type: str,
    report_type: str,
    update_info: Optional[Dict] = None,
    mode: str = "daily"
) -> str:
    """生成传统格式的头部"""
    from main import get_beijing_time, CONFIG
    
    total_titles = sum(
        len(stat.get("titles", [])) for stat in report_data.get("stats", []) 
        if stat.get("count", 0) > 0
    )
    
    now = get_beijing_time()
    
    if format_type == "feishu":
        return f"📊 **热点词汇统计**\n\n"
    elif format_type == "dingtalk":
        return f"📊 热点词汇统计\n\n"
    elif format_type == "telegram":
        return f"📊 热点词汇统计\n\n"
    
    return ""