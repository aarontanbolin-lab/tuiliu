# -*- coding: utf-8 -*-
"""
推流 — 数据处理管线
串联去重、分类、提取、验证四大模块
"""
from .dedup import DedupEngine
from .classifier import SectionClassifier
from .extractor import KeyInfoExtractor
from .verifier import CrossVerifier


class ProcessingPipeline:
    """数据处理管线 —— 一站式处理"""

    def __init__(self):
        self.deduplicator = DedupEngine()
        self.classifier = SectionClassifier()
        self.extractor = KeyInfoExtractor()
        self.verifier = CrossVerifier()

    def run(self, raw_items: list) -> dict:
        """
        执行完整处理管线。
        输入：原始采集条目列表 [{url, title, content, source, ...}]
        输出：按版块分类、去重、提取、验证后的结构化数据
        """
        # 第1步：去重
        deduplicated = self.deduplicator.deduplicate(raw_items)

        # 第2步：分类
        classified = self.classifier.classify_all(deduplicated)

        # 第3步：信息提取
        extracted = self.extractor.process_all(classified)

        # 第4步：交叉验证
        verified = self.verifier.verify_all(extracted)

        # 状态报告
        report = self.verifier.generate_status_report(verified)

        return {
            'sections': verified,
            'summary': {
                'raw_count': len(raw_items),
                'deduplicated_count': len(deduplicated),
                **report,
            }
        }

    def reset(self):
        """重置管线（每日采集前调用）"""
        self.deduplicator.reset()
