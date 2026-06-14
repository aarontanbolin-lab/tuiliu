# -*- coding: utf-8 -*-
"""
推流 — RSS采集器
从已验证的RSS源采集实时资讯
"""
import feedparser
import httpx
import time
import html
from typing import List, Dict


# Phase 1 验证通过的RSS源
RSS_SOURCES = [
    {'name': '36氪', 'url': 'https://36kr.com/feed', 'category': 'hot_industries'},
    {'name': '量子位', 'url': 'https://www.qbitai.com/feed', 'category': 'science_tech'},
    {'name': 'IEEE Spectrum', 'url': 'https://spectrum.ieee.org/rss', 'category': 'science_tech'},
    {'name': 'Nature', 'url': 'https://www.nature.com/nature.rss', 'category': 'science_tech'},
    {'name': 'Science', 'url': 'https://www.science.org/rss/news_current.xml', 'category': 'science_tech'},
    {'name': 'PNAS', 'url': 'https://www.pnas.org/action/showFeed?type=etoc&feed=rss&jc=pnas', 'category': 'science_tech'},
    {'name': 'MIT Technology Review', 'url': 'https://www.technologyreview.com/feed/', 'category': 'science_tech'},
    {'name': 'Federal Reserve', 'url': 'https://www.federalreserve.gov/feeds/press_all.xml', 'category': 'financial_policy'},
]


class RSSCollector:
    """RSS源采集器"""

    def __init__(self, sources: List[Dict] = None):
        self.sources = sources or RSS_SOURCES
        self.status = {}  # 记录各源状态

    def _parse_entry(self, entry, source_name: str, category: str) -> Dict:
        """将RSS条目转换为内部格式"""
        content = ''
        if hasattr(entry, 'summary'):
            content = entry.summary or ''
        elif hasattr(entry, 'description'):
            content = entry.description or ''
        elif hasattr(entry, 'content'):
            content = str(entry.content[0].value) if entry.content else ''

        # 去除HTML标签（保留纯文本）
        import re
        content = re.sub(r'<[^>]+>', '', content)
        content = html.unescape(content)  # 解码 &nbsp; 等HTML实体
        content = content.strip()[:1000]  # 截取前1000字

        return {
            'title': getattr(entry, 'title', '').strip(),
            'url': getattr(entry, 'link', ''),
            'content': content,
            'source': source_name,
            'category': category,
            'published': getattr(entry, 'published', ''),
        }

    def fetch_all(self) -> List[Dict]:
        """采集所有RSS源，返回条目列表"""
        all_items = []
        self.status = {}

        for source in self.sources:
            name = source['name']
            url = source['url']
            category = source['category']

            try:
                feed = feedparser.parse(url)
                if feed.bozo and not feed.entries:
                    self.status[name] = 'failed'
                    continue

                items = []
                for entry in feed.entries:
                    item = self._parse_entry(entry, name, category)
                    if item['title']:  # 过滤空标题
                        items.append(item)

                all_items.extend(items)
                self.status[name] = 'ok'
                print(f'  [RSS] {name}: {len(items)} 条')

            except Exception as e:
                self.status[name] = 'failed'
                print(f'  [RSS] {name}: 失败 ({e})')

        return all_items

    def get_status(self) -> Dict:
        return self.status


# =============================================================================
# API采集器：arXiv
# =============================================================================
def fetch_arxiv(categories: List[str] = None, max_results: int = 10) -> List[Dict]:
    """采集arXiv最新论文"""
    if categories is None:
        categories = ['cs.AI', 'q-bio', 'cond-mat.mes-hall', 'physics.app-ph']

    all_items = []
    for cat in categories:
        try:
            url = f'https://export.arxiv.org/api/query?search_query=cat:{cat}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}'
            r = httpx.get(url, timeout=30)
            feed = feedparser.parse(r.text)

            for entry in feed.entries:
                # 提取摘要（去除HTML）
                import re
                summary = re.sub(r'<[^>]+>', '', getattr(entry, 'summary', ''))
                summary = html.unescape(summary)  # 解码 HTML 实体
                summary = summary.strip()[:800]

                all_items.append({
                    'title': getattr(entry, 'title', '').strip().replace('\n', ' '),
                    'url': getattr(entry, 'id', '').strip(),
                    'content': summary,
                    'source': 'arXiv',
                    'category': 'science_tech',
                    'published': getattr(entry, 'published', ''),
                    'arxiv_id': getattr(entry, 'id', '').split('/abs/')[-1] if '/abs/' in getattr(entry, 'id', '') else '',
                })

            print(f'  [arXiv] {cat}: {len(feed.entries)} 篇')

        except Exception as e:
            print(f'  [arXiv] {cat}: 失败 ({e})')

    return all_items


# =============================================================================
# API采集器：财联社
# =============================================================================
def fetch_cls_telegraph(max_items: int = 30) -> List[Dict]:
    """采集财联社电报快讯（SHA1-MD5签名）"""
    import hashlib

    try:
        # 构造签名参数
        app = 'CailianpressWeb'
        os = 'web'
        sv = '8.4.6'
        rn = max_items
        last_time = 0

        param_str = f'app={app}&last_time={last_time}&os={os}&rn={rn}&sv={sv}'
        sha1_result = hashlib.sha1(param_str.encode('utf-8')).hexdigest()
        sign = hashlib.md5(sha1_result.encode('utf-8')).hexdigest()

        url = f'https://www.cls.cn/v1/roll/get_roll_list?{param_str}&sign={sign}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.cls.cn/telegraph',
        }

        r = httpx.get(url, headers=headers, timeout=15)
        data = r.json()

        if data.get('errno') != 0:
            print(f'  [财联社] API错误: {data.get("msg", "")}')
            return []

        roll_data = data.get('data', {}).get('roll_data', [])
        items = []
        for item in roll_data:
            title = item.get('title', '') or item.get('brief', '')
            content = item.get('content', '') or item.get('brief', '')

            # 识别类别
            category = 'hot_industries'  # 默认
            level = item.get('level', 'C')
            ctime = item.get('ctime', 0)
            if level == 'A':
                # A级快讯通常是重要政策或宏观消息
                title_lower = (title + content).lower()
                if any(k in title_lower for k in ['央行', '利率', '降准', 'lpr', '货币政策']):
                    category = 'financial_policy'

            items.append({
                'title': title[:100],
                'url': f'https://www.cls.cn/telegraph/{item.get("id", "")}',
                'content': content[:500],
                'source': '财联社',
                'category': category,
                'published': time.strftime('%Y-%m-%d', time.localtime(ctime if ctime > 0 else time.time())),
                'level': level,
            })

        print(f'  [财联社] 电报: {len(items)} 条')
        return items

    except Exception as e:
        print(f'  [财联社] 失败: {e}')
        return []


# =============================================================================
# 测试
# =============================================================================
if __name__ == '__main__':
    print("=== RSS采集测试 ===")
    rss = RSSCollector()
    items = rss.fetch_all()
    print(f'\n共采集 {len(items)} 条')
    print(f'状态: {rss.get_status()}')

    print("\n=== arXiv采集测试 ===")
    arxiv = fetch_arxiv(max_results=3)
    for item in arxiv[:3]:
        print(f'  {item["title"][:60]}')

    print("\n=== 财联社采集测试 ===")
    cls = fetch_cls_telegraph(max_items=5)
    for item in cls[:3]:
        print(f'  [{item.get("level","?")}] {item["title"][:60]}')
