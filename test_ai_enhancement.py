#!/usr/bin/env python3
# coding=utf-8

"""
AI增强功能测试脚本
"""

import os
import sys
import json
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

def test_ai_service():
    """测试AI服务基础功能"""
    try:
        from ai_enhanced_service import AIEnhancedService
        
        print("🧪 测试AI增强服务...")
        
        # 创建服务实例
        ai_service = AIEnhancedService()
        
        # 检查是否启用
        if ai_service.is_enabled():
            print("✅ AI服务已启用")
        else:
            print("ℹ️ AI服务未启用（未设置CLAUDE_CODE_OAUTH_TOKEN）")
            print("   这是正常的，系统会优雅降级到传统模式")
        
        return True
        
    except Exception as e:
        print(f"❌ AI服务测试失败: {e}")
        return False

def test_message_formatter():
    """测试消息格式化器"""
    try:
        from ai_message_formatter import format_message_with_ai_enhancement
        
        print("🧪 测试消息格式化器...")
        
        # 模拟报告数据
        test_report_data = {
            'stats': [
                {
                    'word': 'AI',
                    'count': 5,
                    'titles': [
                        {
                            'title': 'ChatGPT-5正式发布',
                            'source_name': '百度热搜',
                            'rank': 1,
                            'url': 'https://example.com/1',
                            'mobile_url': 'https://m.example.com/1',
                            'is_new': True
                        }
                    ]
                }
            ]
        }
        
        # 测试格式化
        result = format_message_with_ai_enhancement(test_report_data, "daily", enable_ai=False)
        
        print("✅ 消息格式化器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 消息格式化器测试失败: {e}")
        return False

def test_enhanced_message_generator():
    """测试增强消息生成器"""
    try:
        from enhanced_message_generator import generate_enhanced_message_content
        
        print("🧪 测试增强消息生成器...")
        
        # 模拟报告数据
        test_report_data = {
            'stats': [
                {
                    'word': 'AI',
                    'count': 3,
                    'titles': [
                        {
                            'title': 'AI技术新突破',
                            'source_name': '今日头条',
                            'rank': 2,
                            'url': 'https://example.com/2',
                            'is_new': False
                        }
                    ]
                }
            ]
        }
        
        # 测试消息生成
        batches = generate_enhanced_message_content(
            test_report_data, "feishu", "测试报告", None, "daily"
        )
        
        if batches and len(batches) > 0:
            print("✅ 增强消息生成器测试通过")
            print(f"   生成了 {len(batches)} 个消息批次")
            return True
        else:
            print("❌ 增强消息生成器未生成消息")
            return False
        
    except Exception as e:
        print(f"❌ 增强消息生成器测试失败: {e}")
        return False

def test_imports():
    """测试所有新模块的导入"""
    print("🧪 测试模块导入...")
    
    modules_to_test = [
        'ai_enhanced_service',
        'ai_message_formatter', 
        'enhanced_message_generator'
    ]
    
    success_count = 0
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"   ✅ {module_name}")
            success_count += 1
        except Exception as e:
            print(f"   ❌ {module_name}: {e}")
    
    print(f"导入测试: {success_count}/{len(modules_to_test)} 成功")
    return success_count == len(modules_to_test)

def main():
    """主测试函数"""
    print("🚀 开始AI增强功能测试\n")
    
    # 检查Python版本
    python_version = sys.version_info
    print(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 7):
        print("⚠️ 警告: 建议使用Python 3.7+")
    
    print()
    
    # 测试计数
    total_tests = 0
    passed_tests = 0
    
    # 运行测试
    tests = [
        ("模块导入测试", test_imports),
        ("AI服务测试", test_ai_service),
        ("消息格式化器测试", test_message_formatter),
        ("增强消息生成器测试", test_enhanced_message_generator),
    ]
    
    for test_name, test_func in tests:
        total_tests += 1
        print(f"🔍 {test_name}")
        
        try:
            if test_func():
                passed_tests += 1
                print(f"✅ {test_name} 通过\n")
            else:
                print(f"❌ {test_name} 失败\n")
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}\n")
    
    # 测试结果汇总
    print("=" * 50)
    print(f"📊 测试结果: {passed_tests}/{total_tests} 通过")
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过！AI增强功能已准备就绪")
        print("\n📝 使用说明:")
        print("1. 设置环境变量 CLAUDE_CODE_OAUTH_TOKEN 来启用AI功能")
        print("2. 如果未设置token，系统会自动使用传统模式")
        print("3. AI功能包括智能去重、内容分类和总结")
        return True
    else:
        print("⚠️ 部分测试失败，请检查代码实现")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)