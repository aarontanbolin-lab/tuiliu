# -*- coding: utf-8 -*-
"""
推流 — AI内容生成器
负责日报的AI分析、概览、寓言等智能内容生成。
在自动化运行时，由WorkBuddy AI填充；独立运行时使用模板占位。
"""
import random
from typing import Dict, List


# =============================================================================
# 每日寓言：概念库
# =============================================================================
CONCEPT_POOL = [
    {
        'concept': '奈奎斯特采样定理',
        'field': '信号处理',
        'story_seed': '一个盲人想知道河流的形状。他不能跳进河里（那样会扰动水流），只能在岸边每隔一段距离伸手触摸水面。他触摸得越频繁，心中绘出的河流形状越接近真实。但如果他触摸的频率低于河面波纹变化速度的一半，他画出的河就会和真实的河完全不同——那是一条根本不存在的河。',
        'explanation_seed': '奈奎斯特采样定理指出：要无失真地重建一个信号，采样频率必须至少是信号最高频率的两倍。盲人触摸水面就是"采样"，河面波纹就是"信号"。寓言中的"触摸频率太低会画出不存在的河"正是混叠现象的本质——欠采样会导致虚假信号的出现。这在工程中处处可见：数字音频的采样率、CT扫描的断层间隔、甚至我们理解世界的方式——如果你对一个复杂系统的观察频率不够，你看到的将是幻觉而非真相。',
    },
    {
        'concept': '随机梯度下降 (SGD)',
        'field': '机器学习',
        'story_seed': '山谷里有一个失明的老人，他每天都在寻找山谷的最低点——传说那里有一口永不干涸的井。他不能一次看清整个山谷的地形，只能每走一步就用拐杖探一探脚下的坡度，然后朝着下坡的方向迈一小步。有时候他走错了方向，因为脚下的石头给他了错误的坡度信号；有时候他走过的路坑坑洼洼，在局部的小凹地里打转。但他从不一次迈太大的步子，也从不只看一块石头就决定方向。日复一日，年复一年，他的位置越来越低。',
        'explanation_seed': '这就是随机梯度下降（SGD）——机器学习中最核心的优化算法。失明老人代表模型参数，山谷代表损失函数的曲面，拐杖探路代表用一小批（mini-batch）数据计算梯度，每次向下坡迈一小步就是参数更新。寓言中的"有时被石头误导"对应SGD的随机性噪声——梯度估计不完美，但大量小步的平均效果是收敛的。"在小凹地里打转"对应局部最优解——SGD的随机性反而有助于跳出浅的局部最小值。整个故事的核心洞察是：在信息不完整、噪声不可避的环境中，小步快跑比大步跨越更可靠。',
    },
    {
        'concept': '马尔可夫毯 (Markov Blanket)',
        'field': '概率图模型/认知科学',
        'story_seed': '从前有个城邦，城邦里每个人都只认识自己的邻居。一个人想要了解世界，不必走出城邦去亲眼看见远方的事——他只需观察邻居们的反应。如果所有邻居都很焦虑，他就知道远方可能出了大事；如果邻居们都很平静，他就知道天下太平。奇怪的是，一旦他知道了他所有邻居的状态，远方的任何事情都不能给他更多的信息了。有一个哲学家给这种现象取了个名字：一个人的认知边界，恰好由他所有的邻居们组成了一道无形的毯子，把他和世界的其余部分隔开了。',
        'explanation_seed': '这就是马尔可夫毯——概率图模型和自由能原理中的核心概念。一个人的邻居们（在贝叶斯网络中指的是父节点、子节点和子节点的其他父节点）构成了一个"信息边界"：给定毯子内部所有节点的状态，毯子外部的任何节点都与内部节点条件独立。寓言中的"邻居们焦虑就知道远方出了大事"对应了信息通过马尔可夫毯的传导机制；"知道了所有邻居就不需要走出去"对应条件独立性的数学定义。这一概念在认知科学中被弗里斯顿（Karl Friston）用于解释意识——我们的意识本身可能就是大脑内部状态与其外部世界之间的马尔可夫毯。',
    },
    {
        'concept': '涌现 (Emergence)',
        'field': '复杂系统',
        'story_seed': '有一群蚂蚁，每一只都遵循三条极简单的规则：跟着前面蚂蚁留下的气味走、遇到食物就搬回家、气味淡了就换条路。没有一只蚂蚁知道"蚁群"长什么样，没有一只蚂蚁在"管理"其他蚂蚁，没有蚁王在发号施令。但三个月后，这群蚂蚁建起了一座结构精巧、通风良好、育儿室和粮仓分布合理的蚁巢——其复杂程度远超任何一只蚂蚁的理解能力。一位路过的人类科学家看呆了：这是他见过的最美丽的建筑，但它不是由任何一个建筑师设计的。',
        'explanation_seed': '这就是涌现——复杂系统中的宏观秩序从微观简单规则的相互作用中自发产生。蚁群中的每只蚂蚁遵循的"气味跟随"、"信息素更新"等规则，等同于多主体系统中的个体行为函数。蚁巢的复杂结构不是任何一只蚂蚁"聪明"的结果，而是大量简单个体交互产生的系统属性。同样的逻辑解释了鸟群的V字形编队（每只鸟只需保持与邻居的距离和方向）、人类语言（没有"语言设计师"，语法规则自发涌现）、甚至自由市场的价格机制（没有"定价者"，供需博弈涌现出价格）。理解涌现的关键启示是：复杂系统的行为不能通过研究其组成部分来预测——你解剖一只蚂蚁，永远找不到蚁巢。',
    },
    {
        'concept': '香农熵与信息论',
        'field': '信息论',
        'story_seed': '有一个小镇，镇上居民每天早晨都要在广场上聚一次，由镇长宣布当天的天气。镇长是个沉默寡言的人，他不会说"今天是晴天"，而是用一扇窗来传递信息——如果今天是晴天，他打开窗户；如果是雨天，他关着窗户。居民们都觉得这办法很妙：一件事只需要一个动作就能说清楚。直到有一天，镇长说他要出远门，由他的副手代为传达天气。副手是个话痨，每次都要说足一百个字，但居民们却发现——他那一百个字里真正有用的信息，也就和镇长的开窗关窗一样多。',
        'explanation_seed': '这就是香农熵的核心洞察：信息量取决于事件的不确定性，而非消息的长度。镇长两扇窗对应两种天气，每次传递的信息量是1比特（log₂2=1）。副手的"一百个字"如果仍然是传递两种天气中的一种，其信息量仍然是1比特——冗余的99个字是零信息。香农熵量化了"惊讶程度"：越不可能发生的事件，一旦发生，携带的信息量越大。这一概念影响了从数据压缩（去除冗余）、密码学（信息隐藏）、到机器学习（交叉熵损失函数）的几乎所有数字技术。正如寓言暗示的：重要的不是你说了多少，而是你说了之后消解了多少不确定性。',
    },
    {
        'concept': '囚徒困境与演化博弈',
        'field': '博弈论',
        'story_seed': '两个商人犯了事，被关在相邻的牢房里。狱卒分别告诉他们：如果你举报对方而对方保持沉默，你立刻自由，对方判十年；如果你们都举报对方，各判五年；如果你们都沉默，因为没有证据，各判一年。夜深人静时，两个人都盯着天花板在想同一件事：如果对方举报了我而我没有举报他，我就完了。所以不管对方怎么做，举报都是更"安全"的选择。第二天，他们都举报了对方。各判五年。多年后他们的故事被一个生物学家听到，他在森林里发现了一群蝙蝠——这些蝙蝠每天晚上出去觅食，回来后会把自己吸的血液反刍给那些运气不好的同伴。谁如果只接受而不回报，就被整个群体记住并排斥。',
        'explanation_seed': '囚徒困境揭示了个人理性与集体理性的冲突：每个人做出"对自己最优"的选择（举报=背叛），导致所有人共同堕入更差的结果（各判五年 vs 各判一年）。而蝙蝠的故事是演化博弈论中的"以牙还牙"（Tit-for-Tat）策略：在重复博弈中，合作可以自然演化出来——只要参与者能够记住对方的历史行为并对背叛实施惩罚。核心洞见是：合作的秩序不需要一个"管理者"来强制执行，它可以自发地从重复互动和声誉机制中涌现。这一模型被用来解释从国家间的军备竞赛、企业间的价格战、到气候变化谈判中"搭便车"问题的一切困局——为什么聪明人集体做蠢事，以及为什么蠢事做多了，聪明人会学会合作。',
    },
]


