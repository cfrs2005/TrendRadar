#!/usr/bin/env python3
# coding=utf-8

"""
测试 BigModel API 集成
"""

import os
import sys
from bigmodel_service import BigModelService

def test_bigmodel_integration():
    """测试 BigModel API 集成"""
    print("🧪 开始测试 BigModel API 集成...")
    
    # 检查环境变量
    api_token = os.getenv("CLAUDE_CODE_OAUTH_TOKEN")
    if not api_token:
        print("❌ 未设置 CLAUDE_CODE_OAUTH_TOKEN 环境变量")
        print("💡 请设置环境变量来测试 BigModel API")
        return False
    
    # 创建 BigModel 服务实例
    try:
        ai_service = BigModelService()
        print(f"✅ BigModel 服务创建成功")
        print(f"   API URL: {ai_service.api_url}")
        print(f"   Model: {ai_service.model}")
    except Exception as e:
        print(f"❌ BigModel 服务创建失败: {str(e)}")
        return False
    
    # 测试数据
    test_titles = [
        {
            "title": "OpenAI发布新的GPT-4 Turbo模型，性能提升显著",
            "source_name": "科技头条",
            "url": "https://example.com/1",
            "mobile_url": "https://m.example.com/1",
            "ranks": [1, 2],
            "is_new": True
        },
        {
            "title": "GPT-4 Turbo：OpenAI最新大语言模型全面评测",
            "source_name": "AI资讯",
            "url": "https://example.com/2", 
            "mobile_url": "https://m.example.com/2",
            "ranks": [3, 4],
            "is_new": True
        },
        {
            "title": "国家统计局：前三季度GDP同比增长5.2%",
            "source_name": "财经快报",
            "url": "https://example.com/3",
            "mobile_url": "https://m.example.com/3", 
            "ranks": [1, 2],
            "is_new": True
        },
        {
            "title": "全球经济展望：中国经济稳健增长",
            "source_name": "经济观察",
            "url": "https://example.com/4",
            "mobile_url": "https://m.example.com/4",
            "ranks": [3, 4],
            "is_new": True
        }
    ]
    
    print(f"📊 测试数据: {len(test_titles)} 条新闻标题")
    
    # 测试智能去重和分析
    try:
        print("\n🤖 开始 AI 智能去重和分析...")
        deduplicated_titles, analysis_result = ai_service.smart_deduplicate_and_analyze(test_titles)
        
        print(f"📈 去重结果: {len(test_titles)} 条 → {len(deduplicated_titles)} 条")
        
        if analysis_result:
            print("📋 AI 分析结果:")
            print(f"   去重率: {analysis_result.get('deduplication_rate', 'N/A')}")
            print(f"   热门话题: {', '.join(analysis_result.get('hot_topics', []))}")
            print(f"   内容总结: {analysis_result.get('summary', 'N/A')}")
            
            categories = analysis_result.get('categories', {})
            if categories:
                print("   智能分类:")
                for category, indices in categories.items():
                    print(f"     {category}: {len(indices)} 条")
        
        print("\n📝 去重后的标题:")
        for i, title_data in enumerate(deduplicated_titles, 1):
            print(f"   {i}. {title_data['title']} ({title_data['source_name']})")
            if 'ai_category' in title_data:
                print(f"      分类: {title_data['ai_category']}")
        
        # 测试消息格式化
        print("\n✨ 测试 AI 增强消息格式化...")
        ai_message = ai_service.format_ai_enhanced_message(deduplicated_titles, analysis_result)
        if ai_message:
            print("📤 AI 增强消息:")
            print(ai_message)
        else:
            print("⚠️  AI 增强消息为空")
            
    except Exception as e:
        print(f"❌ AI 智能去重和分析失败: {str(e)}")
        return False
    
    print("\n✅ BigModel API 集成测试完成！")
    return True

def test_basic_functionality():
    """测试基础功能（不需要 API Token）"""
    print("🧪 测试基础功能...")
    
    # 测试哈希去重
    ai_service = BigModelService()
    
    test_titles = [
        {"title": "重复标题测试", "source_name": "来源1"},
        {"title": "重复标题测试", "source_name": "来源2"}, 
        {"title": "不同标题", "source_name": "来源1"},
    ]
    
    deduplicated = ai_service._basic_deduplicate(test_titles)
    print(f"📊 基础去重: {len(test_titles)} 条 → {len(deduplicated)} 条")
    
    expected_count = 2  # 两个不同标题
    if len(deduplicated) == expected_count:
        print("✅ 基础哈希去重功能正常")
        return True
    else:
        print(f"❌ 基础哈希去重功能异常: 期望 {expected_count} 条，实际 {len(deduplicated)} 条")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 BigModel API 集成测试")
    print("=" * 60)
    
    # 测试基础功能
    basic_ok = test_basic_functionality()
    
    print("\n" + "=" * 60)
    
    # 测试完整 API 集成（如果有 token）
    if os.getenv("CLAUDE_CODE_OAUTH_TOKEN"):
        api_ok = test_bigmodel_integration()
        overall_success = basic_ok and api_ok
    else:
        print("⚠️  跳过 API 集成测试（未设置 CLAUDE_CODE_OAUTH_TOKEN）")
        overall_success = basic_ok
    
    print("\n" + "=" * 60)
    if overall_success:
        print("🎉 所有测试通过！BigModel API 集成成功！")
        sys.exit(0)
    else:
        print("❌ 测试失败，请检查配置和实现")
        sys.exit(1)