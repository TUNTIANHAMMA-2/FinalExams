# JavaEE 企业级 Web 应用开发实战：RhizoDelta 后端方向报告

本目录是《JavaEE 企业级 Web 应用开发实战》期末课程设计报告。报告基于 RhizoDelta 后端工程整理，侧重 Spring Boot、图数据库、异步任务、认证授权、实时事件和 AI 编排等后端设计。

## 交付物

| 文件 | 用途 |
| --- | --- |
| [JavaEE企业级Web应用开发实战考查方案.docx](./JavaEE企业级Web应用开发实战考查方案.docx) | 课程考查方案 |
| [JavaEE企业级Web应用开发实战期末课程设计报告.doc](./JavaEE企业级Web应用开发实战期末课程设计报告.doc) | 正式 Word 报告 |
| [JavaEE企业级Web应用开发实战期末课程设计报告.docx](./JavaEE企业级Web应用开发实战期末课程设计报告.docx) | 正式 Word 报告备份 |
| [JavaEE企业级Web应用开发实战期末课程设计报告.md](./JavaEE企业级Web应用开发实战期末课程设计报告.md) | 报告内容源文件 |
| [答辩.md](./答辩.md) | 口头答辩稿 |
| [docs/](./docs/README.md) | 辅助理解、演示和问答文档 |

## 阅读顺序

1. [答辩.md](./答辩.md)
2. [docs/README.md](./docs/README.md)
3. [docs/project-understanding.md](./docs/project-understanding.md)
4. [docs/system-design.md](./docs/system-design.md)
5. [docs/demo-flow.md](./docs/demo-flow.md)
6. [docs/defense-outline.md](./docs/defense-outline.md)
7. [docs/defense-qa.md](./docs/defense-qa.md)

## 结构说明

- `generated/` 保存报告生成过程中的 HTML 等中间文件。
- `images/` 保存架构图、数据模型图和关键流程图。
- 考查方案偏向常规 Spring Boot + MyBatis-Plus 单表 CRUD 系统；本报告以 RhizoDelta 真实后端工程为载体，使用 Spring Boot、Spring Data Neo4j、RabbitMQ、Redis、JWT、SSE 等技术。答辩时应说明这种课程要求和真实工程实现之间的对应关系。

