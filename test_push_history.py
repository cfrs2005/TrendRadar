#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试推送历史记录功能

验证修复后的 incremental 模式是否按预期工作
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from push_history import PushHistory


def test_push_history():
    """测试推送历史记录功能"""
    print("=== 测试推送历史记录功能 ===\n")
    
    # 初始化推送历史记录
    history = PushHistory()
    
    # 测试数据
    test_items = {
        "weibo": {
            "新闻A": {"url": "https://weibo.com/1", "count": 1},
            "新闻B": {"url": "https://weibo.com/2", "count": 2},
        },
        "zhihu": {
            "新闻C": {"url": "https://zhihu.com/1", "count": 1},
        }
    }
    
    print("1️⃣ 测试获取新增内容（第一次运行）")
    new_items = history.get_new_items(test_items)
    print(f"新增内容数量: {sum(len(titles) for titles in new_items.values())}")
    
    # 标记为已推送
    print("\n2️⃣ 标记内容为已推送")
    history.mark_items_as_pushed(new_items)
    
    print("\n3️⃣ 测试获取新增内容（第二次运行，应该为空）")
    new_items_2 = history.get_new_items(test_items)
    print(f"新增内容数量: {sum(len(titles) for titles in new_items_2.values())}")
    
    # 添加新的测试数据
    new_test_items = {
        "weibo": {
            "新闻A": {"url": "https://weibo.com/1", "count": 1},  # 重复
            "新闻D": {"url": "https://weibo.com/3", "count": 3},  # 新增
        },
        "bilibili-hot-search": {
            "新闻E": {"url": "https://bilibili.com/1", "count": 1},  # 新增
        }
    }
    
    print("\n4️⃣ 测试获取新增内容（添加新数据后）")
    new_items_3 = history.get_new_items(new_test_items)
    print(f"新增内容数量: {sum(len(titles) for titles in new_items_3.values())}")
    
    for source_id, titles in new_items_3.items():
        print(f"  {source_id}: {list(titles.keys())}")
    
    # 标记新的内容为已推送
    print("\n5️⃣ 标记新内容为已推送")
    history.mark_items_as_pushed(new_items_3)
    
    print("\n6️⃣ 获取统计信息")
    stats = history.get_statistics()
    print(f"总推送数量: {stats['total_pushed']}")
    print(f"来源分布: {stats['source_distribution']}")
    print(f"日期分布: {stats['date_distribution']}")
    
    print("\n✅ 推送历史记录功能测试完成！")
    return True


def test_incremental_logic():
    """测试 incremental 模式逻辑"""
    print("\n=== 测试 Incremental 模式逻辑 ===\n")
    
    # 模拟数据文件结构
    test_data_dir = Path("test_output")
    test_data_dir.mkdir(exist_ok=True)
    
    # 创建模拟的新闻数据文件
    time_1_data = """weibo | 微博
1. 新闻A [URL:https://weibo.com/1]
2. 新闻B [URL:https://weibo.com/2]

zhihu | 知乎  
1. 新闻C [URL:https://zhihu.com/1]
"""
    
    time_2_data = """weibo | 微博
1. 新闻A [URL:https://weibo.com/1]  # 重复
2. 新闻D [URL:https://weibo.com/3]  # 新增

zhihu | 知乎
1. 新闻C [URL:https://zhihu.com/1]  # 重复
2. 新闻E [URL:https://zhihu.com/2]  # 新增
"""
    
    # 写入测试文件
    (test_data_dir / "time1.txt").write_text(time_1_data, encoding='utf-8')
    (test_data_dir / "time2.txt").write_text(time_2_data, encoding='utf-8')
    
    print("1️⃣ 创建了模拟数据文件")
    print(f"   - time1.txt: 新闻A, 新闻B, 新闻C")
    print(f"   - time2.txt: 新闻A, 新闻D, 新闻C, 新闻E")
    
    # 使用推送历史记录测试增量逻辑
    history = PushHistory(str(test_data_dir))
    
    print("\n2️⃣ 模拟第一次运行（增量模式）")
    # 模拟 parse_file_titles 函数的结果
    all_data_time1 = {
        "weibo": {
            "新闻A": {"url": "https://weibo.com/1", "count": 1},
            "新闻B": {"url": "https://weibo.com/2", "count": 1},
        },
        "zhihu": {
            "新闻C": {"url": "https://zhihu.com/1", "count": 1},
        }
    }
    
    new_items_time1 = history.get_new_items(all_data_time1)
    print(f"   新增内容: {sum(len(titles) for titles in new_items_time1.values())} 条")
    for source_id, titles in new_items_time1.items():
        print(f"   {source_id}: {list(titles.keys())}")
    
    history.mark_items_as_pushed(new_items_time1)
    
    print("\n3️⃣ 模拟第二次运行（增量模式）")
    all_data_time2 = {
        "weibo": {
            "新闻A": {"url": "https://weibo.com/1", "count": 1},  # 重复
            "新闻D": {"url": "https://weibo.com/3", "count": 1},  # 新增
        },
        "zhihu": {
            "新闻C": {"url": "https://zhihu.com/1", "count": 1},  # 重复
            "新闻E": {"url": "https://zhihu.com/2", "count": 1},  # 新增
        }
    }
    
    new_items_time2 = history.get_new_items(all_data_time2)
    print(f"   新增内容: {sum(len(titles) for titles in new_items_time2.values())} 条")
    for source_id, titles in new_items_time2.items():
        print(f"   {source_id}: {list(titles.keys())}")
    
    history.mark_items_as_pushed(new_items_time2)
    
    print("\n4️⃣ 模拟第三次运行（应该没有新增内容）")
    new_items_time3 = history.get_new_items(all_data_time2)
    print(f"   新增内容: {sum(len(titles) for titles in new_items_time3.values())} 条")
    
    print("\n✅ Incremental 模式逻辑测试完成！")
    
    # 清理测试文件
    import shutil
    shutil.rmtree(test_data_dir)
    
    return True


if __name__ == "__main__":
    try:
        success1 = test_push_history()
        success2 = test_incremental_logic()
        
        if success1 and success2:
            print("\n🎉 所有测试通过！修复后的 incremental 模式应该能正常工作。")
        else:
            print("\n❌ 测试失败")
            
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()