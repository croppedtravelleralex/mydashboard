# FEATURES.md

`dashboard` 项目目标功能清单。

## 站点首页
- 展示 Alex Studio 品牌首页
- 作为统一入口页
- 后续可扩展为产品主页 / 项目入口页

## Dashboard 页面
- 展示 5h 额度
- 展示 7d 额度
- 展示抓取状态
- 展示最近更新时间
- 展示错误信息

## 数据接入
- 接入 Ubuntu 采集器输出
- 接入本地只读 API
- 前端自动刷新数据

## 后续扩展
- 历史趋势图
- 阈值提醒
- 多账号支持
- 统一控制台能力


## API 接口（V1）
- `GET /api/openai-usage`
- 返回 5h / 7d 额度
- 返回采集器状态
- 返回最近采集记录
- 返回错误信息数组

## 采集器对接（V1）
- Ubuntu 采集器输出标准 JSON
- 直接替换 `public/api/openai-usage.json`
- 前端无需重写即可切换到真实数据
