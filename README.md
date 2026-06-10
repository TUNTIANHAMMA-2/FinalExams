# FinalExams

本仓库整理了几门期末作业的最终交付物和答辩辅助材料。目录中的子项目类型不同：有软件工程设计报告、基于 RhizoDelta 的课程报告，也有可运行的 Python AI 项目。根目录 README 作为统一入口，方便快速找到正式报告、答辩稿和辅助文档。

## 作业总览

详细进度见 [期末作业进度总览](./作业进度总览.md)。

| 目录 | 课程 / 主题 | 类型 | 主要入口 |
| --- | --- | --- | --- |
| [SoftwareEngineering](./SoftwareEngineering/) | 软件工程导论：宿舍报修管理系统 | 报告型软件工程设计作业 | [答辩稿](./SoftwareEngineering/答辩.md) / [辅助文档](./SoftwareEngineering/docs/README.md) |
| [vuejs-app-dev](./vuejs-app-dev/) | Vue.js 应用开发：RhizoDelta 前端方向报告 | 基于 RhizoDelta 的前端课程报告 | [答辩稿](./vuejs-app-dev/答辩.md) / [辅助文档](./vuejs-app-dev/docs/README.md) |
| [javaee-web-app](./javaee-web-app/) | JavaEE 企业级 Web 应用开发实战：RhizoDelta 后端方向报告 | 基于 RhizoDelta 的后端课程报告 | [答辩稿](./javaee-web-app/答辩.md) / [辅助文档](./javaee-web-app/docs/README.md) |
| [python-ai-course](./python-ai-course/) | 人工智能基础与应用：ASCII 风格人脸识别签到系统 | 可运行的 Python AI + React 演示项目 | [项目 README](./python-ai-course/README.md) / [答辩稿](./python-ai-course/答辩.md) / [辅助文档](./python-ai-course/docs/README.md) |
| [python-data-collection-analysis](./python-data-collection-analysis/) | Python 数据收集与分析：药品销售数据分析 | 可运行的 Python 数据分析项目 + 期末报告 | [项目 README](./python-data-collection-analysis/README.md) / [报告](./python-data-collection-analysis/Python数据收集与分析期末考查报告.md) / [答辩稿](./python-data-collection-analysis/答辩.md) / [辅助文档](./python-data-collection-analysis/docs/README.md) |

## 文档结构

每个子项目都保留顶层 `答辩.md`，用于快速准备口头说明；同时在 `docs/` 下补充统一的辅助文档：

| 文件 | 用途 |
| --- | --- |
| `README.md` | 说明本子项目有哪些正式交付物，以及辅助文档阅读顺序 |
| `project-understanding.md` | 用较短篇幅理解项目背景、目标、角色和亮点 |
| `system-design.md` | 展开系统结构、模块职责、数据流或设计方法 |
| `demo-flow.md` | 提供答辩现场演示或报告讲解步骤 |
| `defense-outline.md` | 用于制作 PPT 或组织口头汇报 |
| `defense-qa.md` | 整理老师可能追问的问题和回答要点 |

## 阅读建议

如果只是确认提交材料是否齐全，先看 [期末作业进度总览](./作业进度总览.md)。

如果准备答辩，建议按这个顺序阅读某个子项目：

1. `答辩.md`
2. `docs/README.md`
3. `docs/project-understanding.md`
4. `docs/demo-flow.md`
5. `docs/defense-outline.md`
6. `docs/defense-qa.md`

如果要运行人工智能课程项目，请进入 [python-ai-course](./python-ai-course/) 并按该目录下的 README 安装依赖、启动后端和前端。

## 交付物说明

- Word、PDF、课程考查方案、报告模板等正式文件保留在各子项目根目录。
- `python-data-collection-analysis/` 已从材料包扩展为可运行的数据分析作业，包含原始材料、分析代码、生成结果、期末报告、Word 版报告和答辩文档。
- `generated/`、`images/`、运行时数据、模型文件、虚拟环境和本地工具目录属于生成物或本地环境内容，不作为核心提交材料。
- `javaee-web-app/` 和 `vuejs-app-dev/` 的报告均基于 RhizoDelta 真实工程整理，更多说明见 [RhizoDelta 课程交付物说明](./RhizoDelta课程交付物说明.md)。
- `python-ai-course/` 是代码型项目，包含后端、前端、测试、运行说明和答辩材料；运行时数据默认不进入 Git。
