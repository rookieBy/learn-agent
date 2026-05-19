"""配置文件"""
import os
from dotenv import load_dotenv

load_dotenv()

# MiniMax / Claude API配置
ANTHROPIC_AUTH_TOKEN = os.getenv("ANTHROPIC_AUTH_TOKEN", "")
ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "https://api.minimaxi.com/anthropic")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "MiniMax-M2.7")

# 搜索配置
HACKER_NEWS_API = "https://hn.algolia.com/api/v1/search"
REDDIT_API = "https://www.reddit.com/r/MachineLearning/search.json"

# 代理配置
HTTP_PROXY = os.getenv("http_proxy", "")
HTTPS_PROXY = os.getenv("https_proxy", "")

# 向量数据库配置
CHROMA_DB_PATH = "./data/chroma_db"

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
