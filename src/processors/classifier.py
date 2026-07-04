# -*- coding: utf-8 -*-
"""
推流 — 版块分类器
将采集到的资讯自动归类到8大版块中
"""
from typing import Dict, List, Tuple


# =============================================================================
# 版块定义
# =============================================================================
SECTIONS = {
    "top_story": {
        "name": "今日焦点",
        "priority": 1,
    },
    "policy": {
        "name": "政策风向",
        "priority": 2,
    },
    "finance": {
        "name": "金融脉搏",
        "priority": 3,
    },
    "industry": {
        "name": "产业前沿",
        "priority": 4,
    },
    "global": {
        "name": "全球视野",
        "priority": 5,
    },
    "ipo": {
        "name": "准IPO & 打新",
        "priority": 6,
    },
    "xwlb": {
        "name": "昨日联播",
        "priority": 7,
    },
}


# =============================================================================
# 关键词规则（每个版块的关键词，带权重）
# =============================================================================
KEYWORD_RULES: Dict[str, List[Tuple[str, float]]] = {
    "top_story": [
        # 重大突发事件、顶层信号
        ("突发", 3.0), ("紧急", 3.0), ("重磅", 3.0), ("习近平", 3.0),
        ("政治局", 3.0), ("中央经济工作", 3.0),
        ("战争", 3.0), ("危机", 3.0), ("崩盘", 3.0),
    ],
    "policy": [
        # 部委与政策信号
        ("国务院", 2.0), ("发改委", 2.0), ("工信部", 2.0), ("科技部", 2.0),
        ("商务部", 1.5), ("住建部", 1.5), ("交通运输部", 1.5),
        ("产业政策", 3.0), ("行业政策", 3.0), ("指导意见", 2.0),
        ("专项行动", 2.0), ("实施方案", 2.0), ("行动计划", 2.0),
        ("通知", 1.0), ("公告", 1.0), ("印发", 1.5),
        ("规范", 1.0), ("监管", 1.0), ("整治", 1.0),
        # 具体行业政策
        ("新能源汽车", 1.5), ("双碳", 2.0), ("光伏", 1.5),
        ("数据安全", 2.0), ("平台经济", 2.0), ("反垄断", 2.0),
        ("房地产", 1.5), ("限购", 1.5), ("房贷", 1.5),
        ("低空经济", 2.0), ("商业航天", 2.0),
    ],
    "finance": [
        # 央行/监管
        ("央行", 3.0), ("中国人民银行", 3.0), ("美联储", 3.0),
        ("货币政策", 3.0), ("财政政策", 2.0),
        ("利率", 2.0), ("加息", 2.0), ("降息", 2.0), ("降准", 2.0),
        ("LPR", 3.0), ("MLF", 2.0), ("逆回购", 2.0),
        ("准备金率", 3.0), ("存款准备金", 3.0),
        ("银保监会", 2.0), ("金融监督管理总局", 2.0), ("证监会", 2.0),
        ("外管局", 2.0), ("金融监管", 2.0),
        ("汇率", 2.0), ("人民币", 1.0), ("美元", 1.0),
        ("资本流动", 2.0), ("跨境资金", 2.0), ("外汇", 1.5),
        # 中方金融独有
        ("宏观调控", 3.0), ("专项债", 2.0), ("再贷款", 2.0),
        ("特别国债", 2.0), ("存款利率", 2.0), ("房贷利率", 2.0),
        ("金融委", 3.0), ("结构性货币", 3.0), ("普惠金融", 2.0),
        # 统计数据
        ("GDP", 3.0), ("CPI", 3.0), ("PPI", 3.0), ("PMI", 3.0),
        ("M2", 3.0), ("M1", 3.0), ("社融", 3.0), ("社会融资规模", 3.0),
        ("信贷", 2.0), ("新增贷款", 2.0),
        ("进出口", 2.0), ("贸易顺差", 2.0),
        ("失业率", 2.0), ("就业", 1.0),
        ("同比增长", 1.5), ("环比增长", 1.5),
        ("统计数据", 3.0), ("经济数据", 2.0), ("宏观数据", 2.0),
        ("工业增加值", 2.0), ("固定资产投资", 2.0), ("社会消费品零售总额", 2.0),
    ],
    "industry": [
        # 行业/赛道
        ("人工智能", 2.0), ("AI", 2.0), ("大模型", 2.0), ("芯片", 1.5), ("半导体", 1.5),
        ("新能源", 1.5), ("储能", 1.5), ("锂电", 1.5), ("动力电池", 1.5),
        ("电动汽车", 1.5), ("自动驾驶", 1.5), ("机器人", 1.5), ("人形机器人", 2.0),
        ("eVTOL", 2.0), ("卫星", 1.5),
        ("生物医药", 1.5), ("创新药", 1.5), ("基因", 1.5), ("合成生物", 2.0),
        ("消费电子", 1.0), ("跨境电商", 1.0), ("出海", 1.0),
        # 供需信号
        ("供不应求", 3.0), ("供给短缺", 3.0), ("产能不足", 3.0),
        ("缺货", 2.0), ("涨价", 1.5), ("价格飙升", 2.0),
        ("库存", 1.5), ("开工率", 1.5), ("产能利用率", 2.0), ("满产", 2.0),
        # 大宗商品
        ("大宗商品", 2.0), ("原油", 1.5), ("铜", 1.5), ("铝", 1.5),
        ("铁矿石", 1.5), ("稀土", 2.0), ("锂矿", 2.0),
        ("运价", 2.0), ("BDI", 2.0), ("集装箱", 2.0),
        # 资本/热度
        ("融资", 1.0), ("天使轮", 1.0), ("IPO", 1.0), ("上市", 1.0),
        ("独角兽", 1.5), ("估值", 1.0), ("市场份额", 1.0),
    ],
    "global": [
        ("美联储", 3.0), ("Fed", 2.0), ("FOMC", 3.0),
        ("欧央行", 3.0), ("ECB", 2.0), ("日本央行", 3.0),
        ("国际", 1.0), ("全球", 1.0), ("美国", 1.0), ("欧洲", 1.0),
        ("地缘", 2.0), ("制裁", 2.0), ("关税", 2.0), ("贸易战", 2.0),
        ("产业链转移", 2.0), ("供应链", 1.0),
    ],
    "ipo": [
        # IPO直接信号
        ("过会", 4.0), ("首发", 3.0), ("IPO", 3.0), ("上市申请", 3.0),
        ("科创板", 3.0), ("创业板", 3.0), ("北交所", 3.0), ("港交所", 3.0),
        ("招股书", 3.0), ("发行审核", 3.0), ("注册制", 2.0),
        ("拟上市", 3.0), ("上会", 3.0), ("聆讯", 3.0),
        # 打新
        ("申购", 4.0), ("新股", 4.0), ("中签", 4.0), ("打新", 4.0),
        ("发行价", 3.0), ("网上发行", 3.0), ("上市公告", 3.0),
        ("配售", 2.0), ("回拨", 2.0),
        # 企业相关
        ("保荐", 2.0), ("募集资金", 2.0), ("融资额", 2.0),
    ],
    "xwlb": [
        # 新闻联播独有信号
        ("新闻联播", 5.0), ("习近平", 4.0), ("李强", 3.0),
        ("中央军委", 3.0), ("国务院", 2.0), ("政治局", 3.0),
    ],
}


