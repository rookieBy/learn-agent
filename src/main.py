#!/usr/bin/env python3
"""面试题分析Agent - 主入口"""
import sys
import os

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
            print(f"\n{response}\n")

        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            logger.error(f"运行错误: {e}")
            print(f"\n错误: {e}\n")

if __name__ == "__main__":
    main()
