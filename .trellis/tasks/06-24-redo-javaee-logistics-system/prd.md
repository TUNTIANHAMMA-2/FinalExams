# 重做 JavaEE 物流管理系统

## Goal

将旧的 `javaee-web-app` RhizoDelta 课程报告资料完整归档到独立目录，并在原路径重建为一个便于交作业和答辩的 Java Spring Boot 物流管理系统，使用 Spring MVC、MyBatis-Plus、MySQL 和 Thymeleaf 作为主要技术栈。

## Requirements

* 归档现有 `javaee-web-app` 全部内容，保留旧报告、图片、模板和未提交文件。
* 在 `javaee-web-app` 原路径创建 Maven/Spring Boot 工程。
* 技术栈使用 Java 17、Spring Boot、Spring MVC、MyBatis-Plus、Thymeleaf、MySQL、Lombok、Validation、devtools。
* 不引入 Redis、RabbitMQ 等复杂组件，优先保证课程作业可运行、可讲清楚。
* 提供物流管理系统基础业务模块：客户、司机、车辆、运单。
* 首页直接展示系统工作台和核心统计，不做营销页。
* 提供运单列表、查询筛选、新增、编辑、删除等核心演示流程。
* 提供符合 REST 风格的运单接口，覆盖 GET、POST、PUT、DELETE 和统一响应封装。
* 更新 README，说明运行方式、功能模块和目录结构。
* 提交 MySQL 建表 SQL、测试数据、课程报告和答辩材料。

## Acceptance Criteria

* [ ] 旧 `javaee-web-app` 内容完整移动到顶层归档目录。
* [ ] 新 `javaee-web-app/pom.xml` 可被 Maven 识别。
* [ ] `mvn test` 至少能完成编译和不依赖数据库连接的单元测试。
* [ ] 启动应用后可访问 Thymeleaf 页面并查看 MySQL 演示数据。
* [ ] 运单可新增、编辑、删除和按状态筛选。
* [ ] REST 接口返回 `code/message/data` 统一结构。

## Definition of Done

* 代码结构清晰，按 entity/mapper/service/controller/view 分层。
* 表单入口使用 Bean Validation 做基本校验。
* 本地质量检查通过，或者明确记录无法运行的原因。
* 不修改与本任务无关的其他子项目文件。

## Technical Approach

采用单体 Spring Boot MVC 应用：Controller 接收表单和 REST 请求，Service 管理业务规则和事务，Mapper 使用 MyBatis-Plus 访问 MySQL，Thymeleaf 负责服务端页面渲染。项目提供 MySQL 建表脚本、演示数据、课程报告和答辩提纲。

## Decision (ADR-lite)

**Context**: 用户要求彻底推翻旧 JavaEE 子项目，重做为便于交作业和答辩的物流管理系统，并确认不需要 Redis/RabbitMQ 等复杂设计。

**Decision**: 用一个课程演示友好的 Spring Boot 3 + Spring MVC + MyBatis-Plus + MySQL + Thymeleaf 单体应用实现核心物流管理流程。

**Consequences**: 技术栈贴近常见 JavaEE 课程 CRUD 项目和 MySQL 实训环境，便于报告截图和答辩讲解；不展示消息队列、缓存等扩展能力。

## Out of Scope

* 用户登录、权限角色、审计日志。
* JPA/Hibernate 持久化实现。
* H2 内存数据库演示模式。
* Redis、RabbitMQ 等中间件集成。
* 真实地图、短信、快递接口、支付接口集成。
* 大规模前端 SPA 或移动端。

## Technical Notes

* 当前 Trellis 只登记 `python-ai-course` 规范，`javaee-web-app` 无专属规范；本任务遵循共享思考指南和现有仓库组织。
* 旧目录当前主要是课程报告资料，不是可运行 Java 工程。
