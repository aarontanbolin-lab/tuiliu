# -*- coding: utf-8 -*-
"""
推流 v2.0 — 编辑精选器
按重要性排序，每版块前5条标记为精选展开，其余折叠。
"""
from typing import Dict, List


# 每版块精选条数
FEATURED_COUNT = 5


def score_item(item: dict) -> float:
    """
    计算单条资讯的编辑重要度得分。
    高分 → 值得展开；低分 → 折叠。
    """
    score = 0.0
    title = str(item.get('title', ''))
    content = str(item.get('content', ''))
    text = (title + content).lower()

    # 1. 财联社A级电报（最高优先级）
    if item.get('level') == 'A':
        score += 3.0

    # 2. 多源交叉验证
    if item.get('reliability') == '多源验证':
        score += 2.0
    elif item.get('reliability') == '交叉验证':
        score += 1.0

    # 3. 政策/官方信号（含"国务院""央行""发改委"等高权重词）
    authority_words = ['国务院', '央行', '发改委', '政治局', '证监会', '工信部',
                       '美联储', 'FOMC', '欧央行', '中国人民银行', '财政部']
    for w in authority_words:
        if w in text:
            score += 0.5
            break  # 只加一次

    # 4. 重大信号词
    signal_words = ['突发', '重磅', '紧急', '崩盘', '危机', '降息', '降准',
                    '加息', '过会', 'IPO', '首发', '申购', '新股', '中签']
    for w in signal_words:
        if w in text:
            score += 0.3

    # 5. 当天数据（published 匹配当日）
    import datetime
    pub = str(item.get('published', ''))
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    if today in pub:
        score += 1.0

    # 6. 标题长度适中（太短没信息，太长没提炼）
    tlen = len(title)
    if 10 <= tlen <= 60:
        score += 0.5

    return score


def rank_sections(sections: dict) -> dict:
    """
    对每个版块的条目按重要度排序，并标记 featured/collapsed。
    返回修改后的 sections。
    """
    ranked = {}
    for section_id, items in sections.items():
        if not items:
            ranked[section_id] = items
            continue

        # 计算得分并排序（高分在前）
        for item in items:
            item['_score'] = score_item(item)
        items.sort(key=lambda x: x.get('_score', 0), reverse=True)

        # 标记前 FEATURED_COUNT 条为精选
        for i, item in enumerate(items):
            if i < FEATURED_COUNT:
                item['_featured'] = True
            else:
                item['_featured'] = False

        ranked[section_id] = items

    return ranked


def count_featured(sections: dict) -> int:
    """统计精选条目总数"""
    total = 0
    for items in sections.values():
        total += sum(1 for item in items if item.get('_featured'))
    return total