# =============================================================================
# 来源到版块映射（当关键词不足以判断时使用）
# =============================================================================
SOURCE_SECTION_HINT: Dict[str, str] = {
    "财联社": "finance",
    "36氪": "industry",
    "华尔街见闻": "finance",
    "证券时报": "finance",
    "量子位": "industry",
    "Federal Reserve": "global",
    "国家统计局": "finance",
    "中国人民银行": "policy",
    "证监会": "ipo",
    "上海期货交易所": "finance",
    "海关总署": "finance",
    "新闻联播": "xwlb",
}


class SectionClassifier:
    """版块智能分类器"""

    def __init__(self, keyword_rules: Dict = None):
        self.rules = keyword_rules or KEYWORD_RULES

    def _score_section(self, text: str, section: str) -> float:
        """计算文本对某个版块的匹配得分"""
        keywords = self.rules.get(section, [])
        total = 0.0
        text_lower = text.lower()
        for keyword, weight in keywords:
            if keyword.lower() in text_lower:
                total += weight
        return total

    def classify(self, item: Dict) -> str:
        """
        分类单条资讯。
        返回版块ID（如 'financial_policy'），或 'hot_industries' 作为兜底。
        """
        # 汇总所有可用的文本
        text_parts = []
        for key in ('title', 'content', 'summary', 'description'):
            val = item.get(key, '')
            if val:
                text_parts.append(str(val))
        combined_text = ' '.join(text_parts)

        if not combined_text.strip():
            return 'industry'  # 无法判断，归入产业前沿

        # 计算每个版块的得分
        scores = {}
        for section_id in self.rules:
            scores[section_id] = self._score_section(combined_text, section_id)

        # 来源作为弱提示
        source = item.get('source', '')
        if source in SOURCE_SECTION_HINT:
            hint_section = SOURCE_SECTION_HINT[source]
            scores[hint_section] = scores.get(hint_section, 0) + 0.5

        # 特殊规则：如果明确包含IPO关键词，优先归入pre_ipo
        pre_ipo_score = scores.get('pre_ipo', 0)
        if pre_ipo_score >= 3.0:
            return 'pre_ipo'

        # 特殊规则：统计数据优先
        stats_score = scores.get('financial_stats', 0)
        if stats_score >= 3.0 and '政策' not in combined_text:
            return 'financial_stats'

        # 取最高得分版块
        best_section = max(scores, key=scores.get)
        best_score = scores[best_section]

        # 如果最高得分太低（<0.5），用来源提示兜底
        if best_score < 0.5 and source in SOURCE_SECTION_HINT:
            return SOURCE_SECTION_HINT[source]

        return best_section

    def classify_all(self, items: List[Dict]) -> Dict[str, List[Dict]]:
        """
        批量分类。
        返回 {section_id: [items]} 的字典。
        """
        result = {section_id: [] for section_id in SECTIONS}
        for item in items:
            section = self.classify(item)
            item['section'] = section
            item['section_name'] = SECTIONS.get(section, {}).get('name', section)
            result[section].append(item)
        return result


