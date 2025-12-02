#!/usr/bin/env python3
"""
新闻内容增强功能测试脚本
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from news_enhancer import (
    NewsEnhancer, 
    enhance_news_data, 
    translate_hackernews_title,
    check_duplicate_content
)


def test_hackernews_translation():
    """测试 Hacker News 标题翻译功能"""
    print("🧪 测试 Hacker News 标题翻译功能")
    
    enhancer = NewsEnhancer()
    
    test_cases = [
        ("AI agents find $4.6M in blockchain smart contract exploits", "hackernews"),
        ("OpenAI releases new GPT-4 model with improved capabilities", "hackernews"), 
        ("Google announces new quantum computing breakthrough", "hackernews"),
        ("Microsoft Windows 11 gets new AI-powered features", "hackernews"),
        ("Apple reveals new iPhone with advanced camera system", "hackernews"),
        ("This is a regular Chinese title from other source", "weibo"),
    ]
    
    for title, source_id in test_cases:
        translated = enhancer.translate_hackernews_title(title, source_id)
        print(f"  📰 [{source_id}] {title}")
        if translated != title:
            print(f"     ➡️ {translated}")
        else:
            print(f"     ✅ (无需翻译)")
        print()


def test_duplicate_detection():
    """测试重复内容检测功能"""
    print("🧪 测试重复内容检测功能")
    
    enhancer = NewsEnhancer()
    
    # 模拟新闻数据
    test_data = {
        "hackernews": {
            "AI agents find $4.6M in blockchain smart contract exploits": {
                "ranks": [1],
                "url": "https://news.ycombinator.com/item?id=123",
                "mobileUrl": "https://news.ycombinator.com/item?id=123"
            },
            "OpenAI releases new GPT-4 model": {
                "ranks": [2],
                "url": "https://news.ycombinator.com/item?id=124", 
                "mobileUrl": "https://news.ycombinator.com/item?id=124"
            },
            "AI agents find $4.6M in blockchain exploits": {  # 类似重复内容
                "ranks": [3],
                "url": "https://news.ycombinator.com/item?id=125",
                "mobileUrl": "https://news.ycombinator.com/item?id=125"
            }
        },
        "zhihu": {
            "网警破获"AI换脸"侵入计算机案": {
                "ranks": [1],
                "url": "https://www.zhihu.com/question/123",
                "mobileUrl": "https://www.zhihu.com/question/123"
            }
        },
        "weibo": {
            "网警破获AI换脸非法侵入系统案": {  # 重复内容
                "ranks": [2],
                "url": "https://weibo.com/123",
                "mobileUrl": "https://weibo.com/123"
            },
            "网警破获"AI换脸"侵入计算机案": {  # 完全重复
                "ranks": [3],
                "url": "https://weibo.com/124", 
                "mobileUrl": "https://weibo.com/124"
            }
        }
    }
    
    # 模拟历史数据
    historical_data = {
        "bilibili-hot-search": {
            "网警破获AI换脸非法侵入系统案": {  # 历史重复内容
                "ranks": [1],
                "url": "https://bilibili.com/123",
                "mobileUrl": "https://bilibili.com/123"
            }
        }
    }
    
    print("  📊 原始数据统计:")
    for source_id, titles_data in test_data.items():
        print(f"    - {source_id}: {len(titles_data)} 条")
    
    print(f"\n  📈 历史数据统计:")
    for source_id, titles_data in historical_data.items():
        print(f"    - {source_id}: {len(titles_data)} 条")
    
    # 测试去重功能
    deduped_data, removed_items = enhancer.check_duplicate_content(test_data, historical_data)
    
    print(f"\n  🧹 去重结果:")
    for source_id, titles_data in deduped_data.items():
        print(f"    - {source_id}: {len(titles_data)} 条 (保留)")
    
    print(f"\n  🗑️  去除的内容:")
    for source_id, items in removed_items.items():
        print(f"    - {source_id}: {len(items)} 条")
        for title, item_info in items.items():
            reason = item_info["reason"]
            print(f"      • {title[:50]}... (原因: {reason})")
    
    return deduped_data, removed_items


def test_complete_enhancement():
    """测试完整的内容增强功能"""
    print("🧪 测试完整的内容增强功能")
    
    # 测试数据
    test_results = {
        "hackernews": {
            "AI agents find $4.6M in blockchain smart contract exploits": {
                "ranks": [1],
                "url": "https://news.ycombinator.com/item?id=123",
                "mobileUrl": "https://news.ycombinator.com/item?id=123"
            },
            "Google announces new quantum computing breakthrough": {
                "ranks": [2], 
                "url": "https://news.ycombinator.com/item?id=124",
                "mobileUrl": "https://news.ycombinator.com/item?id=124"
            }
        },
        "zhihu": {
            "网警破获"AI换脸"侵入计算机案": {
                "ranks": [1],
                "url": "https://www.zhihu.com/question/123",
                "mobileUrl": "https://www.zhihu.com/question/123"
            }
        }
    }
    
    # 模拟历史数据
    title_info = {
        "weibo": {
            "网警破获AI换脸非法侵入系统案": {
                "first_time": "10时54分",
                "last_time": "12时27分", 
                "count": 3
            }
        }
    }
    
    print("  📊 增强前数据:")
    for source_id, titles_data in test_results.items():
        print(f"    - {source_id}: {len(titles_data)} 条")
    
    # 执行内容增强
    enhanced_results, removed_items = enhance_news_data(test_results, title_info)
    
    print(f"\n  🚀 增强后数据:")
    for source_id, titles_data in enhanced_results.items():
        print(f"    - {source_id}: {len(titles_data)} 条")
        for title in titles_data.keys():
            print(f"      • {title}")
            # 检查是否有原始标题字段
            if "original_title" in titles_data[title]:
                print(f"        (原标题: {titles_data[title]['original_title']})")
    
    print(f"\n  🗑️  去除内容:")
    for source_id, items in removed_items.items():
        print(f"    - {source_id}: {len(items)} 条")
    
    return enhanced_results, removed_items


def main():
    """主测试函数"""
    print("🧪 新闻内容增强功能测试")
    print("=" * 50)
    
    # 检查环境变量
    claude_token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
    if claude_token:
        print(f"✅ 检测到 Claude Token (长度: {len(claude_token)})")
        print("   将启用 AI 增强功能")
    else:
        print("⚠️  未检测到 Claude Token")
        print("   将使用简单的词典翻译功能")
    
    print(f"\n⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n" + "=" * 50)
    
    # 运行测试
    try:
        test_hackernews_translation()
        print("\n" + "-" * 50)
        
        test_duplicate_detection()
        print("\n" + "-" * 50)
        
        test_complete_enhancement()
        
        print("\n" + "=" * 50)
        print("🎉 所有测试完成!")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)