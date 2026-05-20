#!/usr/bin/env python3
"""面试题分析Agent - 主入口"""
import sys
import os
from datetime import datetime

# 添加src到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from loguru import logger

from config.settings import (
    ANTHROPIC_AUTH_TOKEN,
    ANTHROPIC_BASE_URL,
    ANTHROPIC_MODEL
)

# 加载环境变量
load_dotenv()

# 配置日志
logger.add("logs/agent_{time}.log", rotation="1 day")

# 会话记录文件路径 - 使用绝对路径
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSION_LOG_DIR = os.path.join(_PROJECT_ROOT, "data", "raw")
SESSION_LOG_FILE = os.path.join(
    SESSION_LOG_DIR,
    f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
)


def ensure_dir(path):
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)


def save_to_markdown(question: str, answer: str):
    """保存问答到markdown文件"""
    ensure_dir(SESSION_LOG_DIR)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(SESSION_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"## {timestamp}\n\n")
        f.write(f"**Q: {question}**\n\n")
        f.write(f"**A:**\n\n{answer}\n\n")
        f.write("---\n\n")

    logger.info(f"已保存到: {SESSION_LOG_FILE}")


def create_llm():
    """创建LLM实例 - 使用MiniMax API"""
    try:
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=ANTHROPIC_MODEL,
            anthropic_api_key=ANTHROPIC_AUTH_TOKEN,
            base_url=ANTHROPIC_BASE_URL,
            temperature=0.7
        )
    except ImportError:
        # 如果没有langchain_anthropic，使用OpenAI兼容接口
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=ANTHROPIC_MODEL,
            api_key=ANTHROPIC_AUTH_TOKEN,
            base_url=f"{ANTHROPIC_BASE_URL}/v1",
            temperature=0.7
        )


def main():
    """主函数"""
    logger.info("启动面试题分析Agent")
    logger.info(f"使用模型: {ANTHROPIC_MODEL}")
    logger.info(f"API地址: {ANTHROPIC_BASE_URL}")
    logger.info(f"会话记录将保存到: {SESSION_LOG_FILE}")

    # 初始化LLM
    llm = create_llm()

    # 初始化工具
    from agent.tools.search import SearchTool
    search_tool = SearchTool()

    # 初始化Agent
    from agent.agent import InterviewAgent
    agent = InterviewAgent(llm=llm, tools=[search_tool])

    # 交互式问答
    print("\n" + "="*50)
    print("  面试题分析Agent - AI Agent开发学习助手")
    print("="*50)
    print("\n问我任何关于AI Agent开发面试的问题")
    print("输入'quit'退出\n")

    while True:
        try:
            question = input("你: ").strip()

            if question.lower() in ['quit', 'exit', 'q']:
                print("再见！")
                break

            if not question:
                continue

            print("\n思考中...")
            response = agent.run(question)

            # 保存到markdown
            save_to_markdown(question, response)

            print(f"\n{response}\n")

        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            logger.error(f"运行错误: {e}")
            print(f"\n错误: {e}\n")


if __name__ == "__main__":
    main()