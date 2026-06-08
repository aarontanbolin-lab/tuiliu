# -*- coding: utf-8 -*-
"""
推流 — 部署与推送模块
CloudStudio 自动部署 + 飞书 Webhook 消息推送
"""
import os, yaml, json
import httpx


class FeishuPusher:
    """飞书自定义机器人消息推送"""

    def __init__(self, webhook_url: str = None):
        if webhook_url is None:
            # 从配置文件读取 (deploy.py → deploy/ → src/ → 推流/)
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                'config', 'settings.yaml'
            )
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            webhook_url = config.get('feishu', {}).get('webhook_url', '')

        self.webhook_url = webhook_url

    def send_text(self, text: str) -> bool:
        """发送纯文本消息"""
        if not self.webhook_url:
            print('[飞书] Webhook 未配置，跳过推送')
            return False

        payload = {
            'msg_type': 'text',
            'content': {'text': text},
        }
        try:
            r = httpx.post(self.webhook_url, json=payload, timeout=10)
            if r.status_code == 200:
                resp = r.json()
                if resp.get('code') == 0 or resp.get('StatusCode') == 0:
                    print(f'[飞书] 推送成功')
                    return True
            print(f'[飞书] 推送失败: HTTP {r.status_code} {r.text[:200]}')
            return False
        except Exception as e:
            print(f'[飞书] 推送异常: {e}')
            return False

    def send_rich(self, title: str, url: str, summary: str = '',
                  items_count: int = 0, allegory_hint: str = '') -> bool:
        """发送富文本卡片消息"""
        if not self.webhook_url:
            print('[飞书] Webhook 未配置，跳过推送')
            return False

        # 构建内容摘要
        content_parts = [summary[:120]] if summary else []
        content_parts.append(f'\n📊 今日收录 {items_count} 条深度资讯')
        if allegory_hint:
            content_parts.append(f'📖 每日寓言：{allegory_hint[:40]}')

        # 飞书富文本消息（使用 post 格式实现丰富排版）
        post_content = [[
            {'tag': 'text', 'text': '📰 '},
            {'tag': 'a', 'text': title, 'href': url},
        ]]

        if content_parts:
            post_content.append([
                {'tag': 'text', 'text': '\n'.join(content_parts)},
            ])

        post_content.append([
            {'tag': 'text', 'text': '\n\n'},
            {'tag': 'a', 'text': '👉 点击查看完整日报', 'href': url},
        ])

        payload = {
            'msg_type': 'post',
            'content': {
                'post': {
                    'zh_cn': {
                        'title': title,
                        'content': post_content,
                    }
                }
            },
        }

        try:
            r = httpx.post(self.webhook_url, json=payload, timeout=10)
            if r.status_code == 200:
                resp = r.json()
                if resp.get('code') == 0 or resp.get('StatusCode') == 0:
                    print(f'[飞书] 富文本推送成功')
                    return True
            print(f'[飞书] 推送失败: HTTP {r.status_code} {r.text[:200]}')
            return False
        except Exception as e:
            print(f'[飞书] 推送异常: {e}')
            return False


class ReportDeployer:
    """报告部署器 — CloudStudio 部署 + 飞书推送"""

    def __init__(self):
        self.pusher = FeishuPusher()

    def deploy(self, html_path: str, report_info: dict = None, cloud_url: str = None) -> dict:
        """
        部署报告并推送通知。
        cloud_url: CloudStudio 部署后的公开 URL（由 WorkBuddy 自动化提供）
        返回 {'deployed': bool, 'url': str, 'pushed': bool, 'deploy_dir': str}
        """
        result = {'deployed': False, 'url': '', 'pushed': False}

        deploy_dir = os.path.dirname(html_path)
        result['deploy_dir'] = deploy_dir

        # 优先使用 CloudStudio 公开 URL，否则用本地路径
        url = cloud_url or f'file://{html_path}'
        result['url'] = url
        result['deployed'] = bool(cloud_url)

        if cloud_url:
            print(f'[部署] CloudStudio URL: {cloud_url}')
        else:
            print(f'[部署] 本地路径: {html_path}')
            print(f'[部署] 待 CloudStudio 部署获取远程URL')

        # 2. 飞书推送
        if report_info:
            title = report_info.get('title', '推流 · 每日内参')
            items_count = report_info.get('items_count', 0)
            summary = report_info.get('summary', '')
            allegory_hint = report_info.get('allegory_hint', '')

            # 先尝试富文本
            if not self.pusher.send_rich(
                title=title,
                url=result['url'],
                summary=summary,
                items_count=items_count,
                allegory_hint=allegory_hint,
            ):
                # 降级为纯文本
                text = f"{title}\n\n{summary}\n\n今日收录 {items_count} 条\n👉 {result['url']}"
                self.pusher.send_text(text)
                result['pushed'] = True
            else:
                result['pushed'] = True

        return result


# =============================================================================
# 测试
# =============================================================================
if __name__ == '__main__':
    deployer = ReportDeployer()
    result = deployer.deploy(
        html_path='../output/preview.html',
        report_info={
            'title': '推流 · 每日内参 2026年6月8日',
            'items_count': 14,
            'summary': '今日焦点：人形机器人融资热潮、央行降准、拓扑量子比特突破',
            'allegory_hint': '涌现 (Emergence)',
        },
    )
    print(f'\n部署结果: {json.dumps(result, ensure_ascii=False, indent=2)}')
