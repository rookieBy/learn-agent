# AI Agent 学习助手 - 使用指南

## 项目简介

这是一个基于 LangGraph 的 AI Agent 学习项目，主要功能：
- **每日知识获取**：从网络获取 AI Agent 开发相关最新资讯
- **面试题解答**：搜索并回答 AI Agent 相关面试问题
- **框架对比分析**：提供 LangGraph、CrewAI、AutoGen 等框架的对比

## 快速开始

### 1. 安装依赖

```bash
cd /root/coding_plan/learn-agent
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 MiniMax API Key
```

### 3. 运行 Agent

```bash
python src/main.py
```

### 4. 使用示例

启动后输入问题：

```
你: 什么是AI Agent？
你: LangGraph和CrewAI有什么区别？
你: 2026年AI Agent发展趋势是什么？
你: quit
```

## 开发命令

```bash
# 运行测试
pytest tests/ -v

# 运行单个测试
pytest tests/test_agent.py -v

# 代码格式化
black src/ tests/

# 带覆盖率测试
pytest --cov=src --cov-report=term-missing
```

## 项目结构

```
learn-agent/
├── src/
│   ├── main.py              # 程序入口
│   ├── config/settings.py    # 配置（API Key等）
│   └── agent/
│       ├── agent.py          # ReAct状态机核心
│       ├── tools/search.py    # 搜索工具
│       └── prompts/          # 提示词模板
├── tests/                    # 测试代码
├── data/
│   ├── raw/                  # 原始知识库
│   └── processed/            # 处理后数据
└── logs/                     # 日志文件
```

## 常见问题

### Q1: 运行报错 "OPENAI_API_KEY not found"

```bash
# 检查 .env 文件
cat .env
# 确认 API Key 已配置
```

### Q2: 搜索结果为空

```bash
# 检查网络代理配置
export http_proxy=http://172.20.176.1:7897
export https_proxy=http://172.20.176.1:7897
```

### Q3: Agent 回答很慢

- MiniMax API 响应可能需要 10-30 秒
- 搜索工具依赖网络状况

## 扩展开发

### 添加新工具

在 `src/agent/tools/` 创建新的 Tool 类：

```python
class NewTool:
    name = "new_tool"
    func = None

    def __init__(self):
        self.func = lambda query: self.do_something(query)

    def do_something(self, query):
        # 实现逻辑
        return results
```

然后在 `main.py` 中注册：

```python
new_tool = NewTool()
agent = InterviewAgent(llm=llm, tools=[search_tool, new_tool])
```

### 修改提示词

编辑 `src/agent/prompts/agent_prompts.py` 中的提示词模板。

## 技术栈

- **LangGraph**: Agent 编排框架
- **LangChain**: LLM 应用开发
- **MiniMax API**: Claude 兼容的 LLM
- **BeautifulSoup**: 网页解析
- **Loguru**: 日志记录