# =============================================================================
# 测试
# =============================================================================
if __name__ == '__main__':
    classifier = SectionClassifier()

    test_items = [
        {'title': '美联储维持利率不变，鲍威尔暗示年内或降息', 'content': 'FOMC声明维持联邦基金利率在5.25%-5.50%不变', 'source': '财联社'},
        {'title': '6月CPI同比上涨0.3%，PPI降幅收窄', 'content': '国家统计局今日发布数据显示，全国居民消费价格同比上涨0.3%', 'source': '国家统计局'},
        {'title': '某半导体公司科创板过会，拟募资50亿元', 'content': '该公司主营AI芯片设计，已通过科创板上市委审核', 'source': '证监会'},
        {'title': '人形机器人赛道持续火爆，多家公司宣布新一轮融资', 'content': '优必选、傅利叶等企业获亿元级融资', 'source': '36氪'},
        {'title': '工信部印发人形机器人创新发展指导意见', 'content': '工信部发文提出到2027年人形机器人技术创新能力显著提升', 'source': '工信部'},
        {'title': 'Nature: 量子计算实现新突破，首次演示拓扑量子比特', 'content': '研究人员在Nature发表论文，展示了拓扑量子比特的首次实验验证', 'source': 'Nature'},
        {'title': '全球铜库存降至十年低位，供给持续紧张', 'content': 'LME铜库存已降至15年来最低水平', 'source': '生意社'},
    ]

    result = classifier.classify_all(test_items)
    for section_id, items in result.items():
        if not items:
            continue
        name = SECTIONS[section_id]['name']
        print(f"\n{'='*40}")
        print(f"  {name} ({len(items)}条)")
        print(f"{'='*40}")
        for item in items:
            print(f"  [{item['source']}] {item['title'][:60]}")
