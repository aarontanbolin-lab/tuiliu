# -*- coding: utf-8 -*-
"""
推流 — 去重引擎
功能：URL去重、标题相似度去重、同事件多源合并
"""
from difflib import SequenceMatcher
from typing import List, Dict, Optional, Tuple
import re


class DedupEngine:
    """智能去重引擎"""

    def __init__(self, title_similarity_threshold: float = 0.85):
        """
        Args:
            title_similarity_threshold: 标题相似度阈值，超过此值视为重复（默认0.85）
        """
        self.threshold = title_similarity_threshold
        self._seen_urls: set = set()
        self._seen_titles: List[str] = []

    @staticmethod
    def _normalize_title(title: str) -> str:
        """标准化标题：去除标点以外的噪声，用于相似度比较"""
        # 去除常见前缀
        prefixes = [
            r'^[\d]+点[\d]*氪[丨|]',    # 36氪时间戳
            r'^快讯[丨|]',
            r'^电报[丨|]',
            r'^【[^】]*】',               # 【标签】
            r'^[\d]{4}年[\d]{1,2}月[\d]{1,2}日[：:]',  # 日期前缀
        ]
        for pattern in prefixes:
            title = re.sub(pattern, '', title)
        # 去除多余空白
        title = re.sub(r'\s+', ' ', title).strip()
        return title

    def _title_similarity(self, title1: str, title2: str) -> float:
        """计算两个标准化标题的相似度"""
        t1 = self._normalize_title(title1)
        t2 = self._normalize_title(title2)
        return SequenceMatcher(None, t1, t2).ratio()

    def is_duplicate_url(self, url: str) -> bool:
        """检查URL是否已存在"""
        return url in self._seen_urls

    def find_duplicate_title(self, title: str) -> Optional[Tuple[str, float]]:
        """
        检查标题是否与已有标题高度相似。
        返回 (匹配到的已有标题, 相似度) 或 None
        """
        for seen_title in self._seen_titles:
            sim = self._title_similarity(title, seen_title)
            if sim >= self.threshold:
                return (seen_title, sim)
        return None

    def add(self, url: str, title: str) -> None:
        """记录已处理的条目"""
        if url:
            self._seen_urls.add(url)
        if title:
            self._seen_titles.append(title)

    def deduplicate(self, items: List[Dict]) -> List[Dict]:
        """
        对条目列表去重。
        每个条目应包含: url (str), title (str), source (str), content (str)

        去重规则：
        1. URL完全匹配 → 丢弃
        2. 标题相似度 > 85% → 合并（保留信息更丰富的版本）
        3. 同一事件不同信源 → 合并标注多源
        """
        result = []
        merged_indices: set = set()

        for i, item in enumerate(items):
            if i in merged_indices:
                continue

            url = item.get('url', '')
            title = item.get('title', '')

            # 规则1：URL去重
            if url and self.is_duplicate_url(url):
                continue

            # 规则2：标题相似度去重
            dup = self.find_duplicate_title(title)
            if dup:
                # 保留信息量更大的版本
                existing = None
                for j, r in enumerate(result):
                    if r.get('title', '') == dup[0]:
                        existing = j
                        break

                if existing is not None:
                    # 比较内容长度，保留更详尽的版本
                    if len(item.get('content', '')) > len(result[existing].get('content', '')):
                        # 迁移来源信息
                        old_sources = result[existing].get('sources', [result[existing].get('source', '')])
                        item['sources'] = old_sources + [item.get('source', '')]
                        result[existing] = item
                    else:
                        # 添加来源
                        sources = result[existing].get('sources', [])
                        if item.get('source') not in sources:
                            sources.append(item.get('source', ''))
                        result[existing]['sources'] = sources
                continue

            # 规则3：同事件检测（标题预处理后相似度在0.6~0.85之间）
            merged = False
            for j, r in enumerate(result):
                sim = self._title_similarity(title, r.get('title', ''))
                if 0.6 <= sim < self.threshold:
                    # 可能是同一事件的不同报道角度
                    sources = r.get('sources', [r.get('source', '')])
                    if item.get('source') not in sources:
                        sources.append(item.get('source', ''))
                    r['sources'] = sources
                    r['cross_verified'] = True
                    # 合并内容（追加不同角度的信息）
                    if item.get('content') and item['content'] not in r.get('content', ''):
                        r['content'] = r.get('content', '') + '\n\n[多源补充] ' + item.get('content', '')
                    merged = True
                    break

            if not merged:
                # 新条目
                item['sources'] = [item.get('source', '')]
                item['cross_verified'] = False
                result.append(item)

            # 记录
            self.add(url, title)

        # 标记多源验证
        for item in result:
            if len(item.get('sources', [])) >= 2:
                item['cross_verified'] = True

        return result

    def reset(self) -> None:
        """重置引擎状态（每日采集前调用）"""
        self._seen_urls.clear()
        self._seen_titles.clear()


# =============================================================================
# 测试
# =============================================================================
if __name__ == '__main__':
    engine = DedupEngine()

    test_items = [
        {'url': 'https://36kr.com/p/123', 'title': '8点1氪丨八家上市公司集中公告"补税"', 'content': '详细内容A', 'source': '36kr'},
        {'url': 'https://36kr.com/p/123', 'title': '8点1氪丨八家上市公司集中公告"补税"', 'content': '重复URL', 'source': '36kr'},
        {'url': 'https://wallstreetcn.com/a/456', 'title': '八家上市公司集中公告补税，涉及金额超百亿', 'content': '详细内容B，来源华尔街见闻', 'source': '华尔街见闻'},
        {'url': 'https://cls.cn/t/789', 'title': '美联储维持利率不变', 'content': '美联储最新决议', 'source': '财联社'},
        {'url': 'https://36kr.com/p/999', 'title': 'AI新突破：GPT-6发布', 'content': '科技新闻', 'source': '36kr'},
    ]

    print("=== 去重前 ===")
    for item in test_items:
        print(f"  [{item['source']}] {item['title'][:60]}")

    result = engine.deduplicate(test_items)

    print(f"\n=== 去重后 ({len(result)} 条) ===")
    for item in result:
        sources = item.get('sources', [])
        verified = '✓多源' if item.get('cross_verified') else '单源'
        print(f"  [{verified}] {'+'.join(sources)}: {item['title'][:60]}")
