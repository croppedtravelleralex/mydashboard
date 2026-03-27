# API.md

`dashboard` 项目接口草案。

## 目标接口

- **`GET /api/openai-usage`**

该接口用于给 `/dashboard/` 页面提供 ChatGPT / OpenAI 账号池的 **5h / 7d 可用额度监控** 数据。

## 借鉴范围说明

本项目参考 `qxcnm/Codex-Manager` 的仅限于：
- 账号池监控视角
- 5 小时额度
- 7 天周期额度
- 剩余百分比 / 已使用百分比
- 重置时间

**不照搬**：
- 其完整账户管理系统
- 聚合 API / Key 管理
- 复杂后台与服务治理逻辑

## 返回结构（V2：账号池监控版）

```json
{
  "ok": true,
  "source": "ubuntu-collector",
  "generated_at": "2026-03-27T20:20:00+08:00",
  "summary": {
    "account_count": 3,
    "available_count": 2,
    "warning_count": 1,
    "danger_count": 0,
    "avg_5h_remaining_percent": 68.4,
    "avg_7d_remaining_percent": 74.1
  },
  "accounts": [
    {
      "id": "account-001",
      "name": "team-account-a",
      "status": "ok",
      "captured_at": "2026-03-27T20:18:43+08:00",
      "quota": {
        "window_5h": {
          "remaining_percent": 68.4,
          "used_percent": 31.6,
          "resets_at": "2026-03-27T23:40:00+08:00",
          "status": "healthy"
        },
        "window_7d": {
          "remaining_percent": 74.1,
          "used_percent": 25.9,
          "resets_at": "2026-03-30T00:00:00+08:00",
          "status": "healthy"
        }
      },
      "collector": {
        "status": "ok",
        "message": "collector finished successfully"
      }
    }
  ],
  "recent_runs": [
    {
      "id": "collector-run-001",
      "status": "success",
      "finished_at": "2026-03-27T20:18:43+08:00"
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

### summary
- `account_count`：账号总数
- `available_count`：当前可用账号数
- `warning_count`：额度告警账号数
- `danger_count`：危险账号数
- `avg_5h_remaining_percent`：账号池 5h 平均剩余额度
- `avg_7d_remaining_percent`：账号池 7d 平均剩余额度

### accounts[]
每个账号一条记录，V2 重点字段：
- `id`
- `name`
- `status`：`ok | warning | danger | unavailable`
- `captured_at`

### accounts[].quota.window_5h / window_7d
- `remaining_percent`：剩余额度百分比
- `used_percent`：已使用百分比
- `resets_at`：重置时间
- `status`：`healthy | warning | danger`

### accounts[].collector
- `status`：`ok | warning | error`
- `message`：采集说明

### recent_runs
- 最近几次采集任务简表，供前端直接展示

### errors
- 接口级错误列表
- 正常情况下为空数组

## 前端使用规则

### V1（当前页）
当前 `/dashboard/` 页面先展示：
- 整体摘要
- 默认主账号 / 主视图的 5h 与 7d 额度
- 最近采集记录

### V2（下一步）
页面扩展为账号池监控：
- 账号列表
- 每个账号 5h 剩余额度
- 每个账号 7d 剩余额度
- 重置时间
- 当前状态颜色

## V2 决策

- 以**账号池监控**为核心，而不是单账号静态展示
- 保留当前静态 JSON / mock JSON / 真接口三层兼容结构
- Ubuntu 采集器最终只要产出该 JSON 结构，前端即可接入


## 立即采集入口（待接线）
- 当前页面只支持“刷新显示”，不会直接触发重新采集。
- 已新增本机一键采集脚本：`scripts/run-collector-once.sh`。
- 下一步需要为该脚本补一个受控 HTTP / webhook 触发入口，再由页面调用。


## Collector Trigger API
- `GET http://127.0.0.1:18765/health`
- `GET http://127.0.0.1:18765/status`
- `POST http://127.0.0.1:18765/collect-now`
- 鉴权：`Authorization: Bearer <token>` 或 `X-Collect-Token: <token>`
- 当前仅监听 `127.0.0.1`，默认不对公网开放。

## Pages Functions 代理
- `POST /api/collect-now`：由 Pages Functions 代理到 trigger 的 `/collect-now`
- `GET /api/collect-status`：由 Pages Functions 代理到 trigger 的 `/status`
- Cloudflare 侧需要配置环境变量：`COLLECT_TRIGGER_URL`、`COLLECT_TRIGGER_TOKEN`、`DASHBOARD_ALLOWED_ORIGIN`。

- `change_summary`：本次汇总相对上次发布结果是否有变化，以及差异字段。
- `recent_runs`：读取 `logs/collector-trigger-runs.json` 的真实采集历史。

- `account_change_summary`：账号级变化摘要，展示哪些账号的额度/状态/重置时间发生变化。
