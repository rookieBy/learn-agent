# 代码走读指南

## 整体架构

```
┌─────────────────────────────────────────────────────┐
│                    main.py                          │
│                   (入口程序)                         │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│               InterviewAgent                       │
│                  (agent.py)                        │
│  ┌─────────────┐    ┌─────────────┐               │
│  │reason_node  │───▶│  act_node   │               │
│  │  (推理)     │    │  (行动)     │               │
│  └─────────────┘    └─────────────┘               │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                   SearchTool                        │
│                 (tools/search.py)                   │
│  ┌─────────────┐    ┌─────────────┐               │
│  │search_hn   │    │search_reddit│               │
│  │(搜HN)      │    │(搜Reddit)   │               │
│  └─────────────┘    └─────────────┘               │
└─────────────────────────────────────────────────────┘
```

---

## 1. main.py 详解

```python
#!/usr/bin/env python3
"""面试题分析Agent - 主入口"""

# 1. 导入
import sys
import os
from dotenv import load_dotenv                    # 读取.env文件
from langchain_openai import ChatOpenAI           # OpenAI LLM
from loguru import logger                         # 日志

from agent.agent import InterviewAgent             # Agent主类
from agent.tools.search import SearchTool          # 搜索工具

# 2. 加载环境变量（.env中的配置）
load_dotenv()

# 3. 配置日志
logger.add("logs/agent_{time}.log", rotation="1 day")

def main():
    """主函数 - 程序入口"""
    
    # 4. 初始化LLM（GPT-4）
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7
    )
    
    # 5. 初始化搜索工具
    search_tool = SearchTool()
    
    # 6. 创建Agent（传入LLM和工具）
    agent = InterviewAgent(llm=llm, tools=[search_tool])
    
    # 7. 交互式问答循环
    print("=== 面试题分析Agent ===")
    
    while True:
        question = input("你: ")
        if question.lower() in ['quit', 'exit']:
            break
        
        # 调用Agent处理问题
        response = agent.run(question)
        print(f"\n{response}\n")

if __name__ == "__main__":
    main()
```

**要点**：
- `load_dotenv()` 读取 .env 文件中的环境变量
- `ChatOpenAI` 是LangChain提供的OpenAI封装
- `temperature=0.7` 控制创造性，0.7是平衡值

---

## 2. agent.py 详解

### 2.1 状态定义

```python
class AgentState(TypedDict):
    """Agent状态 = 对话历史 + 下一步动作"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_action: str
```

- `messages` - 所有对话历史（HumanMessage + AIMessage）
- `Annotated[..., operator.add]` - 每次新消息追加而不是覆盖

### 2.2 Agent初始化

```python
def __init__(self, llm, tools: list):
    self.llm = llm
    # 把工具列表转成字典，方便按名称查找
    self.tools = {t.name: t for t in tools}
    # 构建工作流图
    self.graph = self._build_graph()
```

### 2.3 构建工作流图

```python
def _build_graph(self) -> StateGraph:
    workflow = StateGraph(AgentState)
    
    # 添加两个节点
    workflow.add_node("reason", self.reason_node)   # 推理节点
    workflow.add_node("act", self.act_node)          # 行动节点
    
    # 设置入口
    workflow.set_entry_point("reason")
    
    # 条件边：reason之后判断是继续act还是结束
    workflow.add_conditional_edges(
        "reason",
        self.should_continue,  # 判断函数
        {"continue": "act", "end": END}
    )
    
    # act之后回到reason继续
    workflow.add_edge("act", "reason")
    
    return workflow.compile()
```

### 2.4 推理节点（reason_node）

```python
def reason_node(self, state: AgentState) -> dict:
    """推理：分析问题，决定是否需要工具"""
    messages = state["messages"]
    last_message = messages[-1]
    
    # 构造提示词
    prompt = f"""分析用户问题，决定是否需要调用工具。

用户问题：{last_message.content}

如果需要搜索：
ACTION: search_all
INPUT: 搜索关键词

如果可以直接回答：
RESPONSE: 你的答案
"""
    
    # 调用LLM
    response = self.llm.invoke(prompt)
    content = response.content
    
    return {"messages": [AIMessage(content=content)]}
```

