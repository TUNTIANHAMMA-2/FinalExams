#!/usr/bin/env python3
"""Generate RhizoDelta course-report deliverables.

The generated reports are based on the reviewed RhizoDelta documentation and
source layout. They intentionally keep the Vue course cover/title while
describing the actual React frontend implementation, per the user's course
submission rule.
"""

from __future__ import annotations

import base64
import html
import shutil
import sys
from pathlib import Path
from typing import Iterable

sys.path.insert(0, "/tmp/finalexams-pydeps")

from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.section import WD_SECTION_START
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


ROOT = Path(__file__).resolve().parent
JAVAEE_DIR = ROOT / "javaee-web-app"
VUE_DIR = ROOT / "vuejs-app-dev"
RHIZODELTA_REPO_URL = "https://github.com/TUNTIANHAMMA-2/RhizoDelta"
RHIZODELTA_LOCAL_PATH = "/home/tthm/workspace/RhizoDelta"

FONT_PATH = Path("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc")
if not FONT_PATH.exists():
    FONT_PATH = Path("/usr/share/fonts/opentype/unifont/unifont.otf")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size)


F_TITLE = font(36)
F_H = font(26)
F = font(21)
F_S = font(18)
F_XS = font(15)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> tuple[int, int]:
    if not text:
        return (0, 0)
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def wrap(draw: ImageDraw.ImageDraw, text: str, max_width: int, fnt: ImageFont.FreeTypeFont) -> list[str]:
    lines: list[str] = []
    for raw in text.split("\n"):
        if not raw:
            lines.append("")
            continue
        current = ""
        for ch in raw:
            trial = current + ch
            if text_size(draw, trial, fnt)[0] <= max_width or not current:
                current = trial
            else:
                lines.append(current)
                current = ch
        if current:
            lines.append(current)
    return lines


def center_text(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    fnt: ImageFont.FreeTypeFont = F,
    fill: str = "#172033",
    gap: int = 5,
) -> None:
    x1, y1, x2, y2 = box
    lines = wrap(draw, text, max(1, x2 - x1 - 18), fnt)
    heights = [text_size(draw, line, fnt)[1] for line in lines]
    total_h = sum(heights) + max(0, len(lines) - 1) * gap
    y = y1 + (y2 - y1 - total_h) / 2
    for line, h in zip(lines, heights):
        w, _ = text_size(draw, line, fnt)
        draw.text((x1 + (x2 - x1 - w) / 2, y), line, font=fnt, fill=fill)
        y += h + gap


def box(
    draw: ImageDraw.ImageDraw,
    rect: tuple[int, int, int, int],
    text: str,
    fill: str = "#F8FAFC",
    outline: str = "#2F5EAA",
    fnt: ImageFont.FreeTypeFont = F,
) -> None:
    draw.rounded_rectangle(rect, radius=12, fill=fill, outline=outline, width=3)
    center_text(draw, rect, text, fnt)


