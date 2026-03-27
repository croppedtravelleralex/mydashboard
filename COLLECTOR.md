# COLLECTOR.md

`dashboard` 项目中 Ubuntu 采集器与前端/Pages 对接说明。

## 核心策略

当前 Cloudflare Pages 项目先使用静态文件：

- `public/api/openai-usage.json`

后续真实接入时，Ubuntu 采集器只需要持续产出**同结构 JSON**，就能直接替换当前 mock 数据源，无需大改前端。

## 当前替换路径

### 方案 A：直接覆盖静态 JSON（V1 最简单）
采集器输出：
- `collector/openai-usage.latest.json`

发布前同步到：
- `public/api/openai-usage.json`

这样 Pages 继续走静态部署，但页面读到的是准实时采集结果。

### 方案 B：后续接真实后端接口
后端接口：
- `GET /api/openai-usage`

返回结构保持与静态 JSON 一致。

## Ubuntu 采集器输出契约

输出文件必须为 UTF-8 JSON，字段结构必须兼容：

```json
{
  "ok": true,
  "source": "ubuntu-collector",
  "generated_at": "2026-03-27T20:30:00+08:00",
  "quota": {
    "window_5h": {
      "remaining_percent": 72.8,
      "used_percent": 27.2,
      "status": "healthy"
    },
    "window_7d": {
      "remaining_percent": 66.5,
      "used_percent": 33.5,
      "status": "healthy"
    }
  },
  "collector": {
    "status": "ok",
    "message": "collector finished successfully",
    "last_run_at": "2026-03-27T20:28:43+08:00"
  },
  "recent_runs": [
    {
      "id": "collector-run-001",
      "status": "success",
      "finished_at": "2026-03-27T20:28:43+08:00"
    }
  ],
  "errors": []
}
```

## 字段约束

### 顶层
- `ok`: 布尔值
- `source`: 建议固定为 `ubuntu-collector`
- `generated_at`: ISO 8601 时间字符串

### quota.window_5h / quota.window_7d
- `remaining_percent`: 数值，0-100
- `used_percent`: 数值，0-100
- `status`: `healthy | warning | danger`

### collector
- `status`: `ok | warning | error`
- `message`: 字符串
- `last_run_at`: ISO 8601 时间字符串

### recent_runs
- 最多保留最近 3-10 条即可
- 每项字段：
  - `id`
  - `status`
  - `finished_at`

### errors
- 正常时为空数组
- 错误时可放字符串数组或错误对象数组，V1 先建议字符串数组

## V1 最小落地建议

1. Ubuntu 采集器生成：`collector/openai-usage.latest.json`
2. 发布前脚本复制到：`public/api/openai-usage.json`
3. 执行 `wrangler pages deploy public --project-name alexstudio-web`

## 结果

这样真实接入后：
- 前端代码无需重写
- Pages 结构无需重做
- mock JSON 可以直接被真实 JSON 替换

