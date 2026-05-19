"""Agent核心 - 基于LangGraph的ReAct实现"""
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator

class AgentState(TypedDict):
    """Agent状态定义"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_action: str

class InterviewAgent:
    """
    面试题分析Agent - 演示ReAct范式

    ReAct = Reasoning + Acting
    1. Reasoning: 分析用户问题，理解意图
    2. Acting: 调用工具执行任务
    """

    def __init__(self, llm, tools: list):
        self.llm = llm
        self.tools = {t.name: t for t in tools}
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """构建Agent工作流图"""
        workflow = StateGraph(AgentState)

        # 添加节点
        workflow.add_node("reason", self.reason_node)
        workflow.add_node("act", self.act_node)

        # 设置入口和边
        workflow.set_entry_point("reason")
        workflow.add_conditional_edges(
            "reason",
            self.should_continue,
            {"continue": "act", "end": END}
        )
        workflow.add_edge("act", "reason")

        return workflow.compile()

    def reason_node(self, state: AgentState) -> dict:
        """
        推理节点 - 分析问题，决定是否需要调用工具
        这是ReAct中的'Reasoning'部分
        """
        messages = state["messages"]
        last_message = messages[-1]

        # 构建提示
        prompt = f"""你是一个面试题分析助手。用户的问题是：

{last_message.content}

根据用户问题，决定是否需要调用工具来获取信息。

如果需要调用工具，请用以下格式：
ACTION: 工具名称
INPUT: 搜索 query

如果可以直接回答：
RESPONSE: 你的回答
"""

        response = self.llm.invoke(prompt)

        # 解析LLM响应
        if hasattr(response, 'content'):
            content = response.content
        else:
            content = str(response)

        return {"messages": [AIMessage(content=content)]}

    def should_continue(self, state: AgentState) -> str:
        """判断下一步动作"""
        messages = state["messages"]
        last_message = messages[-1].content

        if "ACTION:" in last_message:
            return "continue"
        return "end"

    def act_node(self, state: AgentState) -> dict:
        """
        行动节点 - 执行工具调用
        这是ReAct中的'Acting'部分
        """
        messages = state["messages"]
        last_message = messages[-1].content

        # 解析工具调用
        if "ACTION:" not in last_message:
            return {"messages": []}

        # 提取工具名称和参数
        lines = last_message.split('\n')
        tool_name = None
        tool_input = None

        for line in lines:
            if line.startswith("ACTION:"):
                tool_name = line.replace("ACTION:", "").strip()
            if line.startswith("INPUT:"):
                tool_input = line.replace("INPUT:", "").strip()

        if tool_name and tool_name in self.tools:
            tool = self.tools[tool_name]
            result = tool.func(tool_input)

            return {
                "messages": [HumanMessage(content=f"工具 {tool_name} 返回结果:\n{result}")]
            }

        return {"messages": [HumanMessage(content="工具不存在")]}

    def run(self, input: str) -> str:
        """运行Agent"""
        result = self.graph.invoke(
            {"messages": [HumanMessage(content=input)]},
            {"recursion_limit": 10}
        )

        # 返回最终响应
        for message in reversed(result["messages"]):
            content = message.content
            if "RESPONSE:" in content:
                return content.replace("RESPONSE:", "").strip()

        # 如果没有直接响应，返回最后一条AI消息
        return result["messages"][-1].content
