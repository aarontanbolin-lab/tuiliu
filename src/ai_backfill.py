# -*- coding: utf-8 -*-
"""
推流 — AI内容回填
在自动化中，由WorkBuddy AI读取分析任务，生成真实分析内容后回填到报告中。
"""
import json, os, sys
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, '..', 'output')
TEMPLATE_DIR = os.path.join(PROJECT_ROOT, 'templates')

SECTIONS_CONFIG = {
    'top_story':    {'name': '今日焦点',          'color': '#C41E3A'},
    'policy':       {'name': '政策风向',          'color': '#6C3483'},
    'finance':      {'name': '金融脉搏',          'color': '#1A5276'},
    'industry':     {'name': '产业前沿',          'color': '#B7950B'},
    'global':       {'name': '全球视野',          'color': '#1E8449'},
    'ipo':          {'name': '准IPO & 打新',      'color': '#D35400'},
}

jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(['html']),
)


def extract_analysis_jobs(sections: dict) -> list:
    """
    从版块数据中提取需要AI分析的条目，生成分析任务列表。
    返回可用于JSON序列化的任务列表。
    """
    jobs = []
    for section_id, items in sections.items():
        for idx, item in enumerate(items):
            job = {
                'section_id': section_id,
                'section_name': SECTIONS_CONFIG.get(section_id, {}).get('name', section_id),
                'item_index': idx,
                'title': item.get('title', ''),
                'content': item.get('content', '')[:500],  # 截取前500字供AI分析
                'source': item.get('source', ''),
                'sources': item.get('sources', []),
                'content_type': item.get('content_type', 'general'),
                # IPO特殊字段
                'ipo_board': item.get('target_board', ''),
                'ipo_funding': item.get('funding_amount', ''),
                # 需生成的分析字段 (AI填写)
                'ai_significance': item.get('ai_analysis', {}).get('significance', ''),
                'ai_opportunity': item.get('ai_analysis', {}).get('opportunity', ''),
                'ai_impact': item.get('ai_analysis', {}).get('impact', ''),
            }
            jobs.append(job)
    return jobs


def save_jobs(jobs: list) -> str:
    """保存分析任务到JSON文件，返回文件路径"""
    path = os.path.join(OUTPUT_DIR, 'analysis_jobs.json')
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    print(f'[AI] 分析任务已提取: {path} ({len(jobs)} 条)')
    return path


def load_filled_jobs(path: str = None) -> list:
    """加载已填充的分析结果"""
    if path is None:
        path = os.path.join(OUTPUT_DIR, 'analysis_filled.json')
    if not os.path.exists(path):
        print(f'[AI] 未找到填充结果: {path}')
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def apply_analysis(sections: dict, filled_jobs: list) -> dict:
    """
    将AI生成的真实分析应用到版块数据中，替换占位符。
    """
    for job in filled_jobs:
        section_id = job['section_id']
        idx = job['item_index']

        if section_id in sections and idx < len(sections[section_id]):
            item = sections[section_id][idx]

            # 替换AI分析
            significance = job.get('ai_significance', '')
            opportunity = job.get('ai_opportunity', '')
            impact = job.get('ai_impact', '')

            # 只有非占位符内容才替换
            if significance and not significance.startswith('[AI分析]'):
                item['ai_analysis'] = {
                    'significance': significance,
                    'opportunity': opportunity,
                    'impact': impact,
                }
    return sections


def render_report(sections: dict, allegory: dict, overview: str, source_status: dict, today_stamp: str = None) -> str:
    """使用回填后的数据重新渲染HTML报告。today_stamp 若不传则取当日。"""
    from datetime import datetime
    from zoneinfo import ZoneInfo
    if today_stamp:
        # 从 today_stamp 还原 datetime（取当天0点）
        now = datetime.strptime(today_stamp, "%Y-%m-%d")
    else:
        now = datetime.now(ZoneInfo("Asia/Shanghai"))
    template = jinja_env.get_template('base.html')
    weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']

    html = template.render(
        date_str=now.strftime("%Y年%m月%d日"),
        weekday=weekdays[now.weekday()],
        overview=overview,
        sections=sections,
        sections_config=SECTIONS_CONFIG,
        allegory=allegory,
        source_status=source_status,
        generation_time=now.strftime("%Y-%m-%d %H:%M:%S"),
        total_items=sum(len(v) for v in sections.values()),
    )

    # 更新输出文件
    date_dir = today_stamp if today_stamp else now.strftime("%Y-%m-%d")
    output_dir = os.path.join(OUTPUT_DIR, date_dir)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'index.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    deploy_dir = os.path.join(OUTPUT_DIR, 'deploy')
    os.makedirs(deploy_dir, exist_ok=True)
    deploy_path = os.path.join(deploy_dir, 'index.html')
    with open(deploy_path, 'w', encoding='utf-8') as f:
        f.write(html)

    latest_path = os.path.join(OUTPUT_DIR, 'latest.html')
    with open(latest_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'[AI] 回填报告已渲染: {output_path} ({len(html)} 字符)')
    return output_path


def create_filled_template():
    """
    生成一个空的 analysis_filled.json 模板，供自动化AI填充。
    自动化中，WorkBuddy阅读此模板并填充每个job的ai_字段。
    """
    # 读取已生成的 analysis_jobs.json
    jobs_path = os.path.join(OUTPUT_DIR, 'analysis_jobs.json')
    if not os.path.exists(jobs_path):
        print('[AI] 请先运行 main.py 生成 analysis_jobs.json')
        return

    with open(jobs_path, 'r', encoding='utf-8') as f:
        jobs = json.load(f)

    # 生成填充模板（清空ai_字段）
    for job in jobs:
        job['ai_significance'] = ''
        job['ai_opportunity'] = ''
        job['ai_impact'] = ''

    template_path = os.path.join(OUTPUT_DIR, 'analysis_filled.json')
    with open(template_path, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)

    print(f'[AI] 填充模板已生成: {template_path}')
    print(f'[AI] 请在自动化中，由WorkBuddy AI为每条新闻的ai_字段生成真实分析内容，然后保存到 analysis_filled.json')


# =============================================================================
# 测试
# =============================================================================
if __name__ == '__main__':
    # 模拟回填流程
    test_sections = {
        'hot_industries': [{
            'title': '人形机器人获亿元融资',
            'content': '人形机器人赛道持续火爆...',
            'source': '36氪', 'sources': ['36氪'],
            'ai_analysis': {
                'significance': '[AI分析] 此事件的核心意义在于…',
                'opportunity': '[AI分析] 相关产业链机会涉及…',
                'impact': '[AI分析] 后续潜在影响包括…',
            },
        }],
        'financial_policy': [{
            'title': '央行降准0.5个百分点',
            'content': '中国人民银行决定...',
            'source': '央行', 'sources': ['中国人民银行'],
            'ai_analysis': {
                'significance': '[AI分析] 此事件的核心意义在于…',
                'opportunity': '[AI分析] 相关产业链机会涉及…',
                'impact': '[AI分析] 后续潜在影响包括…',
            },
        }],
    }

    jobs = extract_analysis_jobs(test_sections)
    save_jobs(jobs)
    create_filled_template()
    print(f'\n共 {len(jobs)} 条分析任务')
