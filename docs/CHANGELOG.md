# 推流 — 版本日志

## v1.0 (2026-06-08) — MVP 首发

### 发布链接
- 公网日报：https://aarontanbolin-lab.github.io/tuiliu/
- GitHub：https://github.com/aarontanbolin-lab/tuiliu
- 飞书推送：已配置，每日 8:00
- 自动化ID：automation-1780905286297（每日 7:00 触发）

### 功能清单

#### 信息版块（8个）
1. 市场最热门行业
2. 供需关系变化
3. 前沿科学与技术突破
4. 行业政策变动
5. 金融政策变动
6. 金融统计数据变动
7. 准IPO企业追踪（A股+港股）
8. 每日寓言（研究生层级概念）

#### 信息源（28个初检，21个可用）
- RSS源：36氪、量子位、IEEE Spectrum、Nature、Science、Cell、PNAS、MIT TechReview、Fed Press
- API源：arXiv、财联社（SHA1-MD5签名）、FRED
- 爬虫源：国务院、统计局、证监会、创杂志等（6个JS渲染源待攻克）
- 用户指定：生意社、求是杂志

#### 技术架构
- Python 3.13 + Jinja2 + feedparser + httpx + BeautifulSoup4
- 数据处理管线：去重引擎 → 版块分类器 → 关键信息提取 → 交叉验证
- 响应式HTML模板：移动端优先，出版物级排版

#### AI能力
- 新闻AI分析：每条新闻附带背景意义/产业链机会/后续影响三栏分析
- 每日寓言：6个研究生概念库（奈奎斯特采样定理/SGD/马尔可夫毯/涌现/香农熵/囚徒困境博弈论）
- 自动概览生成

#### 部署推送
- GitHub Pages 公网部署，固定URL
- 飞书自定义机器人富文本消息推送
- WorkBuddy 每日 7:00 自动化定时触发

### 已知限制
- 数据采集使用测试数据（待替换为真实信源采集）
- AI分析使用占位符（待接入WorkBuddy AI实时生成）
- 6个JS动态渲染信源待Playwright攻克
- ECB、央行（403反爬）暂不纳入

### 变更锁定
- 此版本为推流唯一基准版本
- 任何对 v1.0 的修改须取得用户明确同意
- 后续所有迭代基于此版本进行