### 2.5 判断函数（should_continue）

```python
def should_continue(self, state: AgentState) -> str:
    """判断下一步：继续行动还是结束"""
    last_message = state["messages"][-1].content
    
    # 如果包含ACTION，说明需要调用工具
    if "ACTION:" in last_message:
        return "continue"  # 继续执行act节点
    return "end"           # 否则结束
```

### 2.6 行动节点（act_node）

```python
def act_node(self, state: AgentState) -> dict:
    """行动：执行工具调用"""
    last_message = state["messages"][-1].content
    
    if "ACTION:" not in last_message:
        return {"messages": []}
    
    # 解析工具名和参数
    tool_name = "search_all"  # 从last_message中提取
    tool_input = "AI Agent面试题"
    
    # 调用工具
    result = self.tools[tool_name].func(tool_input)
    
    # 把结果作为新消息，让reason继续处理
    return {
        "messages": [HumanMessage(content=f"搜索结果：{result}")]
    }
```

### 2.7 运行Agent

```python
def run(self, input: str) -> str:
    """运行Agent处理问题"""
    result = self.graph.invoke(
        {"messages": [HumanMessage(content=input)]},
        {"recursion_limit": 10}  # 防止无限循环
    )
    
    # 提取最终答案
    for message in reversed(result["messages"]):
        if "RESPONSE:" in message.content:
            return message.content.replace("RESPONSE:", "").strip()
    
    return result["messages"][-1].content
```

---

## 3. search.py 详解

### 3.1 SearchTool类

```python
class SearchTool:
    """搜索工具 - 封装所有搜索功能"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': '...'
        })
```

### 3.2 HN搜索

```python
def search_hacker_news(self, query: str) -> List[Dict]:
    # 1. 调用HN的Algolia API
    url = f"https://hn.algolia.com/api/v1/search?query={query}+interview"
    resp = self.session.get(url, timeout=10)
    
    # 2. 解析JSON
    data = resp.json()
    
    # 3. 提取结果
    results = []
    for hit in data.get('hits', [])[:5]:  # 只取前5条
        results.append({
            'title': hit.get('title', ''),
            'url': hit.get('url', ''),
            'source': 'HackerNews'
        })
    
    return results
```

### 3.3 聚合搜索

```python
def search_all(self, query: str) -> List[Dict]:
    """搜索所有来源"""
    results = []
    results.extend(self.search_hacker_news(query))
    results.extend(self.search_reddit(query))
    return results
```

---

## 4. settings.py 详解

```python
import os
from dotenv import load_dotenv

load_dotenv()  # 加载.env文件

# 从环境变量读取配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
HTTP_PROXY = os.getenv("http_proxy", "")
CHROMA_DB_PATH = "./data/chroma_db"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
```

---

## 5. 数据流总结

当用户输入"什么是AI Agent？"时：

```
1. main.py
   └── input("你: ") → "什么是AI Agent？"

2. agent.run("什么是AI Agent？")
   └── graph.invoke({"messages": [HumanMessage("什么是AI Agent？")]})

3. reason_node (第1次)
   ├── 分析问题："什么是AI Agent？"
   ├── 判断：需要搜索最新信息
   └── 输出：AIMessage("ACTION: search_all\nINPUT: AI Agent")

4. should_continue
   └── 发现ACTION: → 返回 "continue"

5. act_node (第1次)
   ├── 解析工具名：search_all
   ├── 解析参数：AI Agent
   ├── 调用：self.tools["search_all"].func("AI Agent")
   │   └── search_all() → 返回5条搜索结果
   └── 输出：HumanMessage("搜索结果：[{...}, {...}]")

6. reason_node (第2次)
   ├── 分析搜索结果
   ├── 判断：已经获取足够信息
   └── 输出：AIMessage("RESPONSE: AI Agent是...")

7. should_continue
   └── 没有ACTION: → 返回 "end"

8. graph.invoke() 返回结果

9. main.py 打印答案
```
