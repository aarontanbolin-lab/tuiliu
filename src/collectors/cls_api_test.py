# -*- coding: utf-8 -*-
"""Verify CLS (财联社) API"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import hashlib, time, httpx

base_url = "https://www.cls.cn/nodeapi/telegraphList"
app = "CailianpressWeb"
os = "web"
rn = 5
sv = "7.7.5"
last_time = int(time.time())

# Build signature: SHA1(param_string) -> MD5
param_str = f"app={app}&last_time={last_time}&os={os}&rn={rn}&sv={sv}"
sha1_result = hashlib.sha1(param_str.encode('utf-8')).hexdigest()
sign = hashlib.md5(sha1_result.encode('utf-8')).hexdigest()

url = f"{base_url}?{param_str}&sign={sign}"
print(f"URL: {url[:100]}...")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://www.cls.cn/telegraph',
}

r = httpx.get(url, headers=headers, timeout=15)
print(f"HTTP {r.status_code}")

if r.status_code == 200:
    data = r.json()
    roll_data = data.get('data', {}).get('roll_data', [])
    print(f"OK - Got {len(roll_data)} telegraph items")
    for item in roll_data[:5]:
        title = item.get('title', 'N/A')[:80]
        content = item.get('content', '')[:80]
        level = item.get('level', '?')
        ctime = item.get('ctime', 0)
        ts = time.strftime('%m-%d %H:%M', time.localtime(ctime))
        print(f"  [{level}] {ts} | {title}")
        if content:
            print(f"       {content}")
        print()
else:
    print(f"FAIL: {r.text[:300]}")
