# 面试题分析Agent - 详细使用指南

## 目录

1. [项目简介](#1-项目简介)
2. [快速开始（5分钟上手）](#2-快速开始5分钟上手)
3. [项目结构详解](#3-项目结构详解)
4. [核心概念解释](#4-核心概念解释)
5. [代码运行原理](#5-代码运行原理)
6. [常见问题](#6-常见问题)
7. [下一步学习](#7-下一步学习)

---

## 1. 项目简介

### 1.1 这是什么？

这是一个**用开发驱动学习**的AI Agent项目。你将：
- 通过开发这个Agent来学习Agent开发技能
- 用这个Agent帮你获取和分析AI Agent面试题

### 1.2 核心技术

| 技术 | 用途 | 学习阶段 |
|------|------|----------|
| **LangGraph** | Agent编排框架，控制工作流 | 第1-2周 |
| **LangChain** | LLM应用开发 | 全程 |
| **ReAct范式** | 推理+行动的循环 | 第1-2周 |
| **ChromaDB** | 向量数据库，记忆系统 | 第5-6周 |
| **BeautifulSoup** | 网页爬虫 | 第3-4周 |

---

## 2. 快速开始（5分钟上手）

### 步骤1：创建并激活虚拟环境

```bash
# 进入项目目录
cd ~/interview-agent

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境（每次使用前都要运行）
source venv/bin/activate
```

### 步骤2：安装依赖

```bash
# 安装所有依赖
pip install -r requirements.txt
```

### 步骤3：配置API密钥

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入你的OpenAI API Key
nano .env
# 或者用任何文本编辑器打开.env文件
```

`.env`文件内容：
```
OPENAI_API_KEY=sk-xxxxx-your-key-here
OPENAI_MODEL=gpt-4
```

> **注意**：你没有OpenAI API Key？
> 1. 访问 https://platform.openai.com 注册账号
> 2. 进入API Keys页面创建新密钥
> 3. 充值或使用免费额度

### 步骤4：测试运行

```bash
# 运行基础测试
pytest tests/test_agent.py -v

# 启动Agent（需要API Key）
python src/main.py
```

启动后应该看到：
```
=== 面试题分析Agent ===
问我任何关于AI Agent开发面试的问题
输入'quit'退出

你:
```

### 步骤5：问Agent一个问题

当Agent启动后，输入：
```
你: 什么是AI Agent？
```

Agent会思考并回答（需要几分钟，取决于API响应速度）。

---

## 3. 项目结构详解

```
interview-agent/
├── src/                          # 源代码
│   ├── main.py                   # 程序入口
│   ├── config/
│   │   └── settings.py           # 配置（API Key等）
│   └── agent/
│       ├── agent.py              # ★核心：Agent大脑
│       ├── tools/
│       │   └── search.py         # ★搜索工具
│       ├── memory/               # （待开发）记忆系统
│       └── prompts/
│           └── agent_prompts.py  # 提示词模板
├── tests/
│   └── test_agent.py             # 测试代码
├── data/                         # 数据存储
│   ├── raw/                      # 原始面试题
│   └── processed/                # 处理后数据
├── requirements.txt              # Python依赖
└── .env.example                  # 环境变量模板
```

### 3.1 文件功能表

| 文件 | 功能 | 重要程度 |
|------|------|----------|
| `main.py` | 程序入口，初始化LLM和Agent | ★★★★★ |
| `agent.py` | Agent核心逻辑，ReAct实现 | ★★★★★ |
| `search.py` | 搜索工具，搜索面试题 | ★★★★ |
| `settings.py` | 配置文件，存储API Key等 | ★★★★ |
| `agent_prompts.py` | AI提示词模板 | ★★★ |

---

## 4. 核心概念解释

### 4.1 什么是ReAct范式？

**ReAct = Reasoning（推理）+ Acting（行动）**

这是一个让AI"思考然后行动"的循环：

```
用户提问
    ↓
┌─────────────────────────────┐
│  REASONING（推理）           │
│  AI分析问题，决定是否需要    │
│  调用工具                   │
└─────────────────────────────┘
    ↓ 需要信息
┌─────────────────────────────┐
│  ACTING（行动）             │
│  AI调用搜索工具获取信息      │
└─────────────────────────────┘
    ↓ 获取结果
┌─────────────────────────────┐
│  REASONING（推理）           │
│  AI分析搜索结果，决定回答    │
└─────────────────────────────┘
    ↓
回答用户
```

**代码中的体现**：

在 `agent.py` 中：
- `reason_node()` - 推理节点，分析问题
- `act_node()` - 行动节点，调用工具

### 4.2 什么是Agent状态（State）？

状态就像Agent的"记忆本"，记录当前对话的所有信息。

```python
class AgentState(TypedDict):
    messages: list  # 对话历史
    next_action: str  # 下一步动作
```

### 4.3 什么是工具（Tools）？

工具是Agent的"手"，让它能执行具体操作：

| 工具 | 功能 |
|------|------|
| `SearchTool` | 搜索Hacker News和Reddit的面试题 |

---

## 5. 代码运行原理

### 5.1 启动流程

```
python src/main.py
    ↓
main() 函数被调用
    ↓
加载.env中的API Key
    ↓
初始化ChatOpenAI（GPT-4）
    ↓
初始化SearchTool搜索工具
    ↓
创建InterviewAgent实例
    ↓
进入交互式问答循环
```

### 5.2 Agent处理问题的流程

当你输入"什么是AI Agent？"时：

```
1. 输入被包装成 HumanMessage
   └── message = "什么是AI Agent？"

2. 进入reason_node（推理节点）
   └── LLM分析问题，判断是否需要搜索

3. 如果需要搜索：
   ├── LLM输出 "ACTION: search_all"
   │           "INPUT: AI Agent面试题"
   └── 进入act_node（行动节点）

4. act_node执行搜索
   └── 调用search.py中的search_all()
   └── 返回搜索结果

5. 结果被加回消息历史
   └── 回到reason_node

6. reason_node生成最终回答
   └── 输出RESPONSE: 答案

7. 主循环打印答案给用户
```

### 5.3 关键代码解读

#### agent.py 的核心结构

```python
class InterviewAgent:
    def __init__(self, llm, tools: list):
        # 1. 保存LLM和工具
        self.llm = llm
        self.tools = {t.name: t for t in tools}
        
        # 2. 构建工作图
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        # 创建工作流图
        workflow = StateGraph(AgentState)
        
        # 添加两个节点：reason（推理）和act（行动）
        workflow.add_node("reason", self.reason_node)
        workflow.add_node("act", self.act_node)
        
        # 设置工作流：reason -> act -> (循环或结束)
        workflow.set_entry_point("reason")
        workflow.add_conditional_edges(...)
        workflow.add_edge("act", "reason")
        
        return workflow.compile()
```

#### search.py 的搜索逻辑

```python
class SearchTool:
    def search_hacker_news(self, query: str) -> List[Dict]:
        # 1. 调用HN的Algolia API
        url = f"https://hn.algolia.com/api/v1/search?query={query}"
        response = requests.get(url)
        
        # 2. 解析JSON结果
        data = response.json()
        
        # 3. 提取标题、URL、来源
        results = []
        for hit in data['hits'][:5]:
            results.append({
                'title': hit['title'],
                'url': hit['url'],
                'source': 'HackerNews'
            })
        
        return results
```

---

## 6. 常见问题

### Q1: 运行时报错 "OPENAI_API_KEY not found"

**原因**：没有正确配置.env文件

**解决**：
```bash
# 1. 确认.env文件存在
ls -la .env

# 2. 检查内容
cat .env

# 3. 如果为空，重新创建
cp .env.example .env
nano .env  # 填入API Key
```

### Q2: 运行时报错 "Module not found"

**原因**：没有激活虚拟环境或没有安装依赖

**解决**：
```bash
# 激活虚拟环境
source venv/bin/activate

# 重新安装依赖
pip install -r requirements.txt
```

### Q3: Agent回答很慢

**原因**：GPT-4 API响应较慢，或网络问题

**解决**：
1. 耐心等待（正常可能需要10-30秒）
2. 检查网络连接
3. 切换到gpt-3.5-turbo（更快但能力较弱）

### Q4: 搜索结果为空

**原因**：网络问题或API限制

**解决**：
1. 设置代理：
   ```bash
   export http_proxy="http://172.20.176.1:7897"
   export https_proxy="http://172.20.176.1:7897"
   ```
2. 检查代理是否有效

### Q5: 想知道更多原理

**推荐学习资源**：
- LangGraph文档：https://langchain-ai.github.io/langgraph/
- ReAct论文：https://react-lm.github.io/

---

## 7. 下一步学习

### 当前进度
- ✅ Agent基础骨架（ReAct）
- ✅ 搜索工具

### 第3-4周任务
- 📝 添加网页爬虫工具（抓取文章全文）
- 📝 添加内容解析工具（提取关键信息）
- 📝 学习Function Calling

### 第5-6周任务
- 📝 添加记忆系统（ChromaDB向量数据库）
- 📝 学习RAG技术

### 第7-8周任务
- 📝 多Agent协作（CrewAI）
- 📝 搜索、分析、总结Agent配合

---

## 学习检查清单

在继续之前，确认你理解以下内容：

- [ ] 知道什么是ReAct范式（推理+行动循环）
- [ ] 知道Agent的state是什么
- [ ] 知道如何配置API Key
- [ ] 知道如何运行main.py
- [ ] 能说清楚reason_node和act_node的作用

如果有任何不清楚的，问我！
