# -*- coding: utf-8 -*-
"""
推流 — GitHub Pages 自动部署
将 output/deploy/index.html 推送到 gh-pages 分支
"""
import os, subprocess, shutil, sys
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEPLOY_SRC = os.path.join(PROJECT_ROOT, 'output', 'deploy', 'index.html')
GH_PAGES_DIR = os.path.join(PROJECT_ROOT, '.gh-pages-deploy')


def run(cmd, cwd=None):
    """执行shell命令"""
    result = subprocess.run(cmd, shell=True, cwd=cwd or PROJECT_ROOT,
                          capture_output=True, text=True)
    if result.returncode != 0 and result.stderr:
        print(f'  ⚠ {result.stderr.strip()[:200]}')
    return result


def deploy():
    """执行 GitHub Pages 部署"""
    print('=' * 50)
    print('  推流 · GitHub Pages 部署')
    print('=' * 50)

    # 1. 检查源文件
    if not os.path.exists(DEPLOY_SRC):
        print(f'❌ 部署源文件不存在: {DEPLOY_SRC}')
        print('   请先运行 main.py 生成报告')
        return False

    print(f'\n[1/4] 源文件: {DEPLOY_SRC} ({os.path.getsize(DEPLOY_SRC)} bytes)')

    # 2. 准备 gh-pages 目录
    if os.path.exists(GH_PAGES_DIR):
        shutil.rmtree(GH_PAGES_DIR)

    # 克隆 gh-pages 分支（或创建新的 orphan 分支）
    print(f'[2/4] 准备 gh-pages 分支...')

    # 尝试克隆现有 gh-pages
    clone_result = run('git clone -b gh-pages --single-branch . .gh-pages-deploy 2>&1')

    if clone_result.returncode != 0:
        # gh-pages 不存在，创建 orphan 分支
        print('  gh-pages 分支不存在，创建中...')
        run('git checkout --orphan gh-pages')
        run('git rm -rf --cached .')
        run('git clean -fdx')
        # 创建空提交
        run('git commit --allow-empty -m "init gh-pages"')
        run('git checkout main')
        # 重新克隆
        if os.path.exists(GH_PAGES_DIR):
            shutil.rmtree(GH_PAGES_DIR)
        run('git clone -b gh-pages --single-branch . .gh-pages-deploy')

    # 3. 复制 HTML 到 gh-pages 目录
    print(f'[3/4] 复制报告文件...')

    # 按日期归档
    today = datetime.now().strftime('%Y-%m-%d')
    archive_dir = os.path.join(GH_PAGES_DIR, 'archive', today)
    os.makedirs(archive_dir, exist_ok=True)
    shutil.copy2(DEPLOY_SRC, os.path.join(archive_dir, 'index.html'))

    # 最新版本作为根目录 index.html
    shutil.copy2(DEPLOY_SRC, os.path.join(GH_PAGES_DIR, 'index.html'))

    # 写入 CNAME（如有自定义域名）和 .nojekyll
    with open(os.path.join(GH_PAGES_DIR, '.nojekyll'), 'w') as f:
        f.write('')

    # 4. 提交并推送
    print(f'[4/4] 提交并推送...')

    cwd = GH_PAGES_DIR
    run('git add -A', cwd=cwd)
    run(f'git commit -m "deploy: {today}" --allow-empty', cwd=cwd)
    push_result = run('git push origin gh-pages', cwd=cwd)

    # 清理
    shutil.rmtree(GH_PAGES_DIR, ignore_errors=True)

    # 切回 main
    run('git checkout main')

    if push_result.returncode == 0:
        print(f'\n✅ 部署成功!')
        print(f'   https://aarontanbolin-lab.github.io/tuiliu/')
        print(f'   历史归档: https://aarontanbolin-lab.github.io/tuiliu/archive/{today}/')
        return True
    else:
        print(f'\n❌ 推送失败，请检查 GitHub 认证')
        print(f'   可能需要设置: git remote set-url origin git@github.com:aarontanbolin-lab/tuiliu.git')
        return False


if __name__ == '__main__':
    success = deploy()
    sys.exit(0 if success else 1)
