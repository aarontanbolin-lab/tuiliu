# -*- coding: utf-8 -*-
"""
推流 — 主入口
每日报告生成的完整编排：采集 → 处理 → AI分析 → 渲染 → 输出
"""
import sys, io, os, yaml
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from zoneinfo import ZoneInfo
from jinja2 import Environment, FileSystemLoader, select_autoescape

from processors.pipeline import ProcessingPipeline
from ai_generator import AIGenerator
from deploy.deploy import ReportDeployer
from ai_backfill import extract_analysis_jobs, save_jobs, create_filled_template
from collectors.collector import RSSCollector, fetch_arxiv, fetch_cls_telegraph

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(PROJECT_ROOT, '..', 'config')
TEMPLATE_DIR = os.path.join(PROJECT_ROOT, 'templates')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, '..', 'output')

# GitHub Pages 公网URL
PUBLIC_URL = 'https://aarontanbolin-lab.github.io/tuiliu/'

# Jinja2 环境
jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(['html']),
)

# 版块配置
SECTIONS_CONFIG = {
    'hot_industries':    {'name': '一、市场最热门行业',    'color': '#C41E3A'},
    'supply_demand':     {'name': '二、供需关系变化',      'color': '#B7950B'},
    'science_tech':      {'name': '三、前沿科学与技术突破',  'color': '#1E8449'},
    'industry_policy':   {'name': '四、行业政策变动',      'color': '#6C3483'},
    'financial_policy':  {'name': '五、金融政策变动',      'color': '#1A5276'},
    'financial_stats':   {'name': '六、金融统计数据变动',   'color': '#1A5276'},
    'pre_ipo':           {'name': '七、准IPO企业追踪',     'color': '#D35400'},
}


