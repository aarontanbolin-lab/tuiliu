# -*- coding: utf-8 -*-
"""
推流 — 关键信息提取器
从原文中提取结构化关键事实，保留原文，不篡改。
"""
import re
from typing import Dict, List, Optional
from datetime import datetime


class KeyInfoExtractor:
    """关键信息提取器 —— 提取但不篡改原文"""

    # 日期模式
    DATE_PATTERNS = [
        r'(\d{4})年(\d{1,2})月(\d{1,2})日',
        r'(\d{4})-(\d{1,2})-(\d{1,2})',
        r'(\d{4})/(\d{1,2})/(\d{1,2})',
    ]

    # 百分比模式
    PERCENT_PATTERN = r'([\d,.]+)%'
    # 货币金额模式
    MONEY_PATTERN = r'([\d,.]+)\s*(亿|万|千)?\s*(元|美元|美金|欧元|日元|英镑|港币|人民币)'

    @staticmethod
    def extract_key_facts(text: str) -> Dict:
        """从文本中提取基本关键事实"""
        if not text:
            return {}

        facts = {}

        # 提取百分比数据
        percents = re.findall(KeyInfoExtractor.PERCENT_PATTERN, text)
        if percents:
            facts['percentages'] = percents[:5]

        # 提取金额
        money = re.findall(KeyInfoExtractor.MONEY_PATTERN, text)
        if money:
            facts['money_mentions'] = [f'{m[0]}{m[1] or ""}{m[2]}' for m in money[:5]]

        # 提取日期
        for pattern in KeyInfoExtractor.DATE_PATTERNS:
            dates = re.findall(pattern, text)
            if dates:
                facts['dates_found'] = [f'{d[0]}-{d[1]}-{d[2]}' for d in dates[:3]]
                break

        return facts

    def process_policy(self, item: Dict) -> Dict:
        """处理政策类内容"""
        content = str(item.get('content', '') or item.get('description', ''))
        title = str(item.get('title', ''))

        # 提取发布机构
        orgs = []
        known_orgs = ['国务院', '发改委', '工信部', '科技部', '商务部', '住建部',
                      '央行', '中国人民银行', '银保监会', '证监会', '外管局',
                      '美联储', '欧央行', '财政部']
        for org in known_orgs:
            if org in title or org in content:
                orgs.append(org)
        item['issuing_body'] = orgs[0] if orgs else None

        # 提取文号（如：国发〔2026〕1号）
        doc_id = re.search(r'[（(]\d{4}[）)]\d+号', content)
        if doc_id:
            item['document_id'] = doc_id.group()

        # 关键事实
        item['key_facts'] = self.extract_key_facts(content)
        item['content_type'] = 'policy'

        return item

    def process_stats(self, item: Dict) -> Dict:
        """处理统计数据类内容"""
        content = str(item.get('content', '') or item.get('description', ''))
        title = str(item.get('title', ''))

        # 识别指标名称
        metrics = []
        known_metrics = ['GDP', 'CPI', 'PPI', 'PMI', 'M2', 'M1', '社融',
                         '社会融资规模', '进出口', '失业率', '工业增加值',
                         '固定资产投资', '社会消费品零售总额']
        for metric in known_metrics:
            if metric in title or metric in content:
                metrics.append(metric)
        item['metrics'] = metrics

        # 提取同比/环比
        yoy = re.findall(r'同比[增长下降减少上升回落]*\s*([\d.-]+)%', content)
        mom = re.findall(r'环比[增长下降减少上升回落]*\s*([\d.-]+)%', content)
        if yoy:
            item['yoy_change'] = yoy
        if mom:
            item['mom_change'] = mom

        item['key_facts'] = self.extract_key_facts(content)
        item['content_type'] = 'statistics'

        return item

    def process_science(self, item: Dict) -> Dict:
        """处理科学/技术类内容"""
        content = str(item.get('content', '') or item.get('description', ''))
        title = str(item.get('title', ''))

        # 识别期刊
        journals = ['Nature', 'Science', 'Cell', 'PNAS', 'arXiv', 'IEEE']
        for j in journals:
            if j.lower() in (title + content).lower():
                item['journal'] = j
                break

        # 识别预印本编号
        arxiv_id = re.search(r'arXiv[:\s]*(\d{4}\.\d{4,6})', content)
        if arxiv_id:
            item['arxiv_id'] = arxiv_id.group(1)

        item['key_facts'] = self.extract_key_facts(content)
        item['content_type'] = 'science'

        return item

    def process_ipo(self, item: Dict) -> Dict:
        """处理准IPO类内容（含打新信息）"""
        content = str(item.get('content', '') or item.get('description', ''))
        title = str(item.get('title', ''))

        # 提取拟上市板块
        boards = ['科创板', '创业板', '北交所', '港交所', '上交所主板', '深交所主板']
        for board in boards:
            if board in (title + content):
                item['target_board'] = board
                break

        # 提取融资金额
        fund = re.search(r'(?:募资|融资|募集资金)\s*([\d,.]+)\s*(亿|万)?\s*(元|美元|港币)', content)
        if fund:
            item['funding_amount'] = f'{fund.group(1)}{fund.group(2) or ""}{fund.group(3)}'

        # 提取保荐机构
        sponsor = re.search(r'(?:保荐机构|保荐人)[：:]\s*([^\s,，。]+)', content)
        if sponsor:
            item['sponsor'] = sponsor.group(1)

        # 打新信息提取
        # 申购日期
        ipo_date = re.search(r'(?:申购日期|发行日期|上市日期)[：:]\s*(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?)', content + title)
        if ipo_date:
            item['ipo_date'] = ipo_date.group(1)

        # 发行价
        price = re.search(r'(?:发行价|发行价格)[：:]\s*([\d,.]+)\s*元', content + title)
        if price:
            item['ipo_price'] = price.group(1) + '元'

        # 股票代码
        code = re.search(r'(?:股票代码|证券代码)[：:]\s*(\d{6})', content + title)
        if code:
            item['stock_code'] = code.group(1)

        # 申购上限
        limit = re.search(r'(?:申购上限|网上申购上限)[：:]\s*([\d,.]+)\s*(万)?股', content)
        if limit:
            item['subscription_limit'] = f'{limit.group(1)}{limit.group(2) or ""}股'

        item['key_facts'] = self.extract_key_facts(content)
        item['content_type'] = 'ipo'

        return item

    def process(self, item: Dict) -> Dict:
        """
        根据版块类型，执行对应的信息提取策略。
        输入：已分类的item（含 section 字段）
        输出：补充了结构化信息的item，原content字段不变
        """
        section = item.get('section', '')

        if section == 'policy':
            return self.process_policy(item)
        elif section == 'finance':
            return self.process_stats(item)
        elif section == 'ipo':
            return self.process_ipo(item)
        else:
            # top_story / industry / global — 通用提取
            content = str(item.get('content', '') or item.get('description', ''))
            item['key_facts'] = self.extract_key_facts(content)
            item['content_type'] = 'general'
            return item

    def process_all(self, classified_items: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """批量处理已分类的条目"""
        for section_id, items in classified_items.items():
            for item in items:
                self.process(item)
        return classified_items


# =============================================================================
# 测试
# =============================================================================
if __name__ == '__main__':
    extractor = KeyInfoExtractor()

    test = {
        'section': 'financial_policy',
        'title': '中国人民银行决定于2026年6月15日下调金融机构存款准备金率0.5个百分点',
        'content': '为支持实体经济发展，促进综合融资成本稳中有降，中国人民银行决定于2026年6月15日下调金融机构存款准备金率0.5个百分点（不含已执行5%存款准备金率的金融机构）。此次降准共计释放长期资金约1.2万亿元。',
        'source': '中国人民银行',
    }

    result = extractor.process(test)
    print("=== 提取结果 ===")
    for k, v in result.items():
        print(f"  {k}: {v}")
