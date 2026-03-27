# PLAN.md

`dashboard` 项目计划书。

## 当前目标

把项目收口成一个可部署的统一静态站点，并逐步接入真实数据。

## 当前阶段

### Phase 1：统一静态站点结构
- [x] 建立项目目录
- [x] 建立核心文档
- [x] 完成 dashboard 前端第一版
- [x] 迁移原首页到本项目
- [x] 统一部署目录为 `public/`
- [ ] 校验部署路径映射

### Phase 2：接入真实数据
- [x] 设计 `/api/openai-usage` 返回结构
- [x] 定义 Ubuntu 采集器输出契约
- [x] 明确借鉴 `Codex-Manager` 的账号池监控口径
- [ ] 实现账号池 5h / 7d 真实采集
- [x] 前端拉取真实数据

### Phase 3：稳定化
- [x] 自动发布脚本
- [ ] 状态/错误处理
- [ ] 更新时间显示
- [ ] 阈值状态

## 当前最优先动作

1. [x] 做本地 mock endpoint 或静态 JSON
2. 让 Ubuntu 采集器按契约产出 JSON
3. 用真实 JSON 替换 mock JSON


## 本轮落地

- [x] Dashboard 页面升级为账号池摘要 + 账号列表视图


## 下一步：立即采集触发入口
- [x] 新增本机一键采集脚本 `scripts/run-collector-once.sh`
- [x] 页面预留“立即采集（待接线）”按钮
- [ ] 补真实受控触发入口（HTTP / webhook）
- [ ] 页面按钮直连真实触发入口

- [x] 本机 localhost 立即采集触发器
- [ ] 反向代理 / 公网受控入口
- [ ] 页面“立即采集”按钮直连真实入口

- [x] Pages Functions 代理层（collect-now / collect-status）
- [ ] Cloudflare Pages 环境变量配置
- [ ] 前端真接线后的线上联调

- [x] recent_runs 改为真实 trigger 历史
- [x] 页面显示“本次数据是否变化”

- [x] 账号级 diff 摘要
