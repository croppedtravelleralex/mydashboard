# dashboard

Alex Studio 站点与 ChatGPT Team 额度 dashboard 的统一前端项目。

## 当前状态

- 已收口原 `alexstudio-site` 静态首页
- 已建立 dashboard 静态前端第一版
- 当前项目承担两部分内容：
  - 站点首页
  - `/dashboard` 额度监控页面

## 当前目录

- `frontend/site-root/index.html`：Alex Studio 首页
- `frontend/dashboard/index.html`：Dashboard UI shell v1
- `AI.md`
- `PLAN.md`
- `FEATURES.md`

## 下一步

1. 统一前端目录结构
2. 确定正式部署目录
3. 接入 Ubuntu API 真数据


## 真实数据替换路径

当前站点先使用 `public/api/openai-usage.json` 作为 mock 数据源。
后续 Ubuntu 采集器只需按 `COLLECTOR.md` 约定生成同结构 JSON，并在发布前覆盖该文件即可。


## 自动发布脚本

已提供一键发布脚本：

```bash
export CLOUDFLARE_API_TOKEN='你的token'
bash scripts/deploy-pages.sh
```

脚本行为：
1. 优先读取 `collector/openai-usage.latest.json`
2. 若不存在，则回退到 `collector/openai-usage.latest.sample.json`
3. 覆盖 `public/api/openai-usage.json`
4. 执行 `wrangler pages deploy public --project-name alexstudio-web`