def line_arrow(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    label: str = "",
    color: str = "#475467",
) -> None:
    draw.line((start, end), fill=color, width=3)
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = max((dx * dx + dy * dy) ** 0.5, 1)
    ux, uy = dx / length, dy / length
    left = (-uy, ux)
    p1 = (end[0] - ux * 16 + left[0] * 8, end[1] - uy * 16 + left[1] * 8)
    p2 = (end[0] - ux * 16 - left[0] * 8, end[1] - uy * 16 - left[1] * 8)
    draw.polygon((end, p1, p2), fill=color)
    if label:
        mx = (start[0] + end[0]) // 2
        my = (start[1] + end[1]) // 2 - 26
        w, h = text_size(draw, label, F_XS)
        draw.rounded_rectangle((mx - w // 2 - 8, my - 5, mx + w // 2 + 8, my + h + 5), radius=6, fill="white")
        draw.text((mx - w // 2, my), label, font=F_XS, fill=color)


def diagram_canvas(title: str, width: int = 1500, height: int = 900) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (width, height), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, width - 1, height - 1), outline="#D7DBE8", width=2)
    tw, _ = text_size(draw, title, F_TITLE)
    draw.text(((width - tw) // 2, 28), title, font=F_TITLE, fill="#101827")
    return img, draw


def save_diagram(img: Image.Image, out_dir: Path, name: str) -> Path:
    path = out_dir / "images" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    return path


def architecture_diagram(out_dir: Path) -> Path:
    img, draw = diagram_canvas("RhizoDelta 全栈架构与数据流")
    box(draw, (70, 180, 330, 310), "浏览器\nReact/Vite 前端", "#F0FDF4", "#2D8F6F")
    box(draw, (460, 150, 760, 340), "Spring Boot 后端\nController + Security\n统一 API 响应", "#EFF6FF", "#2F5EAA")
    box(draw, (870, 120, 1140, 250), "RabbitMQ\n异步发帖队列", "#FFF7ED", "#B45309")
    box(draw, (870, 310, 1140, 440), "PostConsumer\n落库 + Embedding\n质量评估 + AI 路由", "#F8FAFC", "#475467")
    box(draw, (1220, 110, 1450, 250), "Neo4j 5\nDAG + 语义关联\n向量索引", "#F5F3FF", "#7C3AED")
    box(draw, (1220, 330, 1450, 460), "Redis\n复核 TTL\nToken/状态辅助", "#FFF1F2", "#E11D48")
    box(draw, (460, 570, 760, 740), "SSE 事件总线\nNODE_CREATED\nEDGE_CREATED\nDECISION_*", "#ECFEFF", "#0891B2")
    box(draw, (870, 570, 1140, 740), "LangGraph4j 工作流\n召回 → 裁决 → 反思\nMERGE / BRANCH\nREVIEW", "#F0F9FF", "#0369A1")
    line_arrow(draw, (330, 245), (460, 245), "REST /api")
    line_arrow(draw, (760, 245), (870, 185), "POST /api/posts")
    line_arrow(draw, (1005, 250), (1005, 310), "consume")
    line_arrow(draw, (1140, 350), (1220, 180), "write/query")
    line_arrow(draw, (1140, 400), (1220, 395), "review TTL")
    line_arrow(draw, (1005, 440), (1005, 570), "orchestrate")
    line_arrow(draw, (870, 655), (760, 655), "events")
    line_arrow(draw, (460, 655), (330, 275), "SSE stream")
    return save_diagram(img, out_dir, "01_fullstack_architecture.png")


def graph_model_diagram(out_dir: Path) -> Path:
    img, draw = diagram_canvas("图数据模型：版本演进 DAG + 语义关联层")
    box(draw, (90, 180, 320, 300), "Human_Post\n用户原始观点", "#EFF6FF", "#2563EB")
    box(draw, (590, 160, 840, 320), "AI_Consensus\nAI 共识摘要", "#F5F3FF", "#7C3AED")
    box(draw, (1120, 180, 1370, 300), "Result\n阶段性结果", "#ECFDF5", "#059669")
    box(draw, (90, 540, 320, 660), "UserAccount\nUserProfile", "#FFF7ED", "#B45309")
    box(draw, (590, 520, 840, 680), "Topic\nPreferenceEvent", "#FEFCE8", "#CA8A04")
    box(draw, (1120, 540, 1370, 660), "语义关联边\nRELATES_TO\nCONCEPTUAL_OVERLAP", "#F8FAFC", "#475467")
    line_arrow(draw, (320, 240), (590, 240), "SYNTHESIZED_FROM / MERGED_INTO")
    line_arrow(draw, (840, 240), (1120, 240), "MATERIALIZED_FROM / JOIN")
    line_arrow(draw, (210, 540), (210, 300), "AUTHORED")
    line_arrow(draw, (320, 600), (590, 600), "FOLLOWS / MUTED / PREFERS")
    line_arrow(draw, (1120, 600), (840, 280), "语义层不参与拓扑排序")
    line_arrow(draw, (590, 280), (320, 280), "BRANCHED_FROM / CONTINUES_FROM")
    center_text(
        draw,
        (420, 720, 1080, 820),
        "核心原则：历史节点默认不可变；修订、合并、分叉均通过新增节点和显式关系边表达。",
        F,
        "#334155",
    )
    return save_diagram(img, out_dir, "02_graph_data_model.png")


def frontend_diagram(out_dir: Path) -> Path:
    img, draw = diagram_canvas("前端模块结构与运行链路")
    box(draw, (80, 160, 350, 290), "App.tsx\nReact Router 7\nRequireAuth", "#EFF6FF", "#2563EB")
    box(draw, (520, 120, 800, 250), "页面组件\nLogin / Home\nWorkspace / Settings", "#F0FDF4", "#16A34A")
    box(draw, (520, 340, 800, 500), "GraphWorkspace\nDesktopGraphWorkspace\nMobileDiscussionTreeView", "#F5F3FF", "#7C3AED")
    box(draw, (950, 120, 1220, 280), "Zustand Stores\nauth / graph / home\nsse / ui / tree", "#FFF7ED", "#B45309")
    box(draw, (950, 380, 1220, 520), "API 封装\nclient.ts\nnodes/posts/auth/events", "#ECFEFF", "#0891B2")
    box(draw, (1260, 250, 1460, 390), "Spring Boot API\n/api/**\nSSE stream", "#F8FAFC", "#475467")
    line_arrow(draw, (350, 225), (520, 185), "route")
    line_arrow(draw, (350, 225), (520, 420), "route")
    line_arrow(draw, (800, 185), (950, 200), "state")
    line_arrow(draw, (800, 420), (950, 200), "state")
    line_arrow(draw, (1085, 280), (1085, 380), "actions")
    line_arrow(draw, (1220, 450), (1260, 330), "fetch")
    line_arrow(draw, (1260, 295), (1220, 200), "events")
    center_text(
        draw,
        (200, 650, 1300, 780),
        "桌面端使用 React Flow 展示 Lineage / Explore 图谱；移动端使用 discussion-tree API 展示嵌套阅读视图，避免在小屏挂载复杂画布。",
        F,
        "#334155",
    )
    return save_diagram(img, out_dir, "03_frontend_architecture.png")


def backend_flow_diagram(out_dir: Path) -> Path:
    img, draw = diagram_canvas("后端发帖与 AI 编排时序")
    steps = [
        ("1. 用户提交帖子", "#EFF6FF", "#2563EB"),
        ("2. JWT 鉴权\n参数校验", "#F0FDF4", "#16A34A"),
        ("3. RabbitMQ 入队\n返回 202", "#FFF7ED", "#B45309"),
        ("4. PostConsumer\n创建 Human_Post", "#F8FAFC", "#475467"),
        ("5. Embedding\n质量评估", "#F5F3FF", "#7C3AED"),
        ("6. AI 路由\nMERGE / BRANCH\nREVIEW", "#ECFEFF", "#0891B2"),
        ("7. Neo4j 写入\n关系边和审计", "#FEFCE8", "#CA8A04"),
        ("8. SSE 推送\n前端增量刷新", "#FFF1F2", "#E11D48"),
    ]
    positions = [
        (90, 190, 340, 320),
        (440, 190, 690, 320),
        (790, 190, 1040, 320),
        (1140, 190, 1390, 320),
        (1140, 480, 1390, 610),
        (790, 480, 1040, 610),
        (440, 480, 690, 610),
        (90, 480, 340, 610),
    ]
    for i, ((text, fill, outline), rect) in enumerate(zip(steps, positions)):
        box(draw, rect, text, fill, outline, F_S)
        if i < len(steps) - 1:
            x1, y1, x2, y2 = rect
            nx1, ny1, nx2, ny2 = positions[i + 1]
            if i == 3:
                line_arrow(draw, ((x1 + x2) // 2, y2), ((nx1 + nx2) // 2, ny1))
            elif i < 3:
                line_arrow(draw, (x2, (y1 + y2) // 2), (nx1, (ny1 + ny2) // 2))
            else:
                line_arrow(draw, (x1, (y1 + y2) // 2), (nx2, (ny1 + ny2) // 2))
    center_text(
        draw,
        (180, 690, 1320, 810),
        "这个链路把 HTTP 请求线程、消息队列、图数据库写入、LLM 调用和前端实时反馈解耦，适合课程报告中说明 JavaEE 企业级应用的分层、异步和安全设计。",
        F,
        "#334155",
    )
    return save_diagram(img, out_dir, "04_backend_async_flow.png")


def set_cell_text(cell, text: str, bold: bool = False) -> None:
    cell.text = ""
    p = cell.paragraphs[0]
    r = p.add_run(text)
    r.bold = bold
    r.font.name = "宋体"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    r.font.size = Pt(10.5)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def set_doc_defaults(doc: Document) -> None:
    styles = doc.styles
    styles["Normal"].font.name = "宋体"
    styles["Normal"]._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    styles["Normal"].font.size = Pt(10.5)
    for name in ["Heading 1", "Heading 2", "Heading 3"]:
        style = styles[name]
        style.font.name = "黑体"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")


def add_page_number(section) -> None:
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    fld_char = OxmlElement("w:fldChar")
    fld_char.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char)
    run._r.append(instr)
    run._r.append(fld_char2)


def add_cover(doc: Document, course: str, title: str, subtitle: str) -> None:
    sec = doc.sections[0]
    sec.top_margin = Cm(2.4)
    sec.bottom_margin = Cm(2.2)
    sec.left_margin = Cm(2.4)
    sec.right_margin = Cm(2.4)

    for _ in range(3):
        doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(course)
    r.bold = True
    r.font.name = "黑体"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
    r.font.size = Pt(22)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(title)
    r.bold = True
    r.font.name = "黑体"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
    r.font.size = Pt(20)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(subtitle)
    r.font.name = "宋体"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    r.font.size = Pt(13)

    for _ in range(6):
        doc.add_paragraph()

    table = doc.add_table(rows=6, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    fields = [
        ("项目名称", "RhizoDelta 图谱化非线性讨论系统"),
        ("学生姓名", "（请填写）"),
        ("学号", "（请填写）"),
        ("班级", "（请填写）"),
        ("指导教师", "（请填写）"),
        ("完成时间", "2026 年 5 月"),
    ]
    for row, (k, v) in zip(table.rows, fields):
        set_cell_text(row.cells[0], k, True)
        set_cell_text(row.cells[1], v)

    doc.add_page_break()


def add_toc(doc: Document) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("目  录")
    r.bold = True
    r.font.name = "黑体"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
    r.font.size = Pt(16)
    doc.add_paragraph("（提交前可在 Word/WPS 中右键更新目录域。）")
    p = doc.add_paragraph()
    run = p.add_run()
    fld_char = OxmlElement("w:fldChar")
    fld_char.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = r'TOC \o "1-3" \h \z \u'
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "separate")
    fld_char3 = OxmlElement("w:fldChar")
    fld_char3.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char)
    run._r.append(instr)
    run._r.append(fld_char2)
    run._r.append(fld_char3)
    doc.add_page_break()


def para(doc: Document, text: str) -> None:
    p = doc.add_paragraph(text)
    p.paragraph_format.first_line_indent = Pt(21)
    p.paragraph_format.line_spacing = 1.35


def bullet(doc: Document, text: str) -> None:
    p = doc.add_paragraph(style="List Bullet")
    p.add_run(text)


def add_table(doc: Document, headers: list[str], rows: list[list[str]]) -> None:
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for idx, header in enumerate(headers):
        set_cell_text(table.rows[0].cells[idx], header, True)
    for row_values in rows:
        row = table.add_row()
        for idx, value in enumerate(row_values):
            set_cell_text(row.cells[idx], value)


def add_image(doc: Document, path: Path, caption: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(str(path), width=Cm(15.5))
    c = doc.add_paragraph(caption)
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER


def javaee_markdown(diagrams: dict[str, Path]) -> str:
    img = lambda key: f"images/{diagrams[key].name}"
    return f"""# 《JavaEE企业级Web应用开发实战》期末课程设计报告

项目名称：RhizoDelta 图谱化非线性讨论系统

代码仓库：{RHIZODELTA_REPO_URL}

本地开发目录：`{RHIZODELTA_LOCAL_PATH}`

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

![全栈架构]({img('architecture')})

系统采用分层架构：`api` 层负责 HTTP 输入输出，`service` 层承载业务规则，`repository` 和 `Neo4jClient` 承担图数据库访问，`infrastructure` 包统一放置安全、消息、SSE、持久化初始化和可观测性能力。

## 五、数据模型与图数据库设计

![图数据模型]({img('graph')})

核心节点包括 `Human_Post`、`AI_Consensus`、`Result`、`UserAccount`、`UserProfile`、`Topic` 和 `PreferenceEvent`。版本演进关系包括 `BRANCHED_FROM`、`MERGED_INTO`、`SYNTHESIZED_FROM`、`CONTINUES_FROM`、`CONVERGED_FROM`、`MATERIALIZED_FROM`、`CROSS_SYNTHESIZED_FROM`。语义关联关系包括 `CONCEPTUAL_OVERLAP` 和 `RELATES_TO`。用户域关系包括 `AUTHORED`、`HAS_PROFILE`、`FOLLOWS`、`MUTED`、`PREFERS`。

## 六、后端功能实现

### 6.1 认证与权限

`SecurityConfig` 关闭 CSRF，使用无状态会话，并把 `JwtAuthenticationFilter` 放入 Spring Security 过滤链。公开接口包括登录、注册、刷新 token、健康检查和头像读取；写入决策、创建语义关联、复核和回滚接口按 `USER`、`AGENT`、`ADMIN` 角色区分权限。

### 6.2 发帖异步处理

`PostController` 负责校验请求、绑定认证用户、检查目标节点、生成稳定 `event_id`，再把 `PostEventMessage` 投递到 RabbitMQ。HTTP 层等待 publisher confirm，消息确认后返回 `202 Accepted`。`PostConsumer` 消费消息后创建 `Human_Post`，异步生成 embedding、质量评分，发布 `NODE_CREATED` 和 `EDGE_CREATED` 事件，并触发 AI 路由编排。

![后端时序]({img('flow')})

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
"""


def vue_markdown(diagrams: dict[str, Path]) -> str:
    img = lambda key: f"images/{diagrams[key].name}"
    return f"""# 《Vue.js应用开发》期末课程设计报告

项目名称：RhizoDelta 图谱化非线性讨论系统前端

说明：按课程提交要求，本报告保留 Vue.js 课程封面与文件名；正文依据实际项目填写。实际前端技术栈为 React 19 + TypeScript + Vite。

代码仓库：{RHIZODELTA_REPO_URL}

本地开发目录：`{RHIZODELTA_LOCAL_PATH}/frontend`

## 一、项目概述

RhizoDelta 前端是一个图谱化讨论系统的交互界面。用户可以登录或注册，浏览根话题，进入图谱工作区查看观点的演进关系，发布新话题，对节点执行延续注入或分叉，并通过右侧详情面板查看溯源、关联和审计信息。桌面端使用 React Flow 展示 DAG 图谱，移动端使用嵌套讨论树降低复杂图形渲染成本。

## 二、需求分析

- 提供登录、注册和受保护路由。
- 首页展示根话题、信息流和右侧辅助信息。
- 工作区支持桌面图谱模式和移动端讨论树模式。
- 节点可查看详情、确权溯源、语义关联和审计时间线。
- 用户可以发布新话题、回复节点、执行延续注入和分叉。
- 前端需要监听 SSE，实时处理节点创建、边创建、决策完成、质量评分等事件。
- UI 需要适配桌面和移动端，保证大规模图谱场景下的交互可用性。

## 三、技术栈与开发环境

| 类别 | 技术 |
|---|---|
| UI 框架 | React 19 |
| 类型系统 | TypeScript 5.x |
| 构建工具 | Vite 8 |
| 路由 | React Router 7 |
| 图谱画布 | @xyflow/react, @dagrejs/dagre, d3-force |
| 状态管理 | Zustand 5 |
| 编辑器 | TipTap 3 + Markdown |
| 样式 | Tailwind CSS 4, CSS Design Tokens |
| 测试 | Vitest, Testing Library |

## 四、前端总体架构

![前端架构]({img('frontend')})

前端入口为 `src/main.tsx` 和 `src/App.tsx`。`App.tsx` 管理路由和鉴权保护：`/login` 是公开路由，`/`、`/workspace`、`/workspace/:rhizomeId`、`/settings` 都需要有效 token。`GraphWorkspace` 根据视口宽度选择桌面图谱工作区或移动端讨论树。

## 五、页面与组件设计

### 5.1 登录/注册页

`LoginPage.tsx` 调用 `/api/auth/login` 和 `/api/auth/register`，成功后把 access token 写入 `localStorage.jwt_token`，并交给 `authStore` 维护用户身份、角色和会话状态。

### 5.2 首页

首页由 `HomePage` 及 `HomeSidebar`、`HomeMainColumn`、`HomeRightRail` 等组件组成，用于展示根话题、动态信息和个人化入口。

### 5.3 工作区

桌面端 `DesktopGraphWorkspace` 组合左侧话题列表、中间 React Flow 画布和右侧详情面板。画布支持版本视图和探索视图，节点点击后可打开 `NodeDetailPanel`，工具条可触发注入和分叉操作。

### 5.4 移动端讨论树

移动端不直接挂载复杂图谱画布，而是请求 `/api/nodes/{{id}}/discussion-tree`，由 `MobileDiscussionTreeView`、`CommentTreeItem`、`MobileReplyComposer` 和 `LongPressMenu` 展示更适合小屏阅读的嵌套讨论结构。

## 六、API 封装与状态管理

`src/api/client.ts` 是统一请求入口，自动附加 `Authorization: Bearer <token>`，并处理统一响应结构 `{{code, message, data}}`。领域 API 被拆分为 `auth.ts`、`nodes.ts`、`posts.ts`、`decisions.ts`、`associations.ts`、`audit.ts`、`profile.ts`、`feed.ts`、`events.ts` 等。

Zustand Store 按职责拆分：`authStore` 管理登录状态，`graphStore` 管理节点、边、选择态和图谱视图，`sseStore` 管理连接状态，`homeStore` 管理首页数据，`discussionTreeStore` 管理移动端讨论树，`uiStore` 管理侧边栏、右面板和 toast。

## 七、实时更新与交互流程

前端通过 `useSse.ts` 请求 `/api/events/stream`。连接建立后解析 SSE 文本块，并根据事件类型更新 store：

- `NODE_CREATED`：拉取新节点并加入图谱。
- `EDGE_CREATED`：补齐端点节点后加入关系边。
- `DECISION_COMPLETE`：替换乐观节点并展示结果。
- `ORCHESTRATION_STATUS`：更新编排状态。
- `SUMMARY_GENERATED`、`QUALITY_SCORED`：刷新摘要和质量徽章。

![全栈数据流]({img('architecture')})

## 八、界面风格与响应式设计

项目采用 Botanical Observatory / Wikipedia-Notion 风格：暖纸色背景、植物学绿色强调色、内容区衬线字体、控件区无衬线字体。核心 design token 位于 `src/styles/tokens.css`。界面在桌面端提供三栏工作台，在移动端切换为讨论树和轻量操作菜单。

## 九、运行、构建与测试

前端运行命令：

```bash
cd frontend
npm install
npm run dev
```

构建命令：

```bash
npm run build
```

Lint 与测试：

```bash
npm run lint
npx vitest
```

当前前端包含 118 个 TypeScript/CSS 源文件和多组测试文件，覆盖表单、节点操作、移动端组件、Markdown 工具、SSE 事件、viewport hook 和 Zustand store。

## 十、总结

本项目前端重点解决了图谱型应用中“数据结构复杂、实时事件多、桌面与移动体验差异大”的问题。通过 API 分层、Zustand 状态拆分、React Flow 图谱渲染、SSE 增量更新和移动端讨论树降级方案，系统形成了较完整的前端工程实践。虽然课程名称为 Vue.js 应用开发，本报告正文按照学校允许的实际项目内容填写，保留课程封面和文件名要求。
"""


def add_javaee_content(doc: Document, diagrams: dict[str, Path]) -> None:
    doc.add_heading("一、项目概述", 1)
    para(doc, "RhizoDelta 是一个基于图谱的非线性讨论系统。它把传统论坛中的线性聊天记录组织为“共识主干 + 异议分支”的知识图谱：用户提交观点后，后端通过 Spring Boot 接收请求，RabbitMQ 解耦异步处理，Neo4j 保存不可变 DAG，AI 编排层对内容进行召回、裁决、反思和落库，前端通过 SSE 接收增量事件并刷新图谱视图。")
    para(doc, f"代码仓库为 {RHIZODELTA_REPO_URL}，本地开发目录为 {RHIZODELTA_LOCAL_PATH}。")

    doc.add_heading("二、需求分析", 1)
    for item in [
        "用户可以注册、登录，并通过 JWT 访问受保护接口。",
        "用户可以发布新话题或回复已有节点，系统返回 202 Accepted，后台异步写入图谱。",
        "系统需要支持节点详情、谱系 lineage、后代 children、溯源 provenance、移动端 discussion-tree 等查询。",
        "管理或 Agent 角色可以执行合并、分支、注入、物化、回滚、语义关联等治理操作。",
        "系统需要保证历史节点不可变，所有演进通过新增节点和关系边表达。",
        "后端需要提供 SSE，让前端实时接收节点创建、边创建、决策完成、质量评分等事件。",
    ]:
        bullet(doc, item)

    doc.add_heading("三、技术选型与开发环境", 1)
    add_table(doc, ["层次", "技术"], [
        ["后端语言与框架", "Java 17, Spring Boot 3.2.3"],
        ["数据访问", "Spring Data Neo4j, Neo4jClient"],
        ["数据库", "Neo4j 5.22"],
        ["消息队列", "RabbitMQ 3-management"],
        ["缓存/复核", "Redis 7"],
        ["鉴权", "Spring Security, JWT, BCrypt"],
        ["AI 编排", "LangChain4j 0.36.2, LangGraph4j 1.8.10"],
        ["监控", "Spring Boot Actuator, Micrometer, Prometheus, Grafana"],
        ["构建", "Maven"],
    ])

    doc.add_heading("四、系统总体设计", 1)
    add_image(doc, diagrams["architecture"], "图 1 RhizoDelta 全栈架构与数据流")
    para(doc, "系统采用分层架构：api 层负责 HTTP 输入输出，service 层承载业务规则，repository 和 Neo4jClient 承担图数据库访问，infrastructure 包统一放置安全、消息、SSE、持久化初始化和可观测性能力。")

    doc.add_heading("五、数据模型与图数据库设计", 1)
    add_image(doc, diagrams["graph"], "图 2 图数据模型")
    para(doc, "核心节点包括 Human_Post、AI_Consensus、Result、UserAccount、UserProfile、Topic 和 PreferenceEvent。版本演进关系包括 BRANCHED_FROM、MERGED_INTO、SYNTHESIZED_FROM、CONTINUES_FROM、CONVERGED_FROM、MATERIALIZED_FROM、CROSS_SYNTHESIZED_FROM。语义关联关系包括 CONCEPTUAL_OVERLAP 和 RELATES_TO。用户域关系包括 AUTHORED、HAS_PROFILE、FOLLOWS、MUTED、PREFERS。")

    doc.add_heading("六、后端功能实现", 1)
    doc.add_heading("6.1 认证与权限", 2)
    para(doc, "SecurityConfig 关闭 CSRF，使用无状态会话，并把 JwtAuthenticationFilter 放入 Spring Security 过滤链。公开接口包括登录、注册、刷新 token、健康检查和头像读取；写入决策、创建语义关联、复核和回滚接口按 USER、AGENT、ADMIN 角色区分权限。")
    doc.add_heading("6.2 发帖异步处理", 2)
    para(doc, "PostController 负责校验请求、绑定认证用户、检查目标节点、生成稳定 event_id，投递 PostEventMessage 到 RabbitMQ。HTTP 层等待 publisher confirm，消息确认后返回 202 Accepted。PostConsumer 消费消息后创建 Human_Post，异步生成 embedding、质量评分，发布 NODE_CREATED 和 EDGE_CREATED 事件，并触发 AI 路由编排。")
    add_image(doc, diagrams["flow"], "图 3 后端发帖与 AI 编排时序")
    doc.add_heading("6.3 图谱查询", 2)
    para(doc, "NodeQueryController 提供只读查询：根话题、节点详情、lineage、children、topology-context、discussion-tree、provenance 和 associations。这些接口把图数据库中的节点和关系转换为前端可直接渲染的 DTO。")
    doc.add_heading("6.4 AI 编排与治理", 2)
    para(doc, "AiRoutingWorkflowService 使用 LangGraph4j 定义状态图：加载帖子、确保 embedding、向量召回、上下文裁剪、规则预过滤、LLM 裁决、反思校验、提交前守卫、执行合并/分支或创建复核任务。规则层可以在高相似或低相似场景跳过 LLM，从而降低延迟和成本。")
    doc.add_heading("6.5 实时推送", 2)
    para(doc, "EventController 暴露 /api/events/stream，通过 SseEventService 为当前用户注册 SseEmitter。后端在发帖排队、节点创建、边创建、决策完成、摘要生成和质量评分时发布事件，前端据此做增量刷新。")

    doc.add_heading("七、部署与运行", 1)
    para(doc, "本地运行需要 JDK 17、Maven、Node.js、npm、Docker Compose 和可用的 DASHSCOPE_API_KEY。后端默认端口为 8090，前端开发端口为 5173，Vite 会把 /api 代理到 http://localhost:8090。")
    add_table(doc, ["步骤", "命令"], [
        ["启动基础设施", "docker compose up -d neo4j rabbitmq redis"],
        ["设置模型密钥", "export DASHSCOPE_API_KEY=your_api_key_here"],
        ["启动后端", "mvn spring-boot:run"],
        ["启动前端", "cd frontend && npm install && npm run dev"],
    ])

    doc.add_heading("八、测试与质量保障", 1)
    para(doc, "后端测试使用 JUnit 5、Spring Boot Test 和 Testcontainers。当前仓库包含 92 个 Java 测试文件，覆盖认证、发帖、决策、图查询、SSE、用户画像、偏好聚合、AI 路由、数据库初始化等模块。常用验证命令为 mvn test -Dspring.profiles.active=test。")

    doc.add_heading("九、总结", 1)
    para(doc, "本项目从 JavaEE 企业级 Web 应用的角度，体现了分层架构、REST API、Spring Security 鉴权、异步消息、图数据库建模、实时事件推送、自动化测试和可观测性等综合能力。项目难点不在单表 CRUD，而在如何把非线性讨论、不可变历史、AI 编排和前端实时反馈组合成一个可运行的工程系统。")


def add_vue_content(doc: Document, diagrams: dict[str, Path]) -> None:
    doc.add_heading("一、项目概述", 1)
    para(doc, "按课程提交要求，本报告保留 Vue.js 课程封面与文件名；正文依据实际项目填写。实际前端技术栈为 React 19 + TypeScript + Vite。RhizoDelta 前端是一个图谱化讨论系统的交互界面。用户可以登录或注册，浏览根话题，进入图谱工作区查看观点的演进关系，发布新话题，对节点执行延续注入或分叉，并通过右侧详情面板查看溯源、关联和审计信息。")
    para(doc, f"代码仓库为 {RHIZODELTA_REPO_URL}，前端目录为 {RHIZODELTA_LOCAL_PATH}/frontend。")

    doc.add_heading("二、需求分析", 1)
    for item in [
        "提供登录、注册和受保护路由。",
        "首页展示根话题、信息流和右侧辅助信息。",
        "工作区支持桌面图谱模式和移动端讨论树模式。",
        "节点可查看详情、确权溯源、语义关联和审计时间线。",
        "用户可以发布新话题、回复节点、执行延续注入和分叉。",
        "前端需要监听 SSE，实时处理节点创建、边创建、决策完成、质量评分等事件。",
        "UI 需要适配桌面和移动端，保证大规模图谱场景下的交互可用性。",
    ]:
        bullet(doc, item)

    doc.add_heading("三、技术栈与开发环境", 1)
    add_table(doc, ["类别", "技术"], [
        ["UI 框架", "React 19"],
        ["类型系统", "TypeScript 5.x"],
        ["构建工具", "Vite 8"],
        ["路由", "React Router 7"],
        ["图谱画布", "@xyflow/react, @dagrejs/dagre, d3-force"],
        ["状态管理", "Zustand 5"],
        ["编辑器", "TipTap 3 + Markdown"],
        ["样式", "Tailwind CSS 4, CSS Design Tokens"],
        ["测试", "Vitest, Testing Library"],
    ])

    doc.add_heading("四、前端总体架构", 1)
    add_image(doc, diagrams["frontend"], "图 1 前端模块结构与运行链路")
    para(doc, "前端入口为 src/main.tsx 和 src/App.tsx。App.tsx 管理路由和鉴权保护：/login 是公开路由，/、/workspace、/workspace/:rhizomeId、/settings 都需要有效 token。GraphWorkspace 根据视口宽度选择桌面图谱工作区或移动端讨论树。")

    doc.add_heading("五、页面与组件设计", 1)
    doc.add_heading("5.1 登录/注册页", 2)
    para(doc, "LoginPage.tsx 调用 /api/auth/login 和 /api/auth/register，成功后把 access token 写入 localStorage.jwt_token，并交给 authStore 维护用户身份、角色和会话状态。")
    doc.add_heading("5.2 首页", 2)
    para(doc, "首页由 HomePage 及 HomeSidebar、HomeMainColumn、HomeRightRail 等组件组成，用于展示根话题、动态信息和个人化入口。")
    doc.add_heading("5.3 工作区", 2)
    para(doc, "桌面端 DesktopGraphWorkspace 组合左侧话题列表、中间 React Flow 画布和右侧详情面板。画布支持版本视图和探索视图，节点点击后可打开 NodeDetailPanel，工具条可触发注入和分叉操作。")
    doc.add_heading("5.4 移动端讨论树", 2)
    para(doc, "移动端不直接挂载复杂图谱画布，而是请求 /api/nodes/{id}/discussion-tree，由 MobileDiscussionTreeView、CommentTreeItem、MobileReplyComposer 和 LongPressMenu 展示更适合小屏阅读的嵌套讨论结构。")

    doc.add_heading("六、API 封装与状态管理", 1)
    para(doc, "src/api/client.ts 是统一请求入口，自动附加 Authorization: Bearer <token>，并处理统一响应结构 {code, message, data}。领域 API 被拆分为 auth.ts、nodes.ts、posts.ts、decisions.ts、associations.ts、audit.ts、profile.ts、feed.ts、events.ts 等。")
    para(doc, "Zustand Store 按职责拆分：authStore 管理登录状态，graphStore 管理节点、边、选择态和图谱视图，sseStore 管理连接状态，homeStore 管理首页数据，discussionTreeStore 管理移动端讨论树，uiStore 管理侧边栏、右面板和 toast。")

    doc.add_heading("七、实时更新与交互流程", 1)
    para(doc, "前端通过 useSse.ts 请求 /api/events/stream。连接建立后解析 SSE 文本块，并根据事件类型更新 store：NODE_CREATED 拉取新节点并加入图谱；EDGE_CREATED 补齐端点节点后加入关系边；DECISION_COMPLETE 替换乐观节点并展示结果；ORCHESTRATION_STATUS 更新编排状态；SUMMARY_GENERATED、QUALITY_SCORED 刷新摘要和质量徽章。")
    add_image(doc, diagrams["architecture"], "图 2 全栈数据流与 SSE 实时更新")

    doc.add_heading("八、界面风格与响应式设计", 1)
    para(doc, "项目采用 Botanical Observatory / Wikipedia-Notion 风格：暖纸色背景、植物学绿色强调色、内容区衬线字体、控件区无衬线字体。核心 design token 位于 src/styles/tokens.css。界面在桌面端提供三栏工作台，在移动端切换为讨论树和轻量操作菜单。")

    doc.add_heading("九、运行、构建与测试", 1)
    add_table(doc, ["用途", "命令"], [
        ["安装依赖", "cd frontend && npm install"],
        ["开发运行", "npm run dev"],
        ["生产构建", "npm run build"],
        ["代码检查", "npm run lint"],
        ["单元测试", "npx vitest"],
    ])
    para(doc, "当前前端包含 118 个 TypeScript/CSS 源文件和多组测试文件，覆盖表单、节点操作、移动端组件、Markdown 工具、SSE 事件、viewport hook 和 Zustand store。")

    doc.add_heading("十、总结", 1)
    para(doc, "本项目前端重点解决了图谱型应用中“数据结构复杂、实时事件多、桌面与移动体验差异大”的问题。通过 API 分层、Zustand 状态拆分、React Flow 图谱渲染、SSE 增量更新和移动端讨论树降级方案，系统形成了较完整的前端工程实践。虽然课程名称为 Vue.js 应用开发，本报告正文按照学校允许的实际项目内容填写，保留课程封面和文件名要求。")


def html_doc(title: str, markdown_body: str, image_paths: Iterable[Path]) -> str:
    image_map = {}
    for path in image_paths:
        data_uri = "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")
        image_map[path.as_posix()] = data_uri
        image_map[path.name] = data_uri
        image_map[f"images/{path.name}"] = data_uri

    lines = []
    for raw in markdown_body.splitlines():
        line = raw.strip()
        if not line:
            lines.append("")
            continue
        if line.startswith("# "):
            lines.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            lines.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("### "):
            lines.append(f"<h3>{html.escape(line[4:])}</h3>")
        elif line.startswith("- "):
            lines.append(f"<p>• {html.escape(line[2:])}</p>")
        elif line.startswith("![") and "](" in line and line.endswith(")"):
            alt = line[2:line.find("]")]
            src = line[line.find("(") + 1:-1]
            data = image_map.get(src, src)
            lines.append(f'<p style="text-align:center"><img alt="{html.escape(alt)}" src="{data}" style="max-width:680px;width:100%"></p>')
        elif line.startswith("|"):
            lines.append(f"<p>{html.escape(line)}</p>")
        elif line.startswith("```"):
            lines.append("<hr>")
        else:
            lines.append(f"<p>{html.escape(line)}</p>")

    return """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
body {{ font-family: SimSun, serif; font-size: 14px; line-height: 1.65; }}
h1 {{ text-align: center; font-family: SimHei, sans-serif; }}
h2, h3 {{ font-family: SimHei, sans-serif; }}
p {{ text-indent: 2em; }}
img {{ border: 1px solid #ddd; }}
</style>
</head>
<body>
{body}
</body>
</html>
""".format(title=html.escape(title), body="\n".join(lines))


def build_report(
    out_dir: Path,
    course: str,
    doc_title: str,
    subtitle: str,
    markdown: str,
    image_paths: list[Path],
    content_builder,
    basename: str,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "generated").mkdir(exist_ok=True)

    md_path = out_dir / f"{basename}.md"
    docx_path = out_dir / f"{basename}.docx"
    doc_path = out_dir / f"{basename}.doc"
    html_path = out_dir / "generated" / f"{basename}.html"

    md_path.write_text(markdown, encoding="utf-8")

    doc = Document()
    set_doc_defaults(doc)
    add_cover(doc, course, doc_title, subtitle)
    add_toc(doc)
    content_builder(doc)
    for section in doc.sections:
        add_page_number(section)
    doc.save(docx_path)

    html_content = html_doc(doc_title, markdown, image_paths)
    html_path.write_text(html_content, encoding="utf-8")
    doc_path.write_text(html_content, encoding="utf-8")


def write_readme() -> None:
    readme = """# RhizoDelta 课程交付物

本目录下的两门课程报告均基于 RhizoDelta 当前代码与已 review 的项目文档生成。

- `javaee-web-app/`：JavaEE 企业级 Web 应用开发实战报告，侧重 Spring Boot 后端、Neo4j、RabbitMQ、JWT、SSE 和 AI 编排。
- `vuejs-app-dev/`：Vue.js 应用开发课程封面与文件名保留 Vue；正文按学校允许的实际项目内容填写，侧重 React/Vite 前端工程。

注意：报告中的个人姓名、学号、班级、指导教师保留为“请填写”，提交前需要在 Word/WPS 中替换。
"""
    (ROOT / "RhizoDelta课程交付物说明.md").write_text(readme, encoding="utf-8")


def main() -> None:
    JAVAEE_DIR.mkdir(exist_ok=True)
    VUE_DIR.mkdir(exist_ok=True)
    for course_dir in [JAVAEE_DIR, VUE_DIR]:
        (course_dir / "images").mkdir(exist_ok=True)

    shared_dir = Path("/tmp/finalexams-rhizodelta-report-assets")
    if shared_dir.exists():
        shutil.rmtree(shared_dir)
    (shared_dir / "images").mkdir(parents=True, exist_ok=True)

    diagrams = {
        "architecture": architecture_diagram(shared_dir),
        "graph": graph_model_diagram(shared_dir),
        "frontend": frontend_diagram(shared_dir),
        "flow": backend_flow_diagram(shared_dir),
    }

    # Copy diagrams into each course folder so markdown links remain local.
    java_diagrams = {}
    vue_diagrams = {}
    for key, path in diagrams.items():
        jpath = JAVAEE_DIR / "images" / path.name
        vpath = VUE_DIR / "images" / path.name
        shutil.copyfile(path, jpath)
        shutil.copyfile(path, vpath)
        java_diagrams[key] = jpath
        vue_diagrams[key] = vpath

    java_md = javaee_markdown(java_diagrams)
    vue_md = vue_markdown(vue_diagrams)

    java_basename = "JavaEE企业级Web应用开发实战期末课程设计报告"
    vue_basename = "Vue.js应用开发期末课程设计报告"

    build_report(
        JAVAEE_DIR,
        "《JavaEE企业级Web应用开发实战》",
        "期末课程设计报告",
        "RhizoDelta 图谱化非线性讨论系统后端实现",
        java_md,
        list(java_diagrams.values()),
        lambda doc: add_javaee_content(doc, java_diagrams),
        java_basename,
    )
    build_report(
        VUE_DIR,
        "《Vue.js应用开发》",
        "期末课程设计报告",
        "RhizoDelta 图谱化非线性讨论系统前端实现",
        vue_md,
        list(vue_diagrams.values()),
        lambda doc: add_vue_content(doc, vue_diagrams),
        vue_basename,
    )
    write_readme()
    print("Generated RhizoDelta course reports.")


if __name__ == "__main__":
    main()
