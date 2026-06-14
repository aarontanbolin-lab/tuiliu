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
    "hot_industries": {
        "name": "市场最热门行业",
        "priority": 1,
    },
    "supply_demand": {
        "name": "供需关系变化",
        "priority": 2,
    },
    "science_tech": {
        "name": "前沿科学与技术突破",
        "priority": 3,
    },
    "industry_policy": {
        "name": "行业政策变动",
        "priority": 4,
    },
    "financial_policy": {
        "name": "金融政策变动",
        "priority": 5,
    },
    "financial_stats": {
        "name": "金融统计数据变动",
        "priority": 6,
    },
    "pre_ipo": {
        "name": "准IPO企业追踪",
        "priority": 7,
    },
}


# =============================================================================
# 关键词规则（每个版块的关键词，带权重）
# =============================================================================
KEYWORD_RULES: Dict[str, List[Tuple[str, float]]] = {
    "hot_industries": [
        # 行业/赛道词
        ("人工智能", 2.0), ("AI", 2.0), ("大模型", 2.0), ("芯片", 1.5), ("半导体", 1.5),
        ("新能源", 1.5), ("光伏", 1.5), ("储能", 1.5), ("锂电", 1.5), ("动力电池", 1.5),
        ("电动汽车", 1.5), ("自动驾驶", 1.5), ("机器人", 1.5), ("人形机器人", 2.0),
        ("低空经济", 2.0), ("eVTOL", 2.0), ("商业航天", 2.0), ("卫星", 1.5),
        ("生物医药", 1.5), ("创新药", 1.5), ("基因", 1.5), ("合成生物", 2.0),
        ("消费电子", 1.0), ("跨境电商", 1.0), ("出海", 1.0),
        # 资本/热度词
        ("融资", 1.0), ("天使轮", 1.0), ("IPO", 1.0), ("上市", 1.0),
        ("独角兽", 1.5), ("估值", 1.0), ("市场份额", 1.0),
        ("热门", 0.5), ("风口", 0.5), ("爆火", 0.5), ("爆发", 0.5),
    ],
    "supply_demand": [
        # 供需直接信号
        ("供不应求", 3.0), ("供给短缺", 3.0), ("产能不足", 3.0), ("供应紧张", 3.0),
        ("缺货", 2.0), ("涨价", 1.5), ("价格飙升", 2.0), ("价格暴涨", 2.0),
        ("库存", 1.5), ("库存低位", 2.0), ("去库存", 1.0), ("补库存", 1.0),
        ("开工率", 1.5), ("产能利用率", 2.0), ("满产", 2.0),
        # 大宗商品
        ("大宗商品", 2.0), ("原油", 1.5), ("铜", 1.5), ("铝", 1.5),
        ("铁矿石", 1.5), ("煤炭", 1.5), ("天然气", 1.5), ("稀土", 2.0),
        ("粮食", 1.5), ("大豆", 1.5), ("玉米", 1.5),
        ("锂矿", 2.0), ("钴", 2.0), ("镍", 2.0),
        # 航运物流
        ("运价", 2.0), ("BDI", 2.0), ("波罗的海", 2.0), ("集装箱", 2.0),
        ("运费", 1.5), ("供应链", 1.0), ("物流", 0.5),
        # 期货
        ("期货", 1.0), ("上期所", 1.0), ("大商所", 1.0), ("郑商所", 1.0),
    ],
    "science_tech": [
        # 学术/研究
        ("研究发现", 2.0), ("论文", 1.5), ("发表", 1.0), ("实验", 1.0),
        ("Nature", 3.0), ("Science", 3.0), ("Cell", 3.0), ("PNAS", 3.0),
        ("arXiv", 2.0), ("预印本", 2.0), ("期刊", 1.0),
        # 科学领域
        ("量子", 2.0), ("核聚变", 2.0), ("基因编辑", 2.0), ("CRISPR", 2.0),
        ("脑机接口", 2.0), ("神经科学", 2.0), ("干细胞", 2.0),
        ("材料科学", 2.0), ("超导", 2.0), ("纳米", 1.5),
        # 技术突破
        ("技术突破", 2.0), ("重大突破", 2.0), ("首次实现", 2.0), ("首次", 1.0),
        ("新发现", 1.5), ("突破性", 1.5), ("里程碑", 1.0),
        ("AI", 1.0), ("GPU", 1.0), ("算力", 1.0),
    ],
    "industry_policy": [
        # 政策信号词
        ("国务院", 2.0), ("发改委", 2.0), ("工信部", 2.0), ("科技部", 2.0),
        ("商务部", 1.5), ("住建部", 1.5), ("交通运输部", 1.5),
        ("产业政策", 3.0), ("行业政策", 3.0), ("指导意见", 2.0),
        ("专项行动", 2.0), ("实施方案", 2.0), ("行动计划", 2.0),
        ("促进", 1.0), ("规范", 1.0), ("监管", 1.0), ("整治", 1.0),
        # 具体行业政策
        ("新能源汽车", 1.5), ("光伏补贴", 2.0), ("双碳", 2.0),
        ("数据安全", 2.0), ("平台经济", 2.0), ("反垄断", 2.0),
        ("房地产", 1.5), ("限购", 1.5), ("房贷", 1.5),
    ],
    "financial_policy": [
        # 央行/监管
        ("央行", 3.0), ("中国人民银行", 3.0), ("美联储", 3.0), ("Fed", 2.0),
        ("FOMC", 3.0), ("欧央行", 3.0), ("ECB", 2.0),
        ("货币政策", 3.0), ("财政政策", 2.0),
        ("利率", 2.0), ("加息", 2.0), ("降息", 2.0), ("降准", 2.0),
        ("LPR", 3.0), ("MLF", 2.0), ("逆回购", 2.0), ("公开市场操作", 2.0),
        ("准备金率", 3.0), ("存款准备金", 3.0),
        # 监管机构
        ("银保监会", 2.0), ("金融监督管理总局", 2.0), ("证监会", 2.0),
        ("外管局", 2.0), ("金融监管", 2.0),
        # 金融政策关键词
        ("汇率", 2.0), ("人民币", 1.0), ("美元", 1.0),
        ("资本流动", 2.0), ("跨境资金", 2.0), ("外汇", 1.5),
        # 中国独有金融政策词（加强中方识别）
        ("政治局", 3.0), ("中央经济工作", 3.0), ("国常会", 3.0),
        ("宏观调控", 3.0), ("信贷政策", 2.0), ("专项债", 2.0), ("再贷款", 2.0),
        ("特别国债", 2.0), ("政策性银行", 2.0), ("开发性金融", 2.0),
        ("存款利率", 2.0), ("房贷利率", 2.0), ("贷款市场报价", 2.0),
        ("金融委", 3.0), ("国务院金融", 3.0),
        ("结构性货币政策", 3.0), ("普惠金融", 2.0), ("碳减排支持工具", 2.0),
        ("宽松货币", 2.0), ("稳健货币", 2.0), ("精准有力", 2.0),
        ("国债收益率", 1.5), ("银行间市场", 1.5), ("质押式回购", 2.0),
    ],
    "financial_stats": [
        # 统计数据关键词
        ("GDP", 3.0), ("CPI", 3.0), ("PPI", 3.0), ("PMI", 3.0),
        ("M2", 3.0), ("M1", 3.0), ("社融", 3.0), ("社会融资规模", 3.0),
        ("信贷", 2.0), ("新增贷款", 2.0),
        ("进出口", 2.0), ("贸易顺差", 2.0), ("贸易逆差", 2.0),
        ("失业率", 2.0), ("就业", 1.0),
        ("同比增长", 1.5), ("环比增长", 1.5), ("同比", 1.0), ("环比", 1.0),
        ("统计数据", 3.0), ("经济数据", 2.0), ("宏观数据", 2.0),
        ("工业增加值", 2.0), ("固定资产投资", 2.0), ("社会消费品零售总额", 2.0),
        ("财政收支", 2.0), ("税收", 1.0),
    ],
    "pre_ipo": [
        # IPO直接信号
        ("过会", 4.0), ("首发", 3.0), ("IPO", 3.0), ("上市申请", 3.0),
        ("科创板", 3.0), ("创业板", 3.0), ("北交所", 3.0), ("港交所", 3.0),
        ("招股书", 3.0), ("发行审核", 3.0), ("注册制", 2.0),
        ("拟上市", 3.0), ("上会", 3.0), ("聆讯", 3.0),
        # 企业相关
        ("保荐", 2.0), ("募集资金", 2.0), ("融资额", 2.0),
    ],
}


# =============================================================================
# 来源到版块映射（当关键词不足以判断时使用）
# =============================================================================
SOURCE_SECTION_HINT: Dict[str, str] = {
    "财联社": "hot_industries",
    "36氪": "hot_industries",
    "华尔街见闻": "hot_industries",
    "量子位": "science_tech",
    "机器之心": "science_tech",
    "IEEE Spectrum": "science_tech",
    "Nature": "science_tech",
    "Science": "science_tech",
    "Cell": "science_tech",
    "PNAS": "science_tech",
    "MIT Technology Review": "science_tech",
    "arXiv": "science_tech",
    "Federal Reserve": "financial_policy",
    "国家统计局": "financial_stats",
    "中国人民银行": "financial_policy",
    "证监会": "pre_ipo",
    "生意社": "supply_demand",
    "上海期货交易所": "supply_demand",
    "海关总署": "financial_stats",
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
            return 'hot_industries'  # 无法判断，归入热门行业

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
