"""搜索工具 - 支持多来源搜索"""
import requests
import urllib.parse
from typing import List, Dict
from loguru import logger

class SearchTool:
    """AI Agent知识搜索工具"""

    name = "search_all"
    func = None

    def __init__(self):
        self.func = lambda query: self.search_all(query)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def search_hacker_news(self, query: str) -> List[Dict]:
        """从Hacker News搜索"""
        encoded_query = urllib.parse.quote(query)
        url = f"https://hn.algolia.com/api/v1/search?query={encoded_query}"
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
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.reddit.com/r/MachineLearning/search.json?q={encoded_query}&limit=5"
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

    def search_web(self, query: str) -> List[Dict]:
        """通过Web搜索（使用 DuckDuckGo）"""
        encoded_query = urllib.parse.quote(query)
        url = f"https://duckduckgo.com/html/?q={encoded_query}+AI+Agent"
        try:
            resp = self.session.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            # 简单的HTML解析
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, 'html.parser')
            results = []
            for i, result in enumerate(soup.select('.result')[:5], 1):
                title_elem = result.select_one('.result-title')
                link_elem = result.select_one('a.result-title')
                if title_elem and link_elem:
                    results.append({
                        'title': title_elem.get_text(strip=True),
                        'url': link_elem.get('href', ''),
                        'source': 'Web'
                    })
            logger.info(f"Web搜索到 {len(results)} 条结果")
            return results
        except Exception as e:
            logger.error(f"Web搜索失败: {e}")
            return []

    def search_all(self, query: str) -> List[Dict]:
        """搜索所有来源"""
        results = []
        results.extend(self.search_hacker_news(query))
        results.extend(self.search_reddit(query))
        # 只返回前10条结果，避免上下文过长
        return results[:10]
