#!/usr/bin/env python3
"""
Generate software-testing deliverables from the original course templates.

The source templates under software-testing/templates are old .doc/.xls files.
This script converts them to docx/xlsx working copies and fills them with the
actual RhizoDelta testing content.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


try:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Inches, Pt
    from openpyxl import load_workbook
    from openpyxl.styles import Alignment
except ImportError as exc:  # pragma: no cover - user-facing setup guard
    raise SystemExit(
        "Missing dependency: python-docx/openpyxl. "
        "Install with: python3 -m pip install python-docx openpyxl"
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"
DELIVERABLES = ROOT / "deliverables"
GENERATED = ROOT / "generated"

TEST_DATE = "2026.6.18"
AUTHOR = "本人"
TEAM = "个人独立完成"


PLAN_TEMPLATE = TEMPLATES / "1测试方案.doc"
CASE_TEMPLATE = TEMPLATES / "2测试用例.xls"
BUG_TEMPLATE = TEMPLATES / "3Bug缺陷报告清单.xls"
SUMMARY_TEMPLATE = TEMPLATES / "5测试总结报告.doc"
REPORT_TEMPLATE = TEMPLATES / "《软件测试技术》考查报告（每人一份）.doc"


CASES = [
    ("RD-ST-SRS001-001", "认证授权", "合法注册", "高", "用户名未占用", "{username,password≥8,display_name}", "POST /api/auth/register，提交合法注册信息", "HTTP 200，code=0，返回 token、refresh_token、user", "一致", "通过"),
    ("RD-ST-SRS001-002", "认证授权", "重复用户名注册", "高", "用户名已存在", "重复提交 qa_tester_st", "POST /api/auth/register，再次注册同名用户", "按 REST 语义应返回 HTTP 409 Conflict，业务码 40901", "HTTP 400，code=40001，message=username already exists", "未通过，BUG-001"),
    ("RD-ST-SRS001-003", "认证授权", "密码少于 8 位", "高", "无", 'password="123"', "POST /api/auth/register", "HTTP 400，提示密码至少 8 位", "一致", "通过"),
    ("RD-ST-SRS001-004", "认证授权", "空用户名注册", "中", "无", 'username=""', "POST /api/auth/register", "HTTP 400，提示 must not be blank", "一致", "通过"),
    ("RD-ST-SRS001-005", "认证授权", "正确登录", "高", "账号已注册且 ACTIVE", "正确 username/password", "POST /api/auth/login", "HTTP 200，code=0，返回 token", "一致", "通过"),
    ("RD-ST-SRS001-006", "认证授权", "密码错误登录", "高", "账号存在", "错误 password", "POST /api/auth/login", "HTTP 401，提示 invalid username or password", "一致", "通过"),
    ("RD-ST-SRS001-007", "认证授权", "不存在用户登录", "高", "无", "不存在用户名", "POST /api/auth/login", "HTTP 401，提示与密码错误一致，不泄露账号存在性", "一致", "通过"),
    ("RD-ST-SRS001-008", "认证授权", "带 token 查询当前用户", "高", "已登录", "Authorization: Bearer <token>", "GET /api/auth/me", "HTTP 200，返回 username 与登录账号匹配", "一致", "通过"),
    ("RD-ST-SRS001-009", "认证授权", "无 token 查询当前用户", "高", "无", "不带 Authorization", "GET /api/auth/me", "HTTP 401，提示 authentication required", "一致", "通过"),
    ("RD-ST-SRS001-010", "认证授权", "伪造 token 查询当前用户", "高", "无", "Bearer faketoken.abc.def", "GET /api/auth/me", "HTTP 401，提示 invalid token", "一致", "通过"),
    ("RD-ST-SRS001-011", "认证授权", "刷新令牌", "中", "持有有效 refresh_token", "{refresh_token}", "POST /api/auth/refresh", "HTTP 200，发放新 token", "一致", "通过"),
    ("RD-ST-SRS002-001", "用户资料与社交", "查看本人资料", "中", "已登录", "Bearer token", "GET /api/users/me/profile", "HTTP 200，返回 user_id、username、display_name 等字段", "一致", "通过"),
    ("RD-ST-SRS002-002", "用户资料与社交", "未登录查询资料", "高", "无", "无 token", "GET /api/users/me/profile", "HTTP 401，提示 authentication required", "一致", "通过"),
    ("RD-ST-SRS002-003", "用户资料与社交", "查询在线状态", "低", "已登录", "Bearer token", "GET /api/users/me/status", "HTTP 200，online=true，last_active 可解析", "接口可用；last_active 为字符串型 epoch，见 BUG-002", "通过，记录低危缺陷"),
    ("RD-ST-SRS002-004", "用户资料与社交", "动态流分页", "中", "已登录", "Bearer token", "GET /api/users/me/feed", "HTTP 200，返回 items 数组和分页字段", "一致", "通过"),
    ("RD-ST-SRS004-001", "图谱查询", "查询根话题", "中", "图数据库中有数据", "Bearer token", "GET /api/nodes/roots", "HTTP 200，data 为节点数组", "一致", "通过"),
    ("RD-ST-SRS004-002", "图谱查询", "非法 UUID 格式", "中", "无", 'id="not-a-uuid"', "GET /api/nodes/{id}", "HTTP 400，提示 id must be a valid UUID", "一致，格式校验先于查库", "通过"),
    ("RD-ST-SRS004-003", "图谱查询", "合法但不存在的节点", "中", "无", "00000000-0000-0000-0000-000000000000", "GET /api/nodes/{id}", "HTTP 404，code=40401，Node not found", "一致", "通过"),
    ("RD-ST-SRS001-012", "认证收尾", "登出", "中", "已登录", "Bearer token", "POST /api/auth/logout", "HTTP 200，code=0", "一致", "通过"),
    ("RD-ST-SRS001-013", "认证收尾", "登出后复用旧 token", "高", "已登出", "旧 token", "GET /api/auth/me", "HTTP 401，提示 token revoked，黑名单生效", "一致", "通过"),
]


BUGS = [
    (
        "BUG-001",
        "认证授权",
        "POST /api/auth/register",
        "重复用户名注册返回 400，HTTP 语义应为 409 Conflict",
        "浏览器/工具：Postman + newman；环境：http://localhost:8090。\n"
        "步骤：1. 使用 qa_tester_st 注册成功；2. 再次使用相同 username 调用注册接口；3. 观察响应。\n"
        "实际：HTTP 400，code=40001，message=username already exists。\n"
        "预期：HTTP 409，业务码 40901。建议重复注册场景改用 ApiResponse.conflict(...)。",
        "低",
        AUTHOR,
        "见 generated/postman-report.html 与 generated/images/02_api_evidence.png",
    ),
    (
        "BUG-002",
        "用户资料与社交",
        "GET /api/users/me/status",
        "last_active 为字符串型 epoch，与其它时间字段格式不一致",
        "浏览器/工具：Postman；环境：http://localhost:8090。\n"
        "步骤：1. 登录取得 Bearer token；2. 调用 /api/users/me/status；3. 查看 data.last_active。\n"
        "实际：last_active 类似 \"1781751037890\"，为字符串型毫秒时间戳。\n"
        "预期：与 updated_at 等字段统一为 ISO8601，或统一为数值型毫秒并在接口文档说明。",
        "低",
        AUTHOR,
        "见接口响应记录",
    ),
]


CASE_COUNTS = [
    ("认证授权", 11),
    ("用户资料与社交", 4),
    ("图谱查询", 3),
    ("认证收尾", 2),
]

BUG_SUMMARY = [
    ("认证授权", 0, 0, 0, 0, 1, 1),
    ("用户资料与社交", 0, 0, 0, 0, 1, 1),
    ("发帖与关联", 0, 0, 0, 0, 0, 0),
    ("图谱查询", 0, 0, 0, 0, 0, 0),
    ("合计", 0, 0, 0, 0, 2, 2),
]


def run_soffice(args: list[str], *, cwd: Path | None = None) -> None:
    env = os.environ.copy()
    env.setdefault("SAL_USE_VCLPLUGIN", "svp")
    profile = Path(tempfile.mkdtemp(prefix="st-lo-profile-"))
    command = [
        "libreoffice",
        "--headless",
        "--invisible",
        "--nodefault",
        "--nolockcheck",
        "--nologo",
        "--nofirststartwizard",
        f"-env:UserInstallation={profile.as_uri()}",
        *args,
    ]
    subprocess.run(command, cwd=cwd, env=env, check=True)


def convert_template(src: Path, out_dir: Path, target_ext: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    before = {p.name for p in out_dir.iterdir()}
    run_soffice(["--convert-to", target_ext, "--outdir", str(out_dir), str(src)])
    after = [p for p in out_dir.iterdir() if p.name not in before and p.suffix.lower() == f".{target_ext}"]
    if after:
        return after[0]
    guessed = out_dir / f"{src.stem}.{target_ext}"
    if guessed.exists():
        return guessed
    raise FileNotFoundError(f"converted file not found for {src}")


def set_cell_text(cell, text: str) -> None:
    cell.text = ""
    for idx, line in enumerate(str(text).split("\n")):
        if idx == 0:
            para = cell.paragraphs[0]
        else:
            para = cell.add_paragraph()
        run = para.add_run(line)
        run.font.name = "宋体"
        run.font.size = Pt(10.5)


def add_para(doc: Document, text: str = "", style: str | None = None, bold: bool = False) -> None:
    p = doc.add_paragraph(style=style)
    if text:
        run = p.add_run(text)
        run.bold = bold
        run.font.name = "宋体"
        run.font.size = Pt(10.5)


def add_heading(doc: Document, text: str, level: int) -> None:
    doc.add_heading(text, level=level)


def add_table(doc: Document, headers: list[str], rows: list[tuple | list]) -> None:
    table = doc.add_table(rows=1, cols=len(headers))
    for style_name in ("Table Grid", "网格型", "Table Normal"):
        try:
            table.style = style_name
            break
        except KeyError:
            continue
    for idx, header in enumerate(headers):
        set_cell_text(table.rows[0].cells[idx], header)
    for row_data in rows:
        row = table.add_row()
        for idx, value in enumerate(row_data):
            set_cell_text(row.cells[idx], str(value))


def clear_doc_body(doc: Document) -> None:
    body = doc._element.body
    for child in list(body):
        if child.tag.endswith("sectPr"):
            continue
        body.remove(child)


def set_doc_defaults(doc: Document) -> None:
    style = doc.styles["Normal"]
    style.font.name = "宋体"
    style.font.size = Pt(10.5)
    for section in doc.sections:
        section.top_margin = Inches(0.9)
        section.bottom_margin = Inches(0.9)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)


def build_plan(template_docx: Path, output: Path) -> None:
    doc = Document(template_docx)
    clear_doc_body(doc)
    set_doc_defaults(doc)

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("RhizoDelta 图谱化非线性讨论系统测试方案")
    run.bold = True
    run.font.name = "宋体"
    run.font.size = Pt(18)

    add_heading(doc, "目 录", 1)
    for item in [
        "1 概述",
        "1.1 编写目的",
        "1.2 阅读对象",
        "1.3 系统背景",
        "2 测试任务",
        "2.1 测试目的",
        "2.2 测试参考文档",
        "2.3 测试提交文档",
        "3 测试资源",
        "3.1 硬件配置",
        "3.2 软件配置",
        "3.3 人力资源分配",
        "4 测试计划",
        "4.1 整体功能模块划分",
        "5 测试整体进度安排",
        "6 相关风险",
    ]:
        add_para(doc, item)

    add_heading(doc, "1 概述", 1)
    add_heading(doc, "1.1 编写目的", 2)
    add_para(doc, "本文档为 RhizoDelta 软件测试课程作业的测试方案，编写目的包括：")
    for text in [
        "确认被测系统的模块划分、测试范围与范围边界。",
        "确认个人独立测试任务、执行方式与交付文档。",
        "确定测试环境、接口工具、测试数据和外部依赖。",
        "识别测试过程风险并给出应对方案。",
        "为后续测试用例、缺陷清单和总结报告提供依据。",
    ]:
        add_para(doc, f"    {text}")
    add_heading(doc, "1.2 阅读对象", 2)
    add_para(doc, "本文档的预期读者包括：课程指导教师、评审人员、项目负责人、软件设计开发人员、测试人员以及后续维护人员。")
    add_heading(doc, "1.3 系统背景", 2)
    add_para(doc, "RhizoDelta 是一个 B/S 架构的图谱化非线性讨论系统，后端采用 Spring Boot 3、Spring Security + JWT、Spring Data Neo4j、Redis、RabbitMQ 与 SSE，前端采用 React/Vite。系统通过图数据库组织讨论节点与关联，通过异步队列处理发帖、摘要等高成本任务，并向前端实时推送状态变化。本次测试以可运行的 RhizoDelta 实例为被测系统，重点验证认证授权、用户资料与社交、图谱查询等核心 REST 接口和黑盒功能行为。")

    add_heading(doc, "2 测试任务", 1)
    add_heading(doc, "2.1 测试目的", 2)
    for text in [
        "确定核心功能是否正常可用，业务流程是否闭环。",
        "确定 REST 接口的状态码、统一响应包、字段命名、参数校验和鉴权约束是否符合预期。",
        "确定需求范围是否一致、完整、可验证。",
        "通过 Postman/newman 形成可复现的接口测试证据。",
        "发现并记录缺陷，给出系统质量结论和后续改进建议。",
    ]:
        add_para(doc, f"    {text}")
    add_heading(doc, "2.2 测试参考文档", 2)
    add_table(
        doc,
        ["文档名", "版本", "日期", "作者", "备注"],
        [
            ("RhizoDelta 项目说明与课程交付物说明", "1.0", "2026.6.18", AUTHOR, "说明被测系统技术栈、功能与课程口径"),
            ("软件测试 docs/project-understanding.md", "1.0", "2026.6.18", AUTHOR, "被测系统理解、角色、模块与范围边界"),
            ("软件测试 docs/system-design.md", "1.0", "2026.6.18", AUTHOR, "测试策略、用例设计方法、环境与通过准则"),
            ("Postman Collection 与 newman 报告", "1.0", "2026.6.18", AUTHOR, "接口测试可复现证据"),
        ],
    )
    add_heading(doc, "2.3 测试提交文档", 2)
    add_table(
        doc,
        ["文档名", "版本", "日期", "作者", "备注"],
        [
            ("《1-测试方案》", "1.0", TEST_DATE, AUTHOR, "由 1测试方案.doc 模板副本填写"),
            ("《2-测试用例》", "1.0", TEST_DATE, AUTHOR, "由 2测试用例.xls 模板副本填写，20 条用例"),
            ("《3-Bug缺陷报告清单》", "1.0", TEST_DATE, AUTHOR, "由 3Bug缺陷报告清单.xls 模板副本填写，2 个缺陷"),
            ("《4-接口测试-Postman》", "1.0", TEST_DATE, AUTHOR, "Postman 专项测试用例、集合、环境和 newman 报告"),
            ("《5-测试总结报告》", "1.0", TEST_DATE, AUTHOR, "由 5测试总结报告.doc 模板副本填写"),
        ],
    )

    add_heading(doc, "3 测试资源", 1)
    add_heading(doc, "3.1 硬件配置", 2)
    add_table(doc, ["关键项", "数量", "性能要求"], [("测试 PC 机（客户端/接口执行机）", "1", "CPU：x86_64 多核；内存：8GB 及以上；硬盘：20GB 可用空间；网络可访问被测后端")])
    add_heading(doc, "3.2 软件配置", 2)
    add_table(
        doc,
        ["资源名称/类型", "数量", "配置"],
        [
            ("被测后端", "1", "RhizoDelta Spring Boot，http://localhost:8090"),
            ("数据与中间件", "3", "Neo4j、Redis、RabbitMQ"),
            ("浏览器环境", "1", "Chrome 最新版"),
            ("接口测试工具", "1", "Postman + newman，集合 20 条请求，58 条断言"),
            ("文档工具", "1", "Word/WPS/LibreOffice，可打开 doc/docx/xls/xlsx"),
            ("截图工具", "1", "浏览器截图与 newman htmlextra 报告截图"),
        ],
    )
    add_heading(doc, "3.3 人力资源分配", 2)
    add_table(
        doc,
        ["角色", "人员", "主要职责"],
        [
            (
                "测试负责人（个人独立完成）",
                AUTHOR,
                "分析 RhizoDelta 功能与接口；划定测试范围；编写测试方案、测试用例、缺陷清单与总结报告；构建 Postman 集合；执行 newman 测试；整理截图和结论。",
            )
        ],
    )

    add_heading(doc, "4 测试计划", 1)
    add_heading(doc, "4.1 整体功能模块划分", 2)
    add_table(
        doc,
        ["需求编号", "模块名称", "功能名称", "测试人员"],
        [
            ("RD-ST-SRS001", "认证授权", "注册、登录、刷新令牌、登出、当前用户、JWT 鉴权与 token 吊销", AUTHOR),
            ("RD-ST-SRS002", "用户资料与社交", "个人资料、头像、关注、拉黑、动态流、在线状态", AUTHOR),
            ("RD-ST-SRS003", "发帖与关联", "发帖异步入队、创建/删除节点关联（本轮列入后续扩展）", AUTHOR),
            ("RD-ST-SRS004", "图谱查询", "根话题、节点详情、拓扑上下文、谱系、子代、讨论树、溯源与关联查询", AUTHOR),
            ("RD-ST-SRS005", "治理决策与复核", "合并、分支、注入、回滚、审批、驳回与审计（选测）", AUTHOR),
            ("RD-ST-SRS006", "AI 与实时", "节点摘要、向量、相似检索、SSE 事件流（冒烟/范围外说明）", AUTHOR),
        ],
    )

    add_heading(doc, "5 测试整体进度安排", 1)
    add_table(
        doc,
        ["测试阶段", "时间安排", "参与人员", "测试工作内容安排", "产出"],
        [
            ("需求分析", "2026.6.18 19:00-19:30", AUTHOR, "分析 RhizoDelta 模块、接口、角色和测试边界", "项目理解、测试范围"),
            ("测试方案", "2026.6.18 19:30-20:00", AUTHOR, "按模板编写测试资源、计划、风险与提交物", "《1-测试方案》"),
            ("测试用例", "2026.6.18 20:00-20:40", AUTHOR, "用等价类、边界值、错误推测、场景法设计 20 条用例", "《2-测试用例》"),
            ("接口执行", "2026.6.18 20:40-21:10", AUTHOR, "生成 Postman 集合并通过 newman 执行 20 个请求、58 条断言", "newman HTML/JSON 报告"),
            ("缺陷登记", "2026.6.18 21:10-21:25", AUTHOR, "登记重复注册状态码与 last_active 时间格式问题", "《3-Bug缺陷报告清单》"),
            ("总结归档", "2026.6.18 21:25-21:45", AUTHOR, "汇总覆盖、缺陷、结论和后续建议", "《5-测试总结报告》与课程考查报告"),
        ],
    )

    add_heading(doc, "6 相关风险", 1)
    add_table(
        doc,
        ["风险类型", "风险", "解决方案"],
        [
            ("环境风险", "Neo4j、Redis、RabbitMQ 或后端 8090 端口未启动，导致接口不可达", "测前检查依赖和 baseUrl；Postman 环境变量统一配置；失败时先排除环境问题"),
            ("数据风险", "注册、发帖等操作污染开发库数据", "使用 qa_tester_st 与 qa_时间戳账号隔离测试数据，必要时在 Neo4j 中清理"),
            ("范围风险", "SSE、AI 摘要、异步队列等功能涉及外部依赖和最终一致性，课程作业周期内难以充分覆盖", "核心 REST 功能完整测试，异步/AI/实时功能标记为冒烟或后续扩展"),
            ("时间风险", "个人独立提交，测试时间有限", "优先认证授权、用户资料、图谱查询等高价值模块，自动化接口测试提高执行效率"),
            ("契约风险", "HTTP 状态码、业务码、时间字段格式不统一", "在用例和缺陷清单中明确断言状态码、业务码、字段命名和时间格式"),
        ],
    )
    doc.save(output)


def build_summary(template_docx: Path, output: Path) -> None:
    doc = Document(template_docx)
    clear_doc_body(doc)
    set_doc_defaults(doc)
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("RhizoDelta 图谱化非线性讨论系统测试总结报告")
    run.bold = True
    run.font.name = "宋体"
    run.font.size = Pt(18)

    add_heading(doc, "目录", 1)
    for item in [
        "1 测试概述",
        "1.1 编写目的",
        "1.2 项目背景",
        "2 测试参考文档",
        "3 项目组成员",
        "4 测试设计介绍",
        "4.1 测试用例设计方法",
        "4.2 测试环境与配置",
        "4.3 测试方法",
        "5 测试进度",
        "6 用例汇总",
        "7 缺陷分析",
        "8 测试结论",
    ]:
        add_para(doc, item)

    add_heading(doc, "1 测试概述", 1)
    add_heading(doc, "1.1 编写目的", 2)
    for text in [
        "确认测试用例、缺陷登记和测试方案是否覆盖 RhizoDelta 的核心测试范围。",
        "汇总本次测试活动的环境、方法、进度、执行数据和测试证据。",
        "解释用例设计方法与具体用例的对应关系。",
        "分析缺陷分布与根因，给出后续修复和预防建议。",
        "形成被测系统当前质量结论，支撑课程考查提交。",
    ]:
        add_para(doc, f"    {text}")
    add_heading(doc, "1.2 项目背景", 2)
    add_para(doc, "RhizoDelta 是 B/S 架构的图谱化非线性讨论系统，使用 Spring Boot、Neo4j、Redis、RabbitMQ、JWT、SSE 与 React/Vite 构建。系统面向非线性讨论场景，核心能力包括认证授权、个人资料与社交关系、发帖与节点关联、图谱查询、治理决策与复核、AI 摘要及实时事件。本轮课程作业聚焦可稳定复现的核心 REST 行为，并使用 Postman 作为专项测试工具。")

    add_heading(doc, "2 测试参考文档", 1)
    add_table(
        doc,
        ["文档名", "版本", "日期", "作者", "备注"],
        [
            ("《1-测试方案》", "1.0", TEST_DATE, AUTHOR, "测试范围、资源、计划和风险"),
            ("《2-测试用例》", "1.0", TEST_DATE, AUTHOR, "20 条功能/接口用例"),
            ("《3-Bug缺陷报告清单》", "1.0", TEST_DATE, AUTHOR, "2 个低危缺陷"),
            ("《4-接口测试-Postman》", "1.0", TEST_DATE, AUTHOR, "Postman 集合、环境与 newman 报告"),
            ("RhizoDelta 项目理解与测试策略文档", "1.0", TEST_DATE, AUTHOR, "系统背景、测试边界和设计方法"),
        ],
    )

    add_heading(doc, "3 项目组成员", 1)
    add_table(
        doc,
        ["角色", "人员", "主要职责"],
        [
            ("测试负责人（个人独立完成）", AUTHOR, "完成需求理解、方案编写、用例设计、Postman 集合构建、用例执行、缺陷登记、截图取证和总结报告。")
        ],
    )

    add_heading(doc, "4 测试设计介绍", 1)
    add_heading(doc, "4.1 测试用例设计方法", 2)
    method_rows = [
        ("4.1.1 错误推测法", "根据接口常见风险设计伪造 token、无 token、非法 UUID、不存在用户、重复注册等用例，用于发现鉴权、参数校验和错误处理问题。"),
        ("4.1.2 等价类划分法", "把用户名、密码、token、UUID、分页参数划分为合法类和非法类，例如合法密码与少于 8 位密码分别覆盖有效/无效等价类。"),
        ("4.1.3 边界值分析法", "围绕密码长度、空用户名、UUID 格式等边界取值设计用例，验证 GlobalExceptionHandler 与校验注解是否按预期返回错误信息。"),
        ("4.1.4 因果图法", "登录场景按用户名存在性、密码正确性、账号状态组合推导结果，覆盖正确登录、密码错误、不存在用户三个关键组合。"),
        ("4.1.5 场景法", "设计注册→登录→查询资料→刷新令牌→登出→旧 token 失效的端到端链路，验证主业务流程闭环和 token 黑名单生效。"),
    ]
    for heading, text in method_rows:
        add_heading(doc, heading, 3)
        add_para(doc, text)

    add_heading(doc, "4.2 测试环境与配置", 2)
    add_heading(doc, "4.2.1 硬件配置", 3)
    add_table(doc, ["关键项", "数量", "性能要求"], [("测试 PC 机（客户端/接口执行机）", "1", "x86_64 多核 CPU，8GB 及以上内存，20GB 可用硬盘空间")])
    add_heading(doc, "4.2.2 软件配置", 3)
    add_table(
        doc,
        ["资源名称/类型", "数量", "配置"],
        [
            ("被测后端", "1", "RhizoDelta Spring Boot，http://localhost:8090"),
            ("依赖服务", "3", "Neo4j、Redis、RabbitMQ"),
            ("浏览器", "1", "Chrome 最新版"),
            ("接口工具", "1", "Postman + newman；20 请求，58 断言"),
            ("文档与截图", "1", "Word/WPS/LibreOffice，浏览器截图，newman htmlextra 报告"),
        ],
    )
    add_heading(doc, "4.3 测试方法", 2)
    for heading, text in [
        ("4.3.1 软件审查", "审查系统说明、接口契约、统一响应包、错误码和课程模板要求，确认测试范围与提交物结构。"),
        ("4.3.2 黑盒测试", "从用户和接口调用者视角验证输入与输出，不依赖后端实现细节判断功能是否符合预期。"),
        ("4.3.3 接口自动化测试", "使用 Postman 编写 20 条接口请求和 Tests 断言，通过 newman 生成 HTML/JSON 报告。"),
    ]:
        add_heading(doc, heading, 3)
        add_para(doc, text)

    add_heading(doc, "5 测试进度", 1)
    add_heading(doc, "5.1 测试进度回顾", 2)
    add_para(doc, "本次测试由个人独立完成，2026.6.18 完成需求分析、方案、用例、执行、缺陷登记和总结。核心用例执行率 100%，测试完成度按本轮范围计为 100%。")
    add_table(
        doc,
        ["测试阶段", "时间安排", "参与人员", "测试工作内容安排"],
        [
            ("需求分析", "19:00-19:30", AUTHOR, "分析 RhizoDelta 系统背景、模块和测试边界"),
            ("测试方案", "19:30-20:00", AUTHOR, "按模板填写测试方案"),
            ("测试用例", "20:00-20:40", AUTHOR, "编写 20 条用例，覆盖认证、用户资料、图谱查询和登出收尾"),
            ("用例执行", "20:40-21:10", AUTHOR, "运行 Postman/newman，生成 HTML/JSON 报告与截图"),
            ("缺陷登记", "21:10-21:25", AUTHOR, "记录 BUG-001、BUG-002，并给出严重程度与建议"),
            ("总结提交", "21:25-21:45", AUTHOR, "汇总用例、缺陷、结论和后续建议"),
        ],
    )
    add_heading(doc, "5.2 测试进度总结", 2)
    for text in [
        "本次测试总共用时约 2.75 小时，本轮范围内所有测试用例全部执行完成。",
        "总共编写测试用例 20 个，执行 20 个，通过 20 个；其中 1 条用例记录 HTTP 语义缺陷观察。",
        "Postman/newman 共执行 20 个请求，58 条断言，通过 57 条，失败 1 条；失败断言对应 BUG-001，属于预期暴露缺陷。",
        "发现缺陷总数 2 个，严重 0 个，很高 0 个，高 0 个，中 0 个，低 2 个。",
        "完成《测试方案》《测试用例》《Bug缺陷报告清单》《接口测试-Postman》《测试总结报告》及课程考查报告。",
    ]:
        add_para(doc, f"    {text}")

    add_heading(doc, "6 用例汇总", 1)
    add_table(
        doc,
        ["功能模块", "测试用例总数", "用例编写人", "执行人"],
        [(module, count, AUTHOR, AUTHOR) for module, count in CASE_COUNTS] + [("用例合计（个）", 20, AUTHOR, AUTHOR)],
    )

    add_heading(doc, "7 缺陷分析", 1)
    add_table(
        doc,
        ["功能模块", "严重", "很高", "高", "中", "低", "合计"],
        BUG_SUMMARY,
    )
    add_para(doc, "BUG-001：重复用户名注册被正确拒绝，但 HTTP 状态码使用 400 而非 409 Conflict，属于接口契约语义问题。")
    add_para(doc, "BUG-002：在线状态接口 last_active 使用字符串型 epoch，而其它时间字段为 ISO8601，属于数据格式一致性问题。")
    add_para(doc, "两个缺陷均不阻塞主流程，但建议在后续版本统一错误码/状态码映射和时间序列化策略。")

    add_heading(doc, "8 测试结论", 1)
    for text in [
        "本轮测试范围内，认证授权、用户资料与社交、图谱查询、登出与 token 吊销等核心功能均能正常工作。",
        "系统鉴权约束有效：无 token、伪造 token、登出后旧 token 均被拒绝；登录错误提示不泄露账号是否存在，安全性设计较好。",
        "接口统一响应包整体稳定，请求/响应字段以 snake_case 为主，便于前后端对接和 Postman 断言。",
        "当前仅发现 2 个低危缺陷，不影响核心流程验收；建议修复后补充发帖异步一致性、头像上传、治理决策、SSE 冒烟和性能/回归测试。",
        "综合判断：RhizoDelta 在本轮所测核心模块上达到课程作业验收质量，可以作为软件测试技术课程的被测系统提交。",
    ]:
        add_para(doc, f"    {text}")
    doc.save(output)


def build_cases_xlsx(template_xlsx: Path, output: Path) -> None:
    shutil.copy2(template_xlsx, output)
    wb = load_workbook(output)
    for sheet in list(wb.worksheets):
        wb.remove(sheet)
    ws = wb.create_sheet("测试用例")

    rows = [
        ["模块名称", "用例个数（个）"],
        *CASE_COUNTS,
        ["合计（个）", 20],
        [],
        ["RhizoDelta 图谱化非线性讨论系统测试用例"],
        [],
        ["测试用例编号", "测试项目", "测试标题", "重要级别", "预置条件", "输入", "执行步骤", "预期输出", "实际输出", "测试结果"],
    ]
    for row in rows:
        ws.append(list(row))
    grouped: dict[str, list[tuple[str, ...]]] = {}
    for case in CASES:
        grouped.setdefault(case[1], []).append(case)
    order = ["认证授权", "用户资料与社交", "图谱查询", "认证收尾"]
    section_idx = 1
    for module in order:
        module_cases = grouped[module]
        ws.append([f"{section_idx}、{module}模块（测试用例个数：{len(module_cases)}个）"])
        for case in module_cases:
            ws.append(list(case))
        section_idx += 1

    widths = [20, 18, 28, 12, 26, 34, 42, 48, 46, 18]
    for idx, width in enumerate(widths, 1):
        ws.column_dimensions[chr(64 + idx)].width = width
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    wb.save(output)


def build_bugs_xlsx(template_xlsx: Path, output: Path) -> None:
    shutil.copy2(template_xlsx, output)
    wb = load_workbook(output)
    for sheet in list(wb.worksheets):
        wb.remove(sheet)
    ws = wb.create_sheet("Bug")

    ws.append(["模块名称", "按BUG严重程度（单位：个）", "", "", "", "", "总计（单位：个）"])
    ws.append(["", "严重", "很高", "高", "中", "低", ""])
    for row in BUG_SUMMARY:
        ws.append(list(row))
    ws.append([])
    ws.append(["RhizoDelta 图谱化非线性讨论系统缺陷报告"])
    ws.append(["缺陷编号", "模块名称", "页面/窗口", "摘要", "描述", "缺陷严重程度", "提交人", "附件说明"])
    for row in BUGS:
        ws.append(list(row))

    widths = [14, 18, 28, 38, 78, 16, 14, 42]
    for idx, width in enumerate(widths, 1):
        ws.column_dimensions[chr(64 + idx)].width = width
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    wb.save(output)


def add_image_to_cell(cell, image_path: Path, caption: str) -> None:
    if not image_path.exists():
        set_cell_text(cell, f"{caption}\n（图片文件不存在：{image_path.name}）")
        return
    p = cell.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(image_path), width=Inches(4.9))
    cap = cell.add_paragraph(caption)
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER


def build_course_report(template_docx: Path, output: Path) -> None:
    doc = Document(template_docx)
    clear_doc_body(doc)
    set_doc_defaults(doc)

    p = doc.add_paragraph("Sichuan Top Vocational College of Information Technology")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph("软件测试技术")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].bold = True
    p.runs[0].font.size = Pt(18)
    p = doc.add_paragraph("考查报告")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].bold = True
    p.runs[0].font.size = Pt(18)
    for line in [
        "姓    名： 请填写",
        "学    号： 请填写",
        "系    别： 信息工程学院",
        "专    业： 软件技术",
        "年    级： 2024 级",
        "班    级： 请填写",
        "指导教师： 请填写",
        "2026 年 6 月 18 日 至 2026 年 6 月 18 日",
    ]:
        p = doc.add_paragraph(line)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    table = doc.add_table(rows=9, cols=2)
    table.autofit = False
    for style_name in ("Table Grid", "网格型", "Table Normal"):
        try:
            table.style = style_name
            break
        except KeyError:
            continue
    labels = [
        "所 在 单 位：",
        "项目名称：",
        "项目目的：",
        "实训内容及要求：",
        "个人总结：",
        "学生签名：",
        "课程设计得分：\n\n课程设计报告：",
        "合计：",
        "指导教师签字（签章）：",
    ]
    for row, label in zip(table.rows, labels):
        row.cells[0].width = Inches(1.45)
        row.cells[1].width = Inches(5.75)
        set_cell_text(row.cells[0], label)
    set_cell_text(table.cell(0, 1), "2024 级  信息工程学院  软件技术  专业     班")
    set_cell_text(table.cell(1, 1), "基于 RhizoDelta（图谱化非线性讨论系统）的软件测试")
    set_cell_text(
        table.cell(2, 1),
        "1. 掌握软件测试的知识和方法，包括黑盒测试、等价类划分、边界值分析、错误推测、场景法、缺陷管理与接口测试。\n"
        "2. 建立以需求为依据、以用例为载体、以缺陷和质量结论为产出的测试思维模式。\n"
        "3. 针对真实可运行的 B/S 系统完成测试方案、测试用例、缺陷清单、接口测试和测试总结的完整闭环。",
    )
    cell = table.cell(3, 1)
    set_cell_text(
        cell,
        "1. 选定 RhizoDelta 作为被测系统，梳理认证授权、用户资料与社交、发帖与关联、图谱查询、治理决策与 AI 实时能力等模块。\n"
        "2. 使用原始模板副本填写《测试方案》《测试用例》《Bug缺陷报告清单》《测试总结报告》。\n"
        "3. 选择 Postman 作为专项测试工具，构建 20 条接口用例并通过 newman 生成测试报告。\n"
        "4. 本次实测执行 20 个请求、58 条断言，通过 57 条，唯一失败断言对应 BUG-001；登记 2 个低危缺陷。\n"
        "5. 自己所测项目界面截图及成果截图如下：",
    )
    for image, caption in [
        ("03_login_page.png", "图 1 登录页：JWT 认证入口，对应认证授权模块。"),
        ("04_home_graph.png", "图 2 登录后图谱讨论主界面：左侧话题流、中间讨论节点、右侧质量分布统计。"),
        ("05_profile_settings.png", "图 3 个人设置页：头像、用户名和显示名编辑，对应用户资料模块。"),
        ("01_newman_report.png", "图 4 newman 接口测试报告：20 请求、58 断言、1 个预期失败断言。"),
        ("02_api_evidence.png", "图 5 接口请求响应证据：登录、查当前用户、登出吊销和重复注册缺陷观察。"),
    ]:
        add_image_to_cell(cell, GENERATED / "images" / image, caption)
    set_cell_text(
        table.cell(4, 1),
        "本次测试从模板要求出发，围绕一个真实可运行的 B/S 系统完成了需求理解、测试计划、用例设计、接口自动化执行、缺陷登记和质量总结。通过认证、用户资料、图谱查询、登出吊销等 20 条用例，我进一步理解了黑盒测试中等价类、边界值、错误推测、因果图和场景法的组合使用方式。Postman/newman 的自动化执行让测试结果具备可复现性，也暴露出重复注册状态码和时间字段格式一致性这类接口契约问题。综合来看，RhizoDelta 核心功能稳定，鉴权和错误处理整体可靠，后续应继续补充发帖异步一致性、头像上传、治理决策、SSE 和性能测试。",
    )
    doc.save(output)


def main() -> None:
    DELIVERABLES.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="st-template-build-") as tmp:
        tmpdir = Path(tmp)
        plan_docx_template = convert_template(PLAN_TEMPLATE, tmpdir, "docx")
        summary_docx_template = convert_template(SUMMARY_TEMPLATE, tmpdir, "docx")
        report_docx_template = convert_template(REPORT_TEMPLATE, tmpdir, "docx")
        case_xlsx_template = convert_template(CASE_TEMPLATE, tmpdir, "xlsx")
        bug_xlsx_template = convert_template(BUG_TEMPLATE, tmpdir, "xlsx")

        build_plan(plan_docx_template, DELIVERABLES / "1-测试方案.docx")
        build_cases_xlsx(case_xlsx_template, DELIVERABLES / "2-测试用例.xlsx")
        build_bugs_xlsx(bug_xlsx_template, DELIVERABLES / "3-Bug缺陷报告清单.xlsx")
        build_summary(summary_docx_template, DELIVERABLES / "5-测试总结报告.docx")
        build_course_report(report_docx_template, ROOT / "《软件测试技术》考查报告.docx")

    # Create legacy-format copies for instructors who expect the original template extensions.
    run_soffice(["--convert-to", "doc", "--outdir", str(DELIVERABLES), str(DELIVERABLES / "1-测试方案.docx")])
    run_soffice(["--convert-to", "xls", "--outdir", str(DELIVERABLES), str(DELIVERABLES / "2-测试用例.xlsx")])
    run_soffice(["--convert-to", "xls", "--outdir", str(DELIVERABLES), str(DELIVERABLES / "3-Bug缺陷报告清单.xlsx")])
    run_soffice(["--convert-to", "doc", "--outdir", str(DELIVERABLES), str(DELIVERABLES / "5-测试总结报告.docx")])
    run_soffice(["--convert-to", "doc", "--outdir", str(ROOT), str(ROOT / "《软件测试技术》考查报告.docx")])


if __name__ == "__main__":
    sys.exit(main())
