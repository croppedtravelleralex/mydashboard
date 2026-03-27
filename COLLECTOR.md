# COLLECTOR.md

`dashboard` 项目中 Ubuntu 采集器与前端/Pages 对接说明。

## 核心目标

本项目的真实目标不是简单显示一个总额度，而是做 **ChatGPT / OpenAI 账号池的 5h / 7d 可用额度监控**。

参考来源：`qxcnm/Codex-Manager`
但只借鉴：
- 账号池监控视角
- 5h 与 7d 两个额度窗口
- 剩余百分比 / 已使用百分比 / 重置时间

## 当前替换路径

### 方案 A：直接覆盖静态 JSON（V1 最简单）
采集器输出：
- `collector/openai-usage.latest.json`

发布前同步到：
- `public/api/openai-usage.json`

### 方案 B：后续接真实后端接口
后端接口：
- `GET /api/openai-usage`

返回结构保持与静态 JSON 一致。

## Ubuntu 采集器输出契约（账号池版）

输出文件必须为 UTF-8 JSON，字段结构兼容 `API.md`。

### 最低要求

采集器至少应输出：
1. 账号总数
2. 可用账号数
3. 每个账号的 5h 剩余额度
4. 每个账号的 7d 剩余额度
5. 两个窗口的重置时间
6. 采集时间
7. 最近采集记录

## 单账号字段契约

```json
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
```

## V1 最小落地建议

1. 先让采集器输出账号池 JSON 到：`collector/openai-usage.latest.json`
2. 发布前脚本复制到：`public/api/openai-usage.json`
3. 执行：`bash scripts/deploy-pages.sh`

## 当前主线判断

最应该优先做的不是复杂后端，而是：
- **先把账号池 5h / 7d 额度采集出来**
- **按约定 JSON 落盘**
- **直接替换当前 mock JSON**

这样能最快把“演示版 dashboard”推进到“真实监控 dashboard”。

## 当前已落地脚手架

- `collector/generate_usage_json.py`

当前该脚本先生成 **账号池监控 JSON 雏形**，后续只需要把账号采集逻辑替换进去即可。

### 当前运行方式

```bash
python3 collector/generate_usage_json.py
```

### 当前输出

```bash
collector/openai-usage.latest.json
```

## Snapshot 解析输入（当前已支持）

当前采集器已支持解析与 `Codex-Manager` 同口径的原始 snapshot 结构，例如：

```json
{
  "rate_limit": {
    "primary_window": {
      "used_percent": 31.6,
      "window_minutes": 300,
      "resets_at": 1774627200
    },
    "secondary_window": {
      "used_percent": 25.9,
      "window_minutes": 10080,
      "resets_at": 1774886400
    }
  }
}
```

当前测试样例文件：
- `collector/sample_usage_snapshot.json`

后续只要把真实抓取结果落成这个结构，采集器就能自动产出 `collector/openai-usage.latest.json`。
