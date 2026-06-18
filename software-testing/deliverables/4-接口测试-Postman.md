# 4 接口测试 · Postman（RhizoDelta）

> 专项工具三选一：**Postman**（接口测试）。对应模板 `templates/4、接口 性能 自动化.txt`。
> 集合与环境由 `scripts/build_postman_collection.py` 生成，已用 **newman** 对运行中实例实跑并导出报告。

## 1 产物

| 文件 | 说明 |
| --- | --- |
| `postman/RhizoDelta.postman_collection.json` | 20 条接口用例，含 Tests 断言（v2.1） |
| `postman/RhizoDelta.local.postman_environment.json` | 环境：`baseUrl=http://localhost:8090` |
| `../generated/postman-report.html` | newman htmlextra 可视化报告 |
| `../generated/postman-run.json` | newman 原始运行数据 |

## 2 运行方式（可复现）

```bash
cd software-testing
python3 scripts/build_postman_collection.py        # 生成集合+环境
npx --yes -p newman -p newman-reporter-htmlextra newman run \
  deliverables/postman/RhizoDelta.postman_collection.json \
  -e deliverables/postman/RhizoDelta.local.postman_environment.json \
  -r cli,json,htmlextra \
  --reporter-json-export generated/postman-run.json \
  --reporter-htmlextra-export generated/postman-report.html
```

> 前提：RhizoDelta 后端运行在 `http://localhost:8090`，且 Neo4j/Redis/RabbitMQ 依赖就绪。集合在注册请求的 pre-request 脚本里用 `qa_+Date.now()` 生成唯一用户名，可重复运行不冲突。

## 3 运行结果（2026-06-18 实测）

| 指标 | 值 |
| --- | --- |
| 请求 | 20 / 失败 0 |
| 断言 | 58 / 通过 57 / 失败 1 |
| 总耗时 | ~1.2s，平均响应 42ms |
| 唯一失败 | 用例 `1.2 注册-重复用户名` 的"期望 409"断言 → 对应 **BUG-001**（重复注册应 409 实返 400） |

> 该失败是**有意为之**的契约断言，用于在报告中坐实 BUG-001；其余 57 条断言全部通过，说明认证、用户资料、图谱查询的核心接口行为正确。

## 4 约定（实测确认）

- 鉴权：`POST /api/auth/login` 取 `data.token`，后续请求头 `Authorization: Bearer {{token}}`；集合在登录/注册/刷新的 Tests 中自动写入环境变量 `token`/`refreshToken`。
- 字段命名：请求与响应均 **snake_case**——注册体 `{username,password,display_name}`，刷新体 `{refresh_token}`，响应 `data.refresh_token`/`data.user.user_id`。
- 响应包：`{code,message,data}`；断言同时校验 HTTP 状态码与业务 `code`。

## 5 覆盖的接口（20 用例）

| 模块 | 用例 |
| --- | --- |
| 认证授权 | 注册（合法/重复/短密码/空用户名）、登录（正确/密码错/不存在用户）、/me（带token/无token/伪造token）、刷新 |
| 用户资料与社交 | 个人资料（带token/无token）、在线状态、动态流 |
| 图谱查询 | 根话题、非法 UUID 格式、合法但不存在节点 |
| 认证收尾 | 登出、登出后复用旧 token 被吊销 |

接口用例与功能用例的逐条输入/预期/实际见 [2-测试用例.md](./2-测试用例.md)。

## 6 待扩展

- 发帖 `POST /api/posts`（异步入队 → 轮询 feed 验证最终一致）。
- 头像上传 `PUT /api/users/me/avatar`（multipart，类型/大小校验）。
- 治理决策 `/api/decisions/*` 与复核 `/api/reviews/*` 主流程。
- SSE `/api/events/stream` 连通性冒烟。
