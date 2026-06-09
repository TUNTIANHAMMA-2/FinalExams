# 系统设计说明

## 1. 总体架构

RhizoDelta 后端采用 Spring Boot 分层架构，核心链路由 REST API、Service、Repository/Neo4jClient、RabbitMQ、Redis、SSE 和监控组件构成。

整体流程：

```text
前端请求
-> Controller 接收和校验
-> Service 执行业务规则
-> Repository / Neo4jClient 持久化图节点和关系
-> RabbitMQ 异步处理耗时任务
-> Redis 保存 token 和短期状态
-> SSE 推送增量事件
-> 前端局部刷新
```

## 2. 技术栈选择

| 技术 | 用途 | 选择原因 |
| --- | --- | --- |
| Spring Boot 3 | 后端应用框架 | 适合构建企业级 Web 服务 |
| Spring Security | 认证授权 | 提供过滤器链和权限控制能力 |
| JWT | 无状态访问令牌 | 适合前后端分离接口访问 |
| Redis | 会话和短期状态 | 支持 token 黑名单、refresh token 和在线状态 |
| Neo4j | 图数据库 | 适合表达节点、边、谱系和溯源关系 |
| RabbitMQ | 消息队列 | 解耦发帖后的异步编排 |
| SSE | 实时推送 | 适合后端向浏览器持续推送事件 |
| Actuator / Prometheus | 监控 | 便于健康检查和指标采集 |

## 3. 分层设计

### 3.1 Controller 层

Controller 负责 HTTP 入口、参数接收和响应封装，例如：

- `AuthController`：认证相关接口。
- `PostController`：接收发帖和回复请求。
- `NodeQueryController`：查询根话题、节点详情、谱系、后代。
- `DecisionController`：合并、分支、注入、物化、回滚。
- `UserProfileController` / `AvatarController`：用户资料和头像。

统一响应使用 `ApiResponse`，避免各接口返回格式不一致。

### 3.2 Service 层

Service 层承载业务规则和事务边界，例如：

- 发帖落库与异步投递。
- 图节点查询和谱系组装。
- 语义关联创建与删除。
- 回滚和 DAG 完整性检查。
- token 刷新、撤销和复用检测。

### 3.3 数据访问层

项目核心数据是图结构，因此使用：

- Spring Data Neo4j Repository。
- `Neo4jClient` 执行参数化 Cypher。
- Neo4j 唯一约束、索引和向量索引。

MyBatis-Plus 的条件查询、分页和逻辑删除要求，在本项目中对应为参数化 Cypher、`PagingParams`、节点 `_deleted` 等属性和 Service 事务。

## 4. 认证授权设计

认证链路：

1. 用户登录时校验账号密码。
2. 使用 BCrypt 校验密码哈希。
3. 生成 access token 和 refresh token。
4. access token 用于后续请求鉴权。
5. refresh token 保存在 Redis 中，用于刷新会话。
6. 退出登录或撤销 token 时写入 Redis 黑名单。

Spring Security 过滤器链统一处理 Bearer token，控制器不重复写鉴权逻辑。

## 5. 异步消息设计

发帖请求可能触发落库、embedding、质量评估、AI 路由和图谱更新等耗时操作。系统使用 RabbitMQ 解耦：

```text
PostController
-> 发布 PostEventMessage
-> RabbitMQ Exchange / Queue
-> PostConsumer
-> Service 执行落库和编排
-> SSE 广播结果
```

设计要点：

- 请求线程快速返回 `202 Accepted`。
- 消费端失败可重试。
- 死信队列保留异常消息。
- 发布确认保证消息没有静默丢失。

## 6. 实时事件设计

SSE 用于向前端推送：

- 节点创建。
- 边创建或删除。
- 决策完成。
- 编排状态。
- 摘要生成。
- 质量评分。

相比轮询，SSE 减少无效请求，也更适合后端异步任务驱动的系统。

## 7. 文件上传设计

头像上传由 `AvatarController` 和 `AvatarStorageService` 处理：

- 接收 `MultipartFile`。
- 校验文件类型、大小和内容。
- 写入 MinIO 或本地存储兜底。
- 更新用户资料中的头像地址。

这对应课程中 MultipartFile 文件处理能力。

## 8. 异常与日志

`GlobalExceptionHandler` 统一处理业务异常和系统异常，把错误转换为一致的 HTTP 响应。日志集中出现在消息队列、SSE、AI 调用、数据库初始化、认证和文件存储等关键链路。

## 9. 部署与运行

项目可通过 Maven 构建后端 JAR，并配合 Docker Compose 启动 Neo4j、RabbitMQ、Redis 等依赖服务。Actuator 和 Prometheus 指标用于运行状态观察。

## 10. 难点与解决策略

| 难点 | 解决策略 |
| --- | --- |
| 图数据查询复杂 | 使用 Neo4j、Cypher 和领域化查询服务 |
| 发帖后链路较长 | RabbitMQ 异步处理，SSE 推送最终状态 |
| 认证状态需要可撤销 | JWT 访问令牌 + Redis 黑名单和 refresh token |
| 课程方案偏 CRUD | 在报告中逐项说明课程要求与真实工程实现的对应关系 |
