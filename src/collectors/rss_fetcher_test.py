# -*- coding: utf-8 -*-
"""Phase 1.13-1.14: arXiv API + scraper feasibility test"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import httpx, feedparser

print("=== 1.13 arXiv API ===")
try:
    url = "https://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&sortOrder=descending&max_results=3"
    r = httpx.get(url, timeout=15)
    f = feedparser.parse(r.text)
    print(f"OK: {len(f.entries)} entries")
    for e in f.entries[:2]:
        print(f"  {e.title[:80]}")
        print(f"  {e.id}")
except Exception as e:
    print(f"FAIL: {e}")

print()

# Quick scraper feasibility for key sites
print("=== 1.14 爬虫源连通性检查 ===")
scrapers = [
    ("国家统计局", "https://www.stats.gov.cn/sj/zxfb/"),
    ("央行货币政策", "https://www.pbc.gov.cn/zhengcehuobisi/125207/125213/"),
    ("国务院政策", "https://www.gov.cn/zhengce/zuixin.htm"),
    ("证监会IPO", "https://www.csrc.gov.cn/csrc/c100028/common_list.shtml"),
    ("生意社", "https://www.100ppi.com/"),
    ("创杂志", "https://www.qstheory.cn/"),
    ("上海期货交易所", "https://www.shfe.com.cn/"),
    ("大连商品交易所", "https://www.dce.com.cn/"),
    ("郑州商品交易所", "https://www.czce.com.cn/"),
    ("海关总署", "https://www.customs.gov.cn/"),
    ("国家外汇管理局", "https://www.safe.gov.cn/"),
    ("银保监会", "https://www.nfra.gov.cn/"),
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

for label, url in scrapers:
    try:
        r = httpx.get(url, timeout=15, headers=headers, follow_redirects=True)
        status = "OK" if r.status_code == 200 else f"HTTP {r.status_code}"
        length = len(r.text)
        has_links = r.text.count('href=')
        print(f"[{status}] {label}: {length} chars, ~{has_links} links")
    except Exception as e:
        print(f"[FAIL] {label}: {str(e)[:60]}")
