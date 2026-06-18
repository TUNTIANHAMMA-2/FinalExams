# 软件测试课程作业（《软件测试技术》期末考查）

本目录是《软件测试技术》期末考查作业。作业形式：**个人独立提交**（封面"每人一份"）。

- **被测系统（SUT）**：RhizoDelta —— 图谱化非线性讨论系统（Spring Boot + Neo4j 后端，React/Vite 前端，B/S 架构）。
- **选题理由**：自有项目、熟悉度高；提供 19 个 Controller、数十个 `/api/**` REST 接口，统一 `ApiResponse` 响应包；本地实例可直接运行（默认 `http://localhost:8090`），便于执行接口测试并截图取证。仓库内 JavaEE、Vue 两门课程报告已基于 RhizoDelta，口径一致。
- **专项测试工具（三选一）**：**Postman**（接口测试）。

> 参考模板里的样例被测系统是"B/S 资产管理系统"，仅作格式参考；本作业把它替换为 RhizoDelta，并把样例模块（权限/登录/个人信息/资产 CRUD）映射到 RhizoDelta 的真实模块。

## 测试范围（圈定，避免课程作业过载）

| 范围 | 模块 | 处理方式 |
| --- | --- | --- |
| 核心（功能 + 接口测试） | 认证授权、用户资料与社交、发帖与关联、图谱查询 | 完整用例 + Postman 接口用例 |
| 选测 | 治理决策与复核（合并/分支/注入/回滚等） | 主流程用例 |
| 仅冒烟 / 范围外 | SSE 实时推送、RabbitMQ 异步、AI 摘要/向量 | 连通性冒烟，或注明"不在本次范围" |

## 交付物清单

| 交付物 | 文件 | 状态 |
| --- | --- | --- |
| 考查报告封面 | [《软件测试技术》考查报告.md](./《软件测试技术》考查报告.md) | 🟡 待填身份/个人总结 |
| 1 测试方案 | [deliverables/1-测试方案.md](./deliverables/1-测试方案.md) | ✅ 完成（计划+模块划分） |
| 2 测试用例 | [deliverables/2-测试用例.md](./deliverables/2-测试用例.md) | ✅ 20 条实测用例 |
| 3 Bug 缺陷报告清单 | [deliverables/3-Bug缺陷报告清单.md](./deliverables/3-Bug缺陷报告清单.md) | ✅ 2 个实测缺陷 |
| 4 接口测试（Postman） | [deliverables/4-接口测试-Postman.md](./deliverables/4-接口测试-Postman.md) | ✅ 20 用例已跑 + newman 报告 |
| 5 测试总结报告 | [deliverables/5-测试总结报告.md](./deliverables/5-测试总结报告.md) | ✅ 完成（含统计与结论） |

## 阅读顺序

1. [《软件测试技术》考查报告.md](./《软件测试技术》考查报告.md)（封面与总览）
2. [docs/README.md](./docs/README.md)（辅助文档导航）
3. [docs/project-understanding.md](./docs/project-understanding.md)（被测系统与测试范围）
4. [docs/system-design.md](./docs/system-design.md)（测试策略与用例设计方法）
5. `deliverables/` 下五份交付物
6. [docs/demo-flow.md](./docs/demo-flow.md) → [docs/defense-outline.md](./docs/defense-outline.md) → [docs/defense-qa.md](./docs/defense-qa.md)（答辩准备）

## 目录结构

```
software-testing/
├─ 《软件测试技术》考查报告.md   # 封面/总览（个人）
├─ deliverables/                  # 五份核心交付物
├─ templates/                     # 原始参考模板（从期末压缩包归档）
├─ docs/                          # 选题理解 / 测试策略 / 答辩辅助
├─ generated/                     # 截图、导出产物（中间物）
└─ scripts/                       # 报告生成 / 测试脚本（后续）
```

## 状态与待办

- [x] 解压期末压缩包、归档原始模板到 `templates/`
- [x] 确定被测系统（RhizoDelta）、工具（Postman）、提交形式（个人）
- [x] 搭好目录与全部交付物骨架
- [x] 填充功能/接口测试用例（20 条，基于运行中的 8090 实例取真实输入/输出）
- [x] 编写 Postman 接口用例集并用 newman 导出测试报告（`generated/postman-report.html`）
- [x] 汇总缺陷（2 个低危）、撰写测试总结报告
- [x] 采集界面截图（登录/主界面/设置）+ 成果截图（newman 报告/接口证据）到 `generated/images/`
- [ ] 扩展：发帖异步一致性、头像上传校验、治理决策主流程、SSE 冒烟
- [ ] 替换封面身份信息（姓名/学号/系别/专业/年级/班级/指导教师），目前为"请填写"
- [ ] （可选）将 md 交付物导出为 Word/PDF 提交版

> 身份信息按本仓库其它课程报告的惯例先留"请填写"，提交前在文档中统一替换。
> 测试期间在开发库注册了测试账号 `qa_tester_st`（及 newman 每次运行生成的 `qa_<时间戳>` 账号），如需可在 Neo4j 中清理。
