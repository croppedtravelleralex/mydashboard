# API.md

`dashboard` 项目接口草案。

## 目标接口

- **`GET /api/openai-usage`**

该接口用于给 `/dashboard/` 页面提供 OpenAI / ChatGPT Team 额度展示数据。

## 返回结构（V1 草案）

```json
{
  "ok": true,
  "source": "ubuntu-collector",
  "generated_at": "2026-03-27T20:20:00+08:00",
  "quota": {
    "window_5h": {
      "remaining_percent": 68.4,
      "used_percent": 31.6,
      "status": "healthy"
    },
    "window_7d": {
      "remaining_percent": 74.1,
      "used_percent": 25.9,
      "status": "healthy"
    }
  },
  "collector": {
    "status": "ok",
    "message": "collector finished successfully",
    "last_run_at": "2026-03-27T20:18:43+08:00"
  },
  "recent_runs": [
    {
      "id": "collector-run-001",
      "status": "success",
      "finished_at": "2026-03-27T20:18:43+08:00"
    },
    {
      "id": "collector-run-002",
      "status": "success",
      "finished_at": "2026-03-27T20:03:12+08:00"
    }
  ],
  "errors": []
}
```

## 字段说明

### 顶层
- `ok`：接口是否成功
- `source`：数据来源，当前预期为 `ubuntu-collector`
- `generated_at`：接口生成时间

### quota.window_5h / quota.window_7d
- `remaining_percent`：剩余额度百分比
- `used_percent`：已使用额度百分比
- `status`：额度状态
  - `healthy`
  - `warning`
  - `danger`

### collector
- `status`：采集器状态
  - `ok`
  - `warning`
  - `error`
- `message`：采集器状态说明
- `last_run_at`：最近成功或最近一次执行时间

### recent_runs
- 最近几次采集任务简表，供前端直接展示

### errors
- 接口级错误列表
- 正常情况下为空数组

## 前端使用规则

- `/dashboard/` 首屏直接请求 `GET /api/openai-usage`
- 若 `ok=false`：
  - 页面显示错误态
  - 仍展示最近更新时间与错误信息
- 若 `collector.status=warning|error`：
  - 页面顶部状态组件显示告警

## V1 决策

- V1 先只做 **只读接口**，不做写操作
- V1 先只支持 **单账号视图**
- V1 先只覆盖：
  - `5h` 额度
  - `7d` 额度
  - 采集器状态
  - 最近采集记录
- 复杂趋势图和多账号留到后续阶段