class AIGenerator:
    """AI内容生成器 —— 日报智能内容的生产模块"""

    def __init__(self):
        self._concepts_used = set()

    # ---- 今日概览 ----
    def generate_overview(self, sections: Dict[str, List[Dict]]) -> str:
        """
        基于各版块内容生成今日概览摘要。
        在实际运行时，由WorkBuddy AI直接生成并替换此输出。
        """
        # 统计各版块头条
        headlines = []
        section_names = {
            'hot_industries': '市场热点', 'supply_demand': '供需变化',
            'science_tech': '科学前沿', 'industry_policy': '行业政策',
            'financial_policy': '金融政策', 'financial_stats': '金融数据',
            'pre_ipo': '准IPO',
        }
        for section_id, items in sections.items():
            if items:
                name = section_names.get(section_id, section_id)
                headlines.append(f"{name}方面，{items[0]['title'][:40]}")

        if headlines:
            return '今日' + '；'.join(headlines[:5]) + '。'
        return '今日暂无重大资讯更新。'

    # ---- 单条新闻AI分析 ----
    def generate_item_analysis(self, item: Dict) -> Dict:
        """
        为单条新闻生成AI分析（意义/产业链机会/后续影响）。
        在实际运行时，由WorkBuddy AI填充。
        """
        return {
            'significance': f"[AI分析] 此事件({item['title'][:30]}...)的核心意义在于…",
            'opportunity': '[AI分析] 相关产业链机会涉及…',
            'impact': '[AI分析] 后续潜在影响包括…',
        }

    # ---- 每日寓言 ----
    def generate_allegory(self) -> Dict:
        """
        从概念库中选择一个尚未用过的研究生层级概念，生成寓言。
        概念库用完后循环重置。
        """
        if len(self._concepts_used) >= len(CONCEPT_POOL):
            self._concepts_used.clear()

        # 随机选择未使用的概念
        available = [c for c in CONCEPT_POOL if c['concept'] not in self._concepts_used]
        concept = random.choice(available) if available else random.choice(CONCEPT_POOL)
        self._concepts_used.add(concept['concept'])

        # 将story_seed和explanation_seed拆分为段落
        story_paras = [p.strip() for p in concept['story_seed'].split('\n') if p.strip()]
        if not story_paras:
            story_paras = [concept['story_seed']]

        explain_paras = [p.strip() for p in concept['explanation_seed'].split('\n') if p.strip()]
        if not explain_paras:
            explain_paras = [concept['explanation_seed']]

        return {
            'story_paragraphs': story_paras,
            'concept': f"概念：{concept['concept']}（{concept['field']}）",
            'explanation_paragraphs': explain_paras,
        }

    # ---- 批量AI分析 ----
    def analyze_all_items(self, sections: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """为所有版块的所有条目生成AI分析"""
        for section_id, items in sections.items():
            for item in items:
                if 'ai_analysis' not in item:
                    item['ai_analysis'] = self.generate_item_analysis(item)
        return sections


# 测试
if __name__ == '__main__':
    gen = AIGenerator()
    for i in range(3):
        a = gen.generate_allegory()
        print(f"\n=== 寓言 {i+1}: {a['concept']} ===")
        print('故事:', a['story_paragraphs'][0][:80], '...')
