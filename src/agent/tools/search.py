"""搜索工具 - 演示ReAct中的Tool Use"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from loguru import logger

class SearchTool:
    """面试题搜索工具"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def search_hacker_news(self, query: str) -> List[Dict]:
        """从Hacker News搜索"""
        url = f"https://hn.algolia.com/api/v1/search?query={query}+interview"
        try:
            resp = self.session.get(url, timeout=10)
            data = resp.json()
            results = []
            for hit in data.get('hits', [])[:5]:
                results.append({
                    'title': hit.get('title', ''),
                    'url': hit.get('url', ''),
                    'source': 'HackerNews'
                })
            logger.info(f"HN搜索到 {len(results)} 条结果")
            return results
        except Exception as e:
            logger.error(f"HN搜索失败: {e}")
            return []

    def search_reddit(self, query: str) -> List[Dict]:
        """从Reddit搜索"""
        url = f"https://www.reddit.com/r/MachineLearning/search.json?q={query}+interview&limit=5"
        try:
            resp = self.session.get(url, timeout=10)
            data = resp.json()
            results = []
            for child in data.get('data', {}).get('children', [])[:5]:
                post = child.get('data', {})
                results.append({
                    'title': post.get('title', ''),
                    'url': post.get('url', ''),
                    'source': 'Reddit'
                })
            logger.info(f"Reddit搜索到 {len(results)} 条结果")
            return results
        except Exception as e:
            logger.error(f"Reddit搜索失败: {e}")
            return []

    def search_all(self, query: str) -> List[Dict]:
        """搜索所有来源"""
        results = []
        results.extend(self.search_hacker_news(query))
        results.extend(self.search_reddit(query))
        return results
