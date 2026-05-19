# ReAct范式详解

## 什么是ReAct？

**ReAct = Reasoning + Acting**

这是一种让大型语言模型（LLM）能够"思考然后行动"的推理框架。

## 为什么需要ReAct？

传统的LLM是这样的：
```
输入问题 → 直接回答
```

ReAct是这样的：
```
输入问题 → 思考（Reasoning）→ 行动（Acting）→ 观察结果 → 再思考 → 再行动 → ...
```

**例子**：用户问"帮我找最近的AI Agent面试题"

普通LLM：只能根据训练知识回答，可能不知道最新的面试题

ReAct Agent：
1. Reasoning：我需要获取最新信息，应该调用搜索工具
2. Acting：调用搜索工具搜索"AI Agent面试题"
3. 观察：得到5条搜索结果
4. Reasoning：结果中有3条相关，继续获取内容
5. Acting：抓取这3篇文章的详细内容
6. ... 最终给出完整答案

## 代码实现

### 1. AgentState（状态）

```python
class AgentState(TypedDict):
    """状态 = Agent的'记忆本'"""
    messages: list        # 对话历史，包括所有思考和行动
    next_action: str      # 下一步要做什么
```

### 2. reason_node（推理节点）

```python
def reason_node(self, state: AgentState) -> dict:
    """
    推理节点 = 思考
    分析当前问题，决定下一步行动
    """
    messages = state["messages"]
    last_message = messages[-1]  # 用户的最新问题

    # 构造提示，让LLM决定是否需要调用工具
    prompt = f"""
    用户问题是：{last_message.content}
    
    如果需要调用工具，回复：
    ACTION: 工具名
    INPUT: 参数
    
    如果可以直接回答，回复：
    RESPONSE: 你的答案
    """

    response = self.llm.invoke(prompt)
    return {"messages": [AIMessage(content=response)]}
```

### 3. act_node（行动节点）

```python
def act_node(self, state: AgentState) -> dict:
    """
    行动节点 = 执行
    根据推理结果调用工具
    """
    messages = state["messages"]
    last_message = messages[-1].content

    # 解析LLM的输出
    if "ACTION:" in last_message:
        tool_name = 提取工具名
        tool_input = 提取参数
        
        # 调用工具
        result = self.tools[tool_name].func(tool_input)
        
        # 把结果返回给推理节点继续思考
        return {"messages": [HumanMessage(content=f"结果: {result}")]}

    return {"messages": []}
```

### 4. 工作流图

```
                    ┌──────────────┐
                    │   START      │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  reason_node │
                    │   (推理)     │
                    └──────┬───────┘
                           │
                    ┌──────┴───────┐
                    │              │
               需要工具?        直接回答?
                    │              │
                    ▼              ▼
            ┌────────────┐    ┌─────────┐
            │ act_node   │    │  输出   │
            │ (行动)     │    │  答案   │
            └─────┬──────┘    └─────────┘
                  │
                  ▼
            ┌────────────┐
            │ 工具执行   │
            │ 结果返回   │
            └─────┬──────┘
                  │
                  └──────→ 回到 reason_node (循环)
```

## ReAct vs 其他范式

| 范式 | 说明 | 适用场景 |
|------|------|----------|
| **ReAct** | Reasoning + Acting，思考后行动 | 需要获取外部信息 |
| **CoT** | Chain of Thought，思维链 | 复杂推理问题 |
| **ToT** | Tree of Thought，思维树 | 需要探索多种方案 |

## 在本项目中的应用

在 `agent.py` 中，ReAct实现：

```python
class InterviewAgent:
    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("reason", self.reason_node)
        workflow.add_node("act", self.act_node)
        
        # 设置流程
        workflow.set_entry_point("reason")
        
        # 条件边：根据推理结果决定是继续行动还是结束
        workflow.add_conditional_edges(
            "reason",
            self.should_continue,  # 判断是否需要行动
            {"continue": "act", "end": END}
        )
        
        # 行动后回到推理继续思考
        workflow.add_edge("act", "reason")
        
        return workflow.compile()
```

这就是LangGraph的强大之处：用图的方式清晰定义Agent的工作流程。
