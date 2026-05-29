# 《JavaEE企业级Web应用开发实战》期末课程设计报告

项目名称：RhizoDelta 图谱化非线性讨论系统

代码仓库：https://github.com/TUNTIANHAMMA-2/RhizoDelta

本地开发目录：`/home/tthm/workspace/RhizoDelta`

## 一、项目概述

RhizoDelta 是一个基于图谱的非线性讨论系统。它把传统论坛中的线性聊天记录组织为“共识主干 + 异议分支”的知识图谱：用户提交观点后，后端通过 Spring Boot 接收请求，RabbitMQ 解耦异步处理，Neo4j 保存不可变 DAG，AI 编排层对内容进行召回、裁决、反思和落库，前端通过 SSE 接收增量事件并刷新图谱视图。

## 二、需求分析

- 用户可以注册、登录，并通过 JWT 访问受保护接口。
- 用户可以发布新话题或回复已有节点，系统返回 `202 Accepted`，后台异步写入图谱。
- 系统需要支持节点详情、谱系 lineage、后代 children、溯源 provenance、移动端 discussion-tree 等查询。
- 管理或 Agent 角色可以执行合并、分支、注入、物化、回滚、语义关联等治理操作。
- 系统需要保证历史节点不可变，所有演进通过新增节点和关系边表达。
- 后端需要提供 SSE，让前端实时接收节点创建、边创建、决策完成、质量评分等事件。

## 三、技术选型与开发环境

| 层次 | 技术 |
|---|---|
| 后端语言与框架 | Java 17, Spring Boot 3.2.3 |
| 数据访问 | Spring Data Neo4j, Neo4jClient |
| 数据库 | Neo4j 5.22 |
| 消息队列 | RabbitMQ 3-management |
| 缓存/复核 | Redis 7 |
| 鉴权 | Spring Security, JWT, BCrypt |
| AI 编排 | LangChain4j 0.36.2, LangGraph4j 1.8.10 |
| 监控 | Spring Boot Actuator, Micrometer, Prometheus, Grafana |
| 构建 | Maven |

## 四、系统总体设计

![全栈架构](images/01_fullstack_architecture.png)

系统采用分层架构：`api` 层负责 HTTP 输入输出，`service` 层承载业务规则，`repository` 和 `Neo4jClient` 承担图数据库访问，`infrastructure` 包统一放置安全、消息、SSE、持久化初始化和可观测性能力。

## 五、数据模型与图数据库设计

![图数据模型](images/02_graph_data_model.png)

核心节点包括 `Human_Post`、`AI_Consensus`、`Result`、`UserAccount`、`UserProfile`、`Topic` 和 `PreferenceEvent`。版本演进关系包括 `BRANCHED_FROM`、`MERGED_INTO`、`SYNTHESIZED_FROM`、`CONTINUES_FROM`、`CONVERGED_FROM`、`MATERIALIZED_FROM`、`CROSS_SYNTHESIZED_FROM`。语义关联关系包括 `CONCEPTUAL_OVERLAP` 和 `RELATES_TO`。用户域关系包括 `AUTHORED`、`HAS_PROFILE`、`FOLLOWS`、`MUTED`、`PREFERS`。

## 六、后端功能实现

### 6.1 认证与权限

`SecurityConfig` 关闭 CSRF，使用无状态会话，并把 `JwtAuthenticationFilter` 放入 Spring Security 过滤链。公开接口包括登录、注册、刷新 token、健康检查和头像读取；写入决策、创建语义关联、复核和回滚接口按 `USER`、`AGENT`、`ADMIN` 角色区分权限。

### 6.2 发帖异步处理

`PostController` 负责校验请求、绑定认证用户、检查目标节点、生成稳定 `event_id`，再把 `PostEventMessage` 投递到 RabbitMQ。HTTP 层等待 publisher confirm，消息确认后返回 `202 Accepted`。`PostConsumer` 消费消息后创建 `Human_Post`，异步生成 embedding、质量评分，发布 `NODE_CREATED` 和 `EDGE_CREATED` 事件，并触发 AI 路由编排。

![后端时序](images/04_backend_async_flow.png)

### 6.3 图谱查询

`NodeQueryController` 提供只读查询：根话题、节点详情、`lineage`、`children`、`topology-context`、`discussion-tree`、`provenance` 和 `associations`。这些接口把图数据库中的节点和关系转换为前端可直接渲染的 DTO。

### 6.4 AI 编排与治理

`AiRoutingWorkflowService` 使用 LangGraph4j 定义状态图：加载帖子、确保 embedding、向量召回、上下文裁剪、规则预过滤、LLM 裁决、反思校验、提交前守卫、执行合并/分支或创建复核任务。规则层可以在高相似或低相似场景跳过 LLM，从而降低延迟和成本。

### 6.5 实时推送

`EventController` 暴露 `/api/events/stream`，通过 `SseEventService` 为当前用户注册 `SseEmitter`。后端在发帖排队、节点创建、边创建、决策完成、摘要生成和质量评分时发布事件，前端据此做增量刷新。

## 七、部署与运行

本地运行需要 JDK 17、Maven、Node.js、npm、Docker Compose 和可用的 `DASHSCOPE_API_KEY`。核心命令：

```bash
docker compose up -d neo4j rabbitmq redis
export DASHSCOPE_API_KEY=your_api_key_here
mvn spring-boot:run
cd frontend && npm install && npm run dev
```

后端默认端口为 `8090`，前端开发端口为 `5173`，Vite 会把 `/api` 代理到 `http://localhost:8090`。

## 八、测试与质量保障

后端测试使用 JUnit 5、Spring Boot Test 和 Testcontainers。当前仓库包含 92 个 Java 测试文件，覆盖认证、发帖、决策、图查询、SSE、用户画像、偏好聚合、AI 路由、数据库初始化等模块。常用验证命令：

```bash
mvn test -Dspring.profiles.active=test
```

## 九、总结

本项目从 JavaEE 企业级 Web 应用的角度，体现了分层架构、REST API、Spring Security 鉴权、异步消息、图数据库建模、实时事件推送、自动化测试和可观测性等综合能力。项目难点不在单表 CRUD，而在如何把非线性讨论、不可变历史、AI 编排和前端实时反馈组合成一个可运行的工程系统。
