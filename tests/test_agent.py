"""Agent基础测试"""
import pytest
import os

# 设置PYTHONPATH
os.environ['PYTHONPATH'] = 'src'

# 测试Agent状态
def test_agent_state():
    from src.agent.agent import AgentState
    state = AgentState(messages=[], next_action="")
    assert state["messages"] == []
    assert state["next_action"] == ""

# 测试搜索工具
def test_search_tool():
    from src.agent.tools.search import SearchTool
    tool = SearchTool()
    assert tool.session is not None

# 测试配置加载
def test_config():
    from src.config.settings import ANTHROPIC_MODEL, ANTHROPIC_BASE_URL
    assert ANTHROPIC_MODEL == "MiniMax-M2.7"
    assert ANTHROPIC_BASE_URL == "https://api.minimaxi.com/anthropic"
