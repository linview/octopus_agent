"""
微信公众号Agent系统主入口

提供命令行接口和基本功能演示
"""

import asyncio
import argparse
import sys
from pathlib import Path

from utils.config import load_config, create_default_config_file
from utils.logger import setup_logging, get_logger
from core.base_agent import BaseAgent


def create_project_structure():
    """创建项目目录结构"""
    directories = [
        "agents",
        "core", 
        "models",
        "utils",
        "config",
        "data",
        "tests",
        "docs",
        "dify_integration",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ 创建目录: {directory}")


def init_project():
    """初始化项目"""
    print("🚀 初始化微信公众号Agent系统...")
    
    # 创建目录结构
    create_project_structure()
    
    # 创建默认配置文件
    try:
        create_default_config_file("config/config.json")
        print("✓ 创建默认配置文件: config/config.json")
    except Exception as e:
        print(f"✗ 创建配置文件失败: {e}")
    
    # 创建环境变量模板
    env_template = """# 微信公众号Agent系统配置文件模板
# 复制此文件为 .env 并填入实际配置

# ===== Agent配置 =====
# 爬虫Agent配置
CRAWLER_MAX_ARTICLES=10
CRAWLER_DELAY=2
CRAWLER_USER_AGENT=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36

# 存储Agent配置
STORER_TYPE=local
STORER_DATA_PATH=./data
STORER_MONGODB_URI=mongodb://localhost:27017/wx_agent

# 分析Agent配置
ANALYZER_MODEL_NAME=jieba
ANALYZER_FEATURES=keywords,summary,sentiment,style

# 生成Agent配置
GENERATOR_LLM_MODEL=Qwen2-7B-Instruct
GENERATOR_MAX_LENGTH=1500
GENERATOR_TEMPERATURE=0.7

# ===== 向量数据库配置 =====
VECTOR_DB_TYPE=chromadb
VECTOR_DB_PATH=./data/vectors
VECTOR_DB_COLLECTION=wx_articles

# ===== Dify平台集成配置 =====
DIFY_ENABLED=false
DIFY_API_URL=http://localhost:5001
DIFY_API_KEY=your_dify_api_key

# ===== 日志配置 =====
LOG_LEVEL=INFO
LOG_FILE=./logs/wx_agent.log

# ===== 开发环境配置 =====
DEBUG=true
TEST_MODE=false
"""
    
    try:
        with open(".env.template", "w", encoding="utf-8") as f:
            f.write(env_template)
        print("✓ 创建环境变量模板: .env.template")
    except Exception as e:
        print(f"✗ 创建环境变量模板失败: {e}")
    
    print("\n🎉 项目初始化完成！")
    print("\n📋 下一步操作：")
    print("1. 复制 .env.template 为 .env 并配置环境变量")
    print("2. 运行 'uv sync' 安装依赖")
    print("3. 运行 'uv run playwright install chromium' 安装浏览器")
    print("4. 运行 'uv run pytest' 执行测试")


def test_config():
    """测试配置加载"""
    print("🔧 测试配置加载...")
    
    try:
        config = load_config()
        print("✓ 配置加载成功")
        print(f"  - 爬虫最大文章数: {config.crawler.max_articles}")
        print(f"  - 存储类型: {config.storer.storage_type}")
        print(f"  - 分析模型: {config.analyzer.model_name}")
        print(f"  - 生成模型: {config.generator.llm_model}")
        
        # 验证配置
        errors = config.validate_config()
        if errors:
            print("⚠️  配置验证发现问题:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("✓ 配置验证通过")
            
    except Exception as e:
        print(f"✗ 配置加载失败: {e}")


def test_logging():
    """测试日志系统"""
    print("📝 测试日志系统...")
    
    try:
        logger = get_logger("test")
        logger.info("这是一条测试日志")
        logger.warning("这是一条警告日志")
        logger.error("这是一条错误日志")
        print("✓ 日志系统测试完成")
        
    except Exception as e:
        print(f"✗ 日志系统测试失败: {e}")


def run_tests():
    """运行测试"""
    print("🧪 运行测试...")
    
    import subprocess
    import sys
    
    try:
        result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ 所有测试通过")
        else:
            print("✗ 测试失败")
            print(result.stdout)
            print(result.stderr)
            
    except Exception as e:
        print(f"✗ 运行测试失败: {e}")


def show_status():
    """显示系统状态"""
    print("📊 系统状态...")
    
    try:
        config = load_config()
        
        print(f"配置版本: {config.config_version}")
        print(f"调试模式: {config.debug}")
        print(f"测试模式: {config.test_mode}")
        
        # 检查目录
        directories = ["agents", "core", "models", "utils", "config", "data", "tests", "docs"]
        for directory in directories:
            if Path(directory).exists():
                print(f"✓ {directory}/")
            else:
                print(f"✗ {directory}/ (缺失)")
                
    except Exception as e:
        print(f"✗ 获取状态失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="微信公众号Agent系统")
    parser.add_argument("command", choices=["init", "test-config", "test-logging", "test", "status"], 
                       help="要执行的命令")
    
    args = parser.parse_args()
    
    if args.command == "init":
        init_project()
    elif args.command == "test-config":
        test_config()
    elif args.command == "test-logging":
        test_logging()
    elif args.command == "test":
        run_tests()
    elif args.command == "status":
        show_status()
    else:
        print(f"未知命令: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main() 