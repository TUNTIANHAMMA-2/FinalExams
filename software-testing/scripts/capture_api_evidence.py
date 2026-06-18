#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对运行中的 RhizoDelta (http://localhost:8090) 实测关键接口，
把真实"请求→响应"对渲染成一张证据 HTML，供 chrome 截图作为成果截图。

用法: python3 scripts/capture_api_evidence.py
输出: generated/api-evidence.html
"""
import json
import os
import time
import urllib.request
import urllib.error

BASE = "http://localhost:8090"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "generated", "api-evidence.html")

USER = f"qa_ev_{int(time.time())}"
PWD = os.environ.get("RD_TEST_PWD", "ChangeMe123!")  # 真实测试口令通过环境变量传入，不写入仓库


def call(method, path, body=None, token=None):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


steps = []


def rec(title, method, path, status, body_in, body_out, note=""):
    steps.append({"title": title, "method": method, "path": path,
                  "status": status, "in": body_in, "out": body_out, "note": note})


# 1 注册（合法）
s, o = call("POST", "/api/auth/register", {"username": USER, "password": PWD, "display_name": "QA Tester"})
token = json.loads(o)["data"]["token"] if s == 200 else None
rec("注册成功", "POST", "/api/auth/register", s, {"username": USER, "password": PWD, "display_name": "QA Tester"}, o)

# 2 重复注册 -> BUG-001
s, o = call("POST", "/api/auth/register", {"username": USER, "password": PWD})
rec("重复用户名注册 — 缺陷 BUG-001", "POST", "/api/auth/register", s,
    {"username": USER, "password": PWD}, o,
    note="HTTP 400 / 业务码 40001；按 REST 语义应为 409 Conflict（系统已定义 40901 却未使用）")

# 3 登录成功
s, o = call("POST", "/api/auth/login", {"username": USER, "password": PWD})
token = json.loads(o)["data"]["token"]
rec("登录成功", "POST", "/api/auth/login", s, {"username": USER, "password": PWD}, o)

# 4 带 token 查当前用户
s, o = call("GET", "/api/auth/me", token=token)
rec("带 token 查当前用户", "GET", "/api/auth/me", s, None, o)

# 5 密码错误
s, o = call("POST", "/api/auth/login", {"username": USER, "password": "WrongPass99"})
rec("密码错误登录被拒", "POST", "/api/auth/login", s, {"username": USER, "password": "WrongPass99"}, o,
    note="提示与'用户不存在'一致，不泄露账号存在性")

# 6 节点 404
s, o = call("GET", "/api/nodes/00000000-0000-0000-0000-000000000000", token=token)
rec("查询不存在的节点", "GET", "/api/nodes/{uuid}", s, None, o)

# 7 登出
s, o = call("POST", "/api/auth/logout", token=token)
rec("登出", "POST", "/api/auth/logout", s, None, o)

# 8 登出后复用旧 token
s, o = call("GET", "/api/auth/me", token=token)
rec("登出后复用旧 token 被吊销", "GET", "/api/auth/me", s, None, o,
    note="token 进入黑名单，立即失效")


def pretty(x):
    if x is None:
        return "(无请求体)"
    if isinstance(x, str):
        try:
            x = json.loads(x)
        except Exception:
            return x
    return json.dumps(x, ensure_ascii=False, indent=2)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def badge(status):
    cls = "ok" if 200 <= status < 300 else ("warn" if status == 400 else "err")
    return f'<span class="badge {cls}">HTTP {status}</span>'


cards = []
for i, st in enumerate(steps, 1):
    body_in = st["in"]
    if isinstance(body_in, dict) and "password" in body_in:
        body_in = {**body_in, "password": "********"}  # 截图脱敏，不暴露测试口令
    note = f'<div class="note">{esc(st["note"])}</div>' if st["note"] else ""
    cards.append(f"""
    <div class="card">
      <div class="hd"><span class="num">{i:02d}</span> {esc(st['title'])} {badge(st['status'])}</div>
      <div class="line"><span class="m">{st['method']}</span> <span class="p">{esc(st['path'])}</span></div>
      <div class="kv">请求体</div><pre class="req">{esc(pretty(body_in))}</pre>
      <div class="kv">响应</div><pre class="res">{esc(pretty(st['out']))}</pre>
      {note}
    </div>""")

html = f"""<!doctype html><html lang="zh"><head><meta charset="utf-8">
<style>
 body{{background:#0f1117;color:#e6e6e6;font-family:'DejaVu Sans Mono',Consolas,monospace;margin:0;padding:24px}}
 h1{{font-size:22px;margin:0 0 4px}} .sub{{color:#9aa4b2;font-size:13px;margin-bottom:18px}}
 .grid{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
 .card{{background:#1a1d27;border:1px solid #2a2f3a;border-radius:8px;padding:12px 14px}}
 .hd{{font-size:14px;font-weight:bold;margin-bottom:6px}}
 .num{{color:#6ea8fe}} .line{{font-size:12px;margin:4px 0 8px}}
 .m{{color:#7ee787;font-weight:bold}} .p{{color:#d2a8ff}}
 .kv{{color:#9aa4b2;font-size:11px;margin-top:6px}}
 pre{{margin:2px 0;padding:8px;border-radius:6px;font-size:11px;white-space:pre-wrap;word-break:break-all}}
 .req{{background:#10141c}} .res{{background:#10171f}}
 .badge{{float:right;font-size:11px;padding:2px 8px;border-radius:10px}}
 .ok{{background:#1f6f43}} .warn{{background:#8a6d00}} .err{{background:#8a2b2b}}
 .note{{margin-top:8px;font-size:11px;color:#ffd479;border-left:3px solid #ffd479;padding-left:8px}}
</style></head><body>
 <h1>RhizoDelta 接口实测证据 · 软件测试成果截图</h1>
 <div class="sub">被测系统 {BASE}　|　实测时间 {time.strftime('%Y-%m-%d %H:%M')}　|　统一响应包 {{code,message,data}}　|　含缺陷 BUG-001</div>
 <div class="grid">{''.join(cards)}</div>
</body></html>"""

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print("证据页已生成:", OUT, "| 测试账号:", USER)
