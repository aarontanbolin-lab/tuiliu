# 推流 v2.0 TODO

## 第1步：信源重构 [x]
- [x] collector.py: 移除6个英文学术源（Nature/Science/PNAS/arXiv/IEEE/MIT）
- [x] collector.py: 新增中文信源（新华网财经/证券时报/第一财经/部委公告）
- [x] collector.py: Federal Reserve 保留但标记为需翻译
- [x] 验证新信源可采集

## 第2步：版块重构 [x]
- [x] main.py: 更新 SECTIONS_CONFIG 为6个新版块
- [x] classifier.py: 更新版块定义和关键词规则
- [x] extractor.py: 更新IPO版块增加打新信息提取
- [x] 验证分类逻辑

## 第3步：编辑精选流程 [x]
- [x] 新增 editor.py: 编辑筛选+导读生成
- [x] pipeline.py: 集成编辑筛选（采集中文源 → 去重 → 筛选 → 分类）
- [x] 总条数控制30-50条

## 第4步：模板+排版重构 [x]
- [x] base.html: 全新布局（封面故事+版块导读+精简条目）
- [x] style.css: 杂志风格排版
- [x] 添加"编辑按语"字段
- [x] 验证渲染效果

## 第5步：自动化任务更新 [x]
- [x] 更新自动化 prompt 适配 v2.0 流程
- [x] 确保 SSH push 免交互

## 第6步：测试+部署 [x]
- [x] 完整试运行
- [x] 验证打新数据
- [x] 部署到 GitHub Pages
