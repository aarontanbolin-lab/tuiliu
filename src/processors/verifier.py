# -*- coding: utf-8 -*-
"""
推流 — 交叉验证模块
对重要信息进行多源交叉验证，标注可靠性。
"""
from typing import Dict, List


class CrossVerifier:
    """交叉验证器 —— 标记信息可靠性"""

    def __init__(self, verification_threshold: int = 2):
        """
        Args:
            verification_threshold: 超过此数量的独立信源确认，视为"已验证"
        """
        self.threshold = verification_threshold

    @staticmethod
    def _reliability_label(source_count: int) -> str:
        """根据来源数量生成可靠性标签"""
        if source_count >= 3:
            return '多源验证'
        elif source_count == 2:
            return '交叉验证'
        elif source_count == 1:
            return '单一信源'
        else:
            return '未知来源'

    @staticmethod
    def _reliability_icon(source_count: int) -> str:
        if source_count >= 3:
            return '✓✓'
        elif source_count == 2:
            return '✓'
        elif source_count == 1:
            return '⚠'
        return '?'

    def verify_item(self, item: Dict) -> Dict:
        """验证单条资讯的可靠性"""
        sources = item.get('sources', [item.get('source', '')])
        source_count = len(set(s for s in sources if s))

        item['source_count'] = source_count
        item['reliability'] = self._reliability_label(source_count)
        item['reliability_icon'] = self._reliability_icon(source_count)

        # 对单一信源的重要信息添加警告
        if source_count < 2:
            # 检查是否为官方信源（官方信源单一来源也相对可信）
            official_sources = [
                '国家统计局', '中国人民银行', '央行', '国务院', '发改委',
                '工信部', '证监会', '银保监会', '海关总署', '外管局',
                'Federal Reserve', '美联储', 'ECB', '欧央行',
                'Nature', 'Science', 'Cell', 'PNAS',
            ]
            primary_source = sources[0] if sources else ''
            is_official = any(org in primary_source for org in official_sources)

            if not is_official:
                item['warning'] = '单一信源报道，建议关注后续交叉验证'
            else:
                item['warning'] = None
        else:
            item['warning'] = None

        # 标记是否为官方一手信息
        item['is_primary_source'] = any(
            org in str(item.get('source', ''))
            for org in ['国家统计局', '中国人民银行', '央行', '国务院', '证监会',
                        '发改委', '工信部', '海关总署', 'Federal Reserve', '美联储']
        )

        return item

    def verify_all(self, classified_items: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """批量验证所有条目"""
        for section_id, items in classified_items.items():
            for item in items:
                self.verify_item(item)
        return classified_items

    def generate_status_report(self, classified_items: Dict[str, List[Dict]]) -> Dict:
        """生成信源状态报告"""
        total = 0
        verified = 0
        single_source = 0
        warnings = 0

        for items in classified_items.values():
            for item in items:
                total += 1
                sources = item.get('sources', [item.get('source', '')])
                count = len(set(s for s in sources if s))
                if count >= 2:
                    verified += 1
                else:
                    single_source += 1
                if item.get('warning'):
                    warnings += 1

        return {
            'total_items': total,
            'multi_source_verified': verified,
            'single_source_items': single_source,
            'warned_items': warnings,
            'verification_rate': f'{verified/total*100:.1f}%' if total > 0 else 'N/A',
        }


# =============================================================================
# 测试
# =============================================================================
if __name__ == '__main__':
    verifier = CrossVerifier()

    classified = {
        'financial_policy': [
            {
                'title': '央行降准0.5个百分点',
                'sources': ['中国人民银行', '财联社', '华尔街见闻'],
                'source': '中国人民银行',
            },
            {
                'title': '某地楼市新政',
                'sources': ['36氪'],
                'source': '36氪',
            },
        ],
        'science_tech': [
            {
                'title': '量子计算新突破',
                'sources': ['Nature'],
                'source': 'Nature',
            },
        ],
    }

    result = verifier.verify_all(classified)

    for section, items in result.items():
        print(f"\n--- {section} ---")
        for item in items:
            icon = item['reliability_icon']
            label = item['reliability']
            warning = f" [{item['warning']}]" if item.get('warning') else ''
            print(f"  {icon} [{label}] {item['title']}{warning}")

    report = verifier.generate_status_report(result)
    print(f"\n=== 状态报告 ===")
    for k, v in report.items():
        print(f"  {k}: {v}")
