# AI.md

`dashboard` 项目 AI 入口文档。

## 项目目标

将 `Alex Studio` 首页与 ChatGPT Team 额度 dashboard 收口为一个统一前端项目，后续接入 Ubuntu 采集器与本地 API，实现真实额度展示。

## 当前结构

```text
public/
├── index.html
└── dashboard/
    └── index.html
frontend/
├── site-root/
│   └── index.html
└── dashboard/
    └── index.html
```

## 结构说明

- `frontend/`：源页面编辑区
- `public/`：正式部署目录
- 根路径 `/` 对应站点首页
- 路径 `/dashboard/` 对应额度 dashboard

## 接手顺序

1. 看 `AI.md`
2. 看 `PLAN.md`
3. 看 `FEATURES.md`
4. 看 `API.md`
5. 看 `COLLECTOR.md`
6. 再看 `public/` 与 `frontend/`

