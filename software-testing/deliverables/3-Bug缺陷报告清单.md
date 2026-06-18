# 3 Bug 缺陷报告清单（RhizoDelta）

> 对应模板 `templates/3Bug缺陷报告清单.xls`。缺陷均来自对 `http://localhost:8090` 的实测（2026-06-18），可复现。

## 一、缺陷分布统计（按模块 × 严重程度，单位：个）

| 模块 | 严重 | 很高 | 高 | 中 | 低 | 合计 |
| --- | --- | --- | --- | --- | --- | --- |
| 认证授权 | 0 | 0 | 0 | 0 | 1 | 1 |
| 用户资料与社交 | 0 | 0 | 0 | 0 | 1 | 1 |
| 发帖与关联 | 0 | 0 | 0 | 0 | 0 | 0 |
| 图谱查询 | 0 | 0 | 0 | 0 | 0 | 0 |
| **合计** | 0 | 0 | 0 | 0 | **2** | **2** |

> 本轮聚焦认证、用户资料、图谱查询的接口契约测试；功能行为均正确，发现 2 个 HTTP 契约/数据一致性级别的低危缺陷。

## 二、缺陷明细

### BUG-001 重复用户名注册返回 400，HTTP 语义应为 409 Conflict

| 项 | 内容 |
| --- | --- |
| 模块 | 认证授权 |
| 接口 | `POST /api/auth/register` |
| 严重程度 | 低 |
| 提交人 | 本人 |

**描述**：注册一个已存在的用户名时，服务端正确拒绝并返回业务码 `40001`、消息 `username already exists`，但 HTTP 状态码为 **400 Bad Request**。按 REST 语义，资源冲突应返回 **409 Conflict**；且代码 `ApiResponse` 已定义 `CONFLICT_CODE=40901` 却未在此场景使用。

**复现步骤**（环境：localhost:8090，Chrome/curl）：
1. `POST /api/auth/register` 用 `{"username":"qa_tester_st","password":"Test@****"}` 注册成功。
2. 再次用**相同 username** 调 `POST /api/auth/register`。
3. 观察响应。

**实际**：`HTTP 400`，`{"code":40001,"message":"username already exists","data":null}`
**预期**：`HTTP 409`，业务码 `40901`
**证据**：Postman 用例 `1.2 注册-重复用户名` 断言 `[缺陷观察] 期望 409` 失败（`expected 400 to deeply equal 409`），见 `../generated/postman-report.html`。
**建议**：重复注册场景改用 `ApiResponse.conflict(...)`（409/40901），与既有错误码体系保持一致。

### BUG-002 在线状态接口 `last_active` 为字符串型 epoch，与其它时间字段格式不一致

| 项 | 内容 |
| --- | --- |
| 模块 | 用户资料与社交 |
| 接口 | `GET /api/users/me/status` |
| 严重程度 | 低 |
| 提交人 | 本人 |

**描述**：`/api/users/me/status` 返回 `"last_active":"1781751037890"`（字符串型毫秒时间戳），而 `/api/users/me/profile` 的 `updated_at` 为 ISO8601 字符串 `"2026-06-18T02:49:22.075Z"`。同一系统内时间字段表示不统一，前端解析需特殊处理，易出错。

**复现步骤**：
1. 登录后 `GET /api/users/me/status`（带 Bearer token）。
2. 查看 `data.last_active` 字段类型与格式。

**实际**：`"last_active":"1781751037890"`（字符串、epoch 毫秒）
**预期**：统一为 ISO8601 字符串，或明确为数值型毫秒时间戳并在文档说明
**建议**：与 `updated_at` 等字段对齐为 ISO8601，或全局统一时间序列化策略。

## 三、严重程度判定标准

| 级别 | 含义 |
| --- | --- |
| 严重 | 阻塞主流程 / 数据错误 / 崩溃，无规避 |
| 很高 | 核心功能不可用，影响范围大 |
| 高 | 重要功能错误，但有规避 |
| 中 | 一般功能问题，体验受影响 |
| 低 | HTTP 语义/数据格式/文案等轻微问题，不影响主功能 |
