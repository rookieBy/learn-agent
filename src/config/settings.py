"""配置文件 - 从config.toml读取，同时支持环境变量覆盖"""
import os
from pathlib import Path

# 尝试导入toml库
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

# 获取配置文件路径
CONFIG_PATH = Path(__file__).parent / "config.toml"

def _load_config() -> dict:
    """加载配置文件"""
    if tomllib and CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "rb") as f:
                return tomllib.load(f)
        except Exception:
            pass
    return {}

_config = _load_config()

# MiniMax / Claude API配置
# config.toml中的值会被环境变量覆盖
_llm_config = _config.get("llm", {})
ANTHROPIC_AUTH_TOKEN = os.getenv("ANTHROPIC_AUTH_TOKEN") or _llm_config.get("api_key", "")
ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL") or _llm_config.get("base_url", "https://api.minimaxi.com/anthropic")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL") or _llm_config.get("model", "MiniMax-M2.7")

# 搜索配置
HACKER_NEWS_API = "https://hn.algolia.com/api/v1/search"
REDDIT_API = "https://www.reddit.com/r/MachineLearning/search.json"

# 代理配置
_proxy_config = _config.get("proxy", {})
HTTP_PROXY = os.getenv("http_proxy") or _proxy_config.get("http", "")
HTTPS_PROXY = os.getenv("https_proxy") or _proxy_config.get("https", "")

# 向量数据库配置
CHROMA_DB_PATH = "./data/chroma_db"

# 日志配置
_log_config = _config.get("logging", {})
LOG_LEVEL = os.getenv("LOG_LEVEL") or _log_config.get("level", "INFO")
