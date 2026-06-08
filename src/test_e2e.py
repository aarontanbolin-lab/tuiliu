# -*- coding: utf-8 -*-
"""Phase 4 端到端集成测试"""
import sys, io, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from ai_generator import AIGenerator

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = Environment(loader=FileSystemLoader(template_dir), autoescape=select_autoescape(['html']))

SECTIONS_CONFIG = {
    'hot_industries':    {'name': '一、市场最热门行业',    'color': '#C41E3A'},
    'supply_demand':     {'name': '二、供需关系变化',      'color': '#B7950B'},
    'science_tech':      {'name': '三、前沿科学与技术突破',  'color': '#1E8449'},
    'industry_policy':   {'name': '四、行业政策变动',      'color': '#6C3483'},
    'financial_policy':  {'name': '五、金融政策变动',      'color': '#1A5276'},
    'financial_stats':   {'name': '六、金融统计数据变动',   'color': '#1A5276'},
    'pre_ipo':           {'name': '七、准IPO企业追踪',     'color': '#D35400'},
}

from generate_preview import build_sample_data

data = build_sample_data()
sections = data['sections']

ai_gen = AIGenerator()
sections = ai_gen.analyze_all_items(sections)
overview = ai_gen.generate_overview(sections)
allegory = ai_gen.generate_allegory()

now = datetime.now()
html = jinja_env.get_template('base.html').render(
    date_str=now.strftime('%Y年%m月%d日'),
    weekday=['星期一','星期二','星期三','星期四','星期五','星期六','星期日'][now.weekday()],
    overview=overview,
    sections=sections,
    sections_config=SECTIONS_CONFIG,
    allegory=allegory,
    source_status=data['source_status'],
    generation_time=now.strftime('%Y-%m-%d %H:%M:%S'),
)

project_root = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(project_root, '..', 'output')
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, 'e2e_test.html')

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

total = sum(len(items) for items in sections.values())
print(f'✅ E2E test: {output_path}')
print(f'   {len(html)} chars | {total} items | {len(sections)} sections')
print(f'   Allegory: {allegory["concept"]}')
