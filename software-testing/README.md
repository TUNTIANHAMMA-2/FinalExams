# 软件测试课程作业（《软件测试技术》期末考查）

本目录是《软件测试技术》期末考查作业。作业形式：**个人独立提交**（封面"每人一份"）。

- **被测系统（SUT）**：RhizoDelta —— 图谱化非线性讨论系统（Spring Boot + Neo4j 后端，React/Vite 前端，B/S 架构）。
- **选题理由**：自有项目、熟悉度高；提供 19 个 Controller、数十个 `/api/**` REST 接口，统一 `ApiResponse` 响应包；本地实例可直接运行（默认 `http://localhost:8090`），便于执行接口测试并截图取证。仓库内 JavaEE、Vue 两门课程报告已基于 RhizoDelta，口径一致。
- **专项测试工具（三选一）**：**Postman**（接口测试）。

> 参考模板里的样例被测系统是"B/S 资产管理系统"。本作业已使用 `templates/` 下的原始 Word/Excel 模板副本生成提交版文档，并把样例模块（权限/登录/个人信息/资产 CRUD）替换为 RhizoDelta 的真实模块。
> `templates/参考项目（期末）.txt` 中列出的 iHRM、学成在线、传智健康等为可选参考项目账号。本作业使用自有 B/S 项目 RhizoDelta 替代，原因是系统可本地运行、接口可复现、截图和缺陷证据可完整留存。

## 测试范围（圈定，避免课程作业过载）

| 范围 | 模块 | 处理方式 |
| --- | --- | --- |
| 本轮核心子集（功能 + 接口测试） | 认证授权、用户资料基础接口、图谱查询基础接口、登出与 token 吊销 | 完整用例 + Postman 接口用例 |
| 后续扩展 | 发帖与关联、头像上传、关注/拉黑、治理决策与复核 | 已在计划和总结中列明，不计入本轮通过率 |
| 仅说明范围外 | SSE 实时推送、RabbitMQ 异步重试、AI 摘要/向量质量 | 说明取舍理由，不作为本轮验收结论依据 |

## 交付物清单

| 交付物 | 文件 | 状态 |
| --- | --- | --- |
| 考查报告封面 | [《软件测试技术》考查报告.doc](./《软件测试技术》考查报告.doc) | ✅ 已按模板副本填写（身份字段保留请填写） |
| 1 测试方案 | [deliverables/1-测试方案.docx](./deliverables/1-测试方案.docx) | ✅ 已按 `1测试方案.doc` 模板副本填写 |
| 2 测试用例 | [deliverables/2-测试用例.xls](./deliverables/2-测试用例.xls) | ✅ 已按 `2测试用例.xls` 模板副本填写，28 条用例：20 条已实测 + 8 条补充设计，并新增等价类划分/方法覆盖工作表 |
| 3 Bug 缺陷报告清单 | [deliverables/3-Bug缺陷报告清单.xls](./deliverables/3-Bug缺陷报告清单.xls) | ✅ 已按 `3Bug缺陷报告清单.xls` 模板副本填写，2 个实测缺陷 |
| 4 接口测试（Postman） | [deliverables/4-接口测试-Postman.md](./deliverables/4-接口测试-Postman.md) | ✅ 20 用例已跑 + newman 报告（BUG-001 作为已知缺陷观察，不阻断验收版报告） |
| 5 测试总结报告 | [deliverables/5-测试总结报告.docx](./deliverables/5-测试总结报告.docx) | ✅ 已按 `5测试总结报告.doc` 模板副本填写 |

## 阅读顺序

1. [《软件测试技术》考查报告.doc](./《软件测试技术》考查报告.doc)（封面、截图与个人总结）
2. [docs/README.md](./docs/README.md)（辅助文档导航）
3. [docs/project-understanding.md](./docs/project-understanding.md)（被测系统与测试范围）
4. [docs/system-design.md](./docs/system-design.md)（测试策略与用例设计方法）
5. `deliverables/` 下五份交付物（当前正式提交格式：`.docx`、`.xls`、`.md`）
6. [docs/demo-flow.md](./docs/demo-flow.md) → [docs/defense-outline.md](./docs/defense-outline.md) → [docs/defense-qa.md](./docs/defense-qa.md)（答辩准备）

## 目录结构

```
software-testing/
├─ 《软件测试技术》考查报告.doc  # 模板副本填写版（个人）
├─ deliverables/                  # 五份核心交付物
├─ templates/                     # 原始参考模板（从期末压缩包归档）
├─ docs/                          # 选题理解 / 测试策略 / 答辩辅助
├─ generated/                     # 截图、导出产物（中间物）
└─ scripts/                       # Postman 构建、截图、模板副本生成脚本
```

## 状态与待办

- [x] 解压期末压缩包、归档原始模板到 `templates/`
- [x] 确定被测系统（RhizoDelta）、工具（Postman）、提交形式（个人）
- [x] 搭好目录与全部交付物骨架
- [x] 填充功能/接口测试用例（28 条：20 条基于运行中的 8090 实例取真实输入/输出，8 条为后续回归补充设计）
- [x] 在测试用例 XLS 中补充输入条件分析、等价类划分、边界值、错误推测、因果图和场景法覆盖关系
- [x] 编写 Postman 接口用例集并用 newman 导出测试报告（`generated/postman-report.html`）
- [x] 汇总缺陷（2 个低危）、撰写测试总结报告
- [x] 采集界面截图（登录/主界面/设置）+ 成果截图（newman 报告/接口证据）到 `generated/images/`
- [x] 使用 `templates/` 原始模板副本生成 Word/Excel 提交版：考查报告、测试方案、测试用例、缺陷清单、测试总结报告
- [x] 统一范围口径：本轮结论只覆盖已实测的核心子集，发帖/关联/治理/SSE 明确列为后续扩展或范围外
- [ ] 扩展：发帖异步一致性、头像上传校验、治理决策主流程、SSE 冒烟
- [ ] 替换封面身份信息（姓名/学号/班级/指导教师），目前为"请填写"

> 身份信息按本仓库其它课程报告的惯例先留"请填写"，提交前在文档中统一替换。
> UI 截图来自线上部署 `https://rhizodelta.toadtools.online`；接口自动化证据来自本地同版本后端 `http://localhost:8090`。
> 测试期间在开发库注册了测试账号 `qa_tester_st`（及 newman 每次运行生成的 `qa_<时间戳>` 账号），如需可在 Neo4j 中清理。

## 重新生成提交版文档

```bash
cd software-testing
PYTHONPATH=/tmp/st-pydeps python3 scripts/generate_template_deliverables.py
```

生成脚本使用 `python-docx` 生成 `.docx`，使用 `xlwt` 直接生成 `.xls`。若本机未准备 `/tmp/st-pydeps`，可先安装 `python-docx` 与 `xlwt`。
