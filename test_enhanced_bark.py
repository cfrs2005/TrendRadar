#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试增强的Bark格式化器和去重功能
Test enhanced Bark formatter and duplicate detection functionality
"""

import sys
import os
from datetime import datetime
from enhanced_bark_formatter import EnhancedBarkFormatter


def test_enhanced_formatter():
    """测试增强的格式化器"""
    
    # 模拟测试数据
    test_report_data = {
        "new_titles": [
            {
                "source_name": "微博热搜",
                "titles": [
                    {
                        "title": "网警破获AI换脸非法侵入系统案",
                        "ranks": [1, 3, 6],
                        "first_time": "10时54分",
                        "last_time": "12时27分",
                        "url": "https://weibo.com/hot/1",
                        "mobileUrl": "https://m.weibo.com/hot/1"
                    },
                    {
                        "title": "ChatGPT推出新功能",
                        "ranks": [2, 5],
                        "first_time": "11时20分",
                        "last_time": "11时45分",
                        "url": "https://weibo.com/hot/2",
                        "mobileUrl": "https://m.weibo.com/hot/2"
                    },
                    {
                        "title": "   网警破获   AI换脸 非法侵入案  ",  # 测试标准化
                        "ranks": [8],
                        "first_time": "12时00分",
                        "last_time": "12时00分",
                        "url": "https://weibo.com/hot/3",
                        "mobileUrl": "https://m.weibo.com/hot/3"
                    }
                ]
            },
            {
                "source_name": "知乎热榜",
                "titles": [
                    {
                        "title": "如何看待AI换脸技术的安全问题？",
                        "ranks": [1],
                        "first_time": "09时30分",
                        "last_time": "09时30分",
                        "url": "https://zhihu.com/question/1",
                        "mobileUrl": "https://m.zhihu.com/question/1"
                    },
                    {
                        "title": "网警破获AI换脸非法侵入系统案",  # 测试跨平台重复
                        "ranks": [3],
                        "first_time": "10时55分",
                        "last_time": "10时55分",
                        "url": "https://zhihu.com/hot/1",
                        "mobileUrl": "https://m.zhihu.com/hot/1"
                    }
                ]
            },
            {
                "source_name": "抖音热点",
                "titles": [
                    {
                        "title": "人工智能发展迎来新突破",
                        "ranks": [4],
                        "first_time": "13时15分",
                        "last_time": "13时15分",
                        "url": "https://douyin.com/hot/1",
                        "mobileUrl": "https://m.douyin.com/hot/1"
                    }
                ]
            }
        ],
        "stats": [
            {
                "word": "AI换脸",
                "count": 4,
                "platforms": ["微博", "知乎", "抖音"]
            },
            {
                "word": "人工智能",
                "count": 3,
                "platforms": ["微博", "知乎", "抖音"]
            },
            {
                "word": "网警",
                "count": 2,
                "platforms": ["微博", "知乎"]
            }
        ],
        "failed_ids": ["failed_platform_1"]
    }
    
    update_info = {
        "remote_version": "2.1.0",
        "current_version": "2.0.5"
    }
    
    # 创建增强格式化器
    formatter = EnhancedBarkFormatter(enable_duplicate_detection=True)
    
    # 格式化消息
    now = datetime.now()
    batches = formatter.format_enhanced_message(test_report_data, now, update_info)
    
    print("=" * 60)
    print("🧪 增强Bark格式化器测试")
    print("=" * 60)
    
    # 显示去重统计
    duplicate_stats = formatter.get_duplicate_stats()
    if duplicate_stats:
        print(f"\n📊 去重统计:")
        print(f"   处理总数: {duplicate_stats['total_processed']} 条")
        print(f"   重复内容: {duplicate_stats['total_duplicates']} 条")
        print(f"   保留内容: {duplicate_stats['unique_content']} 条")
        print(f"   平台重复: {duplicate_stats['platform_duplicates']}")
        print(f"   跨平台重复: {duplicate_stats['cross_platform_duplicates']} 条")
        print(f"   哈希匹配: {duplicate_stats['hash_based_duplicates']} 条")
        print(f"   相似度匹配: {duplicate_stats['similarity_based_duplicates']} 条")
    
    print(f"\n📦 消息批次数量: {len(batches)}")
    
    # 显示每个批次的内容和大小
    for i, batch in enumerate(batches, 1):
        content_size = len(batch.encode('utf-8'))
        print(f"\n--- 批次 {i} ({content_size} 字节) ---")
        print(batch[:500] + "..." if len(batch) > 500 else batch)
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)


def test_duplicate_detector_only():
    """单独测试去重检测器"""
    
    print("\n🔍 单独测试去重检测器")
    print("-" * 40)
    
    from enhanced_duplicate_detector import EnhancedDuplicateDetector
    
    detector = EnhancedDuplicateDetector(enable_similarity_check=True)
    
    test_titles = [
        ("网警破获AI换脸非法侵入系统案", "微博热搜"),
        ("网警破获 AI换脸 非法侵入案", "微博热搜"),  # 标准化后相同
        ("网警破获AI换脸非法侵入系统案", "知乎热榜"),  # 跨平台重复
        ("人工智能发展迎来新突破", "抖音热点"),
        ("AI换脸技术安全引关注", "微博热搜"),  # 相似内容
        ("ChatGPT推出新功能", "微博热搜"),
    ]
    
    print("添加测试内容:")
    for title, platform in test_titles:
        is_unique = detector.add_content(title, platform, {})
        status = "✅ 保留" if is_unique else "🔄 去重"
        print(f"  {status} [{platform}] {title}")
    
    print("\n" + detector.get_duplicate_summary())
    print("\n" + detector.get_duplicate_details())


if __name__ == "__main__":
    try:
        test_enhanced_formatter()
        test_duplicate_detector_only()
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)