def load_config():
    """加载全局配置"""
    settings_path = os.path.join(CONFIG_DIR, 'settings.yaml')
    with open(settings_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def collect_raw_data(config: dict) -> tuple:
    """
    从所有已验证信源采集原始数据。
    返回 (items_list, source_status_dict)
    """
    all_items = []
    source_status = {}

    # 1. RSS采集
    print('  [采集] RSS源...')
    rss = RSSCollector()
    rss_items = rss.fetch_all()
    all_items.extend(rss_items)
    source_status.update(rss.get_status())

    # 2. arXiv论文
    print('  [采集] arXiv...')
    arxiv_items = fetch_arxiv(max_results=5)
    all_items.extend(arxiv_items)
    source_status['arXiv'] = 'ok' if arxiv_items else 'failed'

    # 3. 财联社电报
    print('  [采集] 财联社电报...')
    cls_items = fetch_cls_telegraph(max_items=20)
    all_items.extend(cls_items)
    source_status['财联社'] = 'ok' if cls_items else 'failed'

    print(f'  [采集] 共计 {len(all_items)} 条原始条目')
    return all_items, source_status


def get_source_status(config: dict) -> dict:
    """模拟信源状态（实际运行时由采集模块返回）"""
    sources = [
        '36氪', '财联社', '华尔街见闻', '量子位', '机器之心',
        'IEEE Spectrum', 'Nature', 'Science', 'Cell', 'PNAS',
        'MIT TechReview', 'arXiv', 'Fed', 'ECB',
        '国家统计局', '央行', '国务院', '工信部', '证监会',
        '生意社', '创杂志', '海关总署', '上期所',
    ]
    # 简化：默认全部 ok
    return {s: 'ok' for s in sources}


def run_daily_report():
    """
    执行每日报告生成全流程：
    1. 加载配置
    2. 采集数据
    3. 处理管线（去重→分类→提取→验证）
    4. AI分析（概览/新闻分析/寓言）
    5. 模板渲染
    6. 输出HTML
    """
    print("=" * 50)
    print("  推流 · 每日报告生成")
    print("=" * 50)

    # 1. 加载配置
    config = load_config()
    tz_name = config.get('report', {}).get('timezone', 'Asia/Shanghai')
    tz = ZoneInfo(tz_name)
    today_dt = datetime.now(tz)
    today_stamp = today_dt.strftime("%Y-%m-%d")  # 全局唯一的"今日日期"
    print(f"\n[1/5] 配置加载完成 (时区:{tz_name}, 日期:{today_stamp})")

    # 2. 采集数据
    raw_items, collection_status = collect_raw_data(config)
    print(f"[2/5] 数据采集: {len(raw_items)} 条原始条目")
    if not raw_items:
        print("  ⚠ 采集结果为空，生成空报告框架")

    # 2.5 数据新鲜度检查
    stale_count = 0
    for item in raw_items:
        pub = item.get('published', '')
        if pub and pub != today_stamp and pub != datetime.fromtimestamp(0).strftime("%Y-%m-%d"):
            stale_count += 1
    if stale_count > 0:
        stale_pct = stale_count / len(raw_items) * 100 if raw_items else 0
        print(f"  ⚠ 数据新鲜度: {stale_count}/{len(raw_items)} 条非当日数据 ({stale_pct:.0f}%)")

    # 3. 处理管线
    pipeline = ProcessingPipeline()
    result = pipeline.run(raw_items)
    sections = result['sections']
    summary = result['summary']
    print(f"[3/5] 数据处理完成")
    print(f"  去重:{summary['raw_count']}→{summary['deduplicated_count']} "
          f"| 交叉验证率:{summary['verification_rate']}")

    # 4. AI分析
    ai_gen = AIGenerator()

    # 今日概览
    overview = ai_gen.generate_overview(sections)

    # 每条新闻AI分析（实际运行时由WorkBuddy AI填充）
    sections = ai_gen.analyze_all_items(sections)

    # 每日寓言
    allegory = ai_gen.generate_allegory()
    print(f"[4/5] AI内容生成完成")
    print(f"  今日寓言: {allegory['concept']}")

    # 5. 模板渲染
    date_str = today_dt.strftime("%Y年%m月%d日")
    weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
    weekday = weekdays[today_dt.weekday()]
    generation_time = today_dt.strftime("%Y-%m-%d %H:%M:%S")

    source_status = collection_status  # 使用真实采集状态

    template = jinja_env.get_template('base.html')
    html = template.render(
        date_str=date_str,
        weekday=weekday,
        overview=overview,
        sections=sections,
        sections_config=SECTIONS_CONFIG,
        allegory=allegory,
        source_status=source_status,
        generation_time=generation_time,
        total_items=summary['total_items'],
    )
    print(f"[5/5] 报告渲染完成 ({len(html)} 字符)")

    # 5.5 提取AI分析任务（供自动化WorkBuddy AI填充）
    analysis_jobs = extract_analysis_jobs(sections)
    save_jobs(analysis_jobs)
    create_filled_template()

    # 5.6 序列化状态供AI回填步骤使用
    import pickle
    state_path = os.path.join(OUTPUT_DIR, 'latest.pkl')
    with open(state_path, 'wb') as f:
        pickle.dump({
            'sections': sections,
            'allegory': allegory,
            'overview': overview,
            'source_status': source_status,
            'today_stamp': today_stamp,   # 回填时复用同一个日期
        }, f)

    # 6. 输出
    date_dir = today_stamp
    output_dir = os.path.join(OUTPUT_DIR, date_dir)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'index.html')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    # 同时输出到 deploy 目录（供 CloudStudio 部署）
    deploy_dir = os.path.join(OUTPUT_DIR, 'deploy')
    os.makedirs(deploy_dir, exist_ok=True)
    deploy_path = os.path.join(deploy_dir, 'index.html')
    with open(deploy_path, 'w', encoding='utf-8') as f:
        f.write(html)

    # latest.html 方便本地查看
    latest_path = os.path.join(OUTPUT_DIR, 'latest.html')
    with open(latest_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n✅ 报告已生成: {output_path}")
    print(f"   最新版本: {latest_path}")
    print(f"   共 {summary['total_items']} 条资讯 | {len(sections)} 个版块")

    # 7. 部署与推送
    total_items = sum(len(items) for items in sections.values())
    allegory_hint = allegory['concept'] if allegory else ''
    first_line = overview[:100] if overview else ''

    deployer = ReportDeployer()
    deploy_result = deployer.deploy(
        html_path=output_path,
        report_info={
            'title': f"推流 · {date_str} {weekday}",
            'items_count': total_items,
            'summary': first_line,
            'allegory_hint': allegory_hint,
        },
        cloud_url=PUBLIC_URL,
    )
    print(f"[7/7] 部署推送完成: {'✅' if deploy_result.get('pushed') else '⚠️ 跳过'}")

    return output_path


if __name__ == '__main__':
    run_daily_report()
