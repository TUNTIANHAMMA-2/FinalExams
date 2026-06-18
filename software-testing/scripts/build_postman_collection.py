#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 RhizoDelta 接口测试的 Postman 集合与环境文件。

用法:
    python3 scripts/build_postman_collection.py
输出:
    deliverables/postman/RhizoDelta.postman_collection.json
    deliverables/postman/RhizoDelta.local.postman_environment.json

随后用 newman 执行:
    npx --yes newman run deliverables/postman/RhizoDelta.postman_collection.json \\
        -e deliverables/postman/RhizoDelta.local.postman_environment.json -r cli,json

端点与断言均依据对运行中实例 (http://localhost:8090) 的实测结果编写。
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_DIR = os.path.join(ROOT, "deliverables", "postman")
os.makedirs(OUT_DIR, exist_ok=True)


def req(name, method, path, *, body=None, auth="bearer", headers=None, tests=None, prereq=None):
    """构造一个 Postman 请求条目。auth: bearer|none|fake"""
    item = {"name": name, "event": [], "request": {}}
    if prereq:
        item["event"].append({"listen": "prerequest",
                               "script": {"type": "text/javascript", "exec": prereq.splitlines()}})
    if tests:
        item["event"].append({"listen": "test",
                               "script": {"type": "text/javascript", "exec": tests.splitlines()}})
    hdrs = list(headers or [])
    request = {
        "method": method,
        "header": hdrs,
        # 用整串 raw URL，避免 newman 把含 scheme 的 {{baseUrl}} 拆进 host 后无法还原
        "url": "{{baseUrl}}" + path,
    }
    if auth == "none":
        request["auth"] = {"type": "noauth"}
    elif auth == "fake":
        hdrs.append({"key": "Authorization", "value": "Bearer faketoken.abc.def"})
        request["auth"] = {"type": "noauth"}
    # bearer -> 继承集合级 Bearer {{token}}
    if body is not None:
        hdrs.append({"key": "Content-Type", "value": "application/json"})
        request["body"] = {"mode": "raw", "raw": body,
                           "options": {"raw": {"language": "json"}}}
    item["request"] = request
    return item


# ---- 通用断言片段 ----
def status(code):
    return f'pm.test("HTTP {code}", () => pm.response.to.have.status({code}));'


def code_is(c):
    return f'pm.test("业务码 {c}", () => pm.expect(pm.response.json().code).to.eql({c}));'


PWD = os.environ.get("RD_TEST_PWD", "ChangeMe123!")  # 真实测试口令通过环境变量传入，不写入仓库

# ================= 1 认证授权 =================
auth_items = [
    req("1.1 注册-合法", "POST", "/api/auth/register", auth="none",
        prereq='if(!pm.collectionVariables.get("runUser")){pm.collectionVariables.set("runUser","qa_"+Date.now());}',
        body='{\n  "username": "{{runUser}}",\n  "password": "{{pwd}}",\n  "display_name": "QA Tester"\n}',
        tests="\n".join([
            status(200), code_is(0),
            'const d=pm.response.json().data;',
            'pm.test("返回 token", () => pm.expect(d.token).to.be.a("string").and.not.empty);',
            'pm.test("返回 refresh_token", () => pm.expect(d.refresh_token).to.be.a("string").and.not.empty);',
            'pm.collectionVariables.set("token", d.token);',
            'pm.collectionVariables.set("refreshToken", d.refresh_token);',
            'pm.collectionVariables.set("userId", d.user.user_id);',
        ])),
    req("1.2 注册-重复用户名(缺陷:应409实返400)", "POST", "/api/auth/register", auth="none",
        body='{\n  "username": "{{runUser}}",\n  "password": "{{pwd}}"\n}',
        tests="\n".join([
            'pm.test("拒绝重复注册(非0业务码)", () => pm.expect(pm.response.json().code).to.not.eql(0));',
            'pm.test("提示用户名已存在", () => pm.expect(pm.response.json().message).to.include("exists"));',
            '// 已知缺陷 BUG-001: 语义上应为 409 Conflict, 实际返回 400/40001',
            'pm.test("[缺陷观察] 期望 409", () => pm.expect(pm.response.code).to.eql(409));',
        ])),
    req("1.3 注册-密码过短", "POST", "/api/auth/register", auth="none",
        body='{\n  "username": "qa_short_{{$timestamp}}",\n  "password": "123"\n}',
        tests="\n".join([status(400), code_is(40001),
                         'pm.test("提示密码长度", () => pm.expect(pm.response.json().message).to.include("at least 8"));'])),
    req("1.4 注册-空用户名", "POST", "/api/auth/register", auth="none",
        body='{\n  "username": "",\n  "password": "{{pwd}}"\n}',
        tests="\n".join([status(400), code_is(40001)])),
    req("1.5 登录-正确", "POST", "/api/auth/login", auth="none",
        body='{\n  "username": "{{runUser}}",\n  "password": "{{pwd}}"\n}',
        tests="\n".join([status(200), code_is(0),
                         'const d=pm.response.json().data;',
                         'pm.collectionVariables.set("token", d.token);',
                         'pm.collectionVariables.set("refreshToken", d.refresh_token);',
                         'pm.test("token 非空", () => pm.expect(d.token).to.be.a("string").and.not.empty);'])),
    req("1.6 登录-密码错误", "POST", "/api/auth/login", auth="none",
        body='{\n  "username": "{{runUser}}",\n  "password": "WrongPass99"\n}',
        tests="\n".join([status(401), code_is(40101),
                         'pm.test("统一错误提示", () => pm.expect(pm.response.json().message).to.include("invalid username or password"));'])),
    req("1.7 登录-不存在用户", "POST", "/api/auth/login", auth="none",
        body='{\n  "username": "no_such_user_xyz",\n  "password": "{{pwd}}"\n}',
        tests="\n".join([status(401), code_is(40101),
                         'pm.test("不泄露账号是否存在", () => pm.expect(pm.response.json().message).to.include("invalid username or password"));'])),
    req("1.8 当前用户-带token", "GET", "/api/auth/me", auth="bearer",
        tests="\n".join([status(200), code_is(0),
                         'pm.test("用户名匹配", () => pm.expect(pm.response.json().data.username).to.eql(pm.collectionVariables.get("runUser")));'])),
    req("1.9 当前用户-无token", "GET", "/api/auth/me", auth="none",
        tests="\n".join([status(401), code_is(40101),
                         'pm.test("提示需要认证", () => pm.expect(pm.response.json().message).to.include("authentication required"));'])),
    req("1.10 当前用户-伪造token", "GET", "/api/auth/me", auth="fake",
        tests="\n".join([status(401), code_is(40101),
                         'pm.test("提示无效token", () => pm.expect(pm.response.json().message).to.include("invalid token"));'])),
    req("1.11 刷新令牌", "POST", "/api/auth/refresh", auth="none",
        body='{\n  "refresh_token": "{{refreshToken}}"\n}',
        tests="\n".join([status(200), code_is(0),
                         'const d=pm.response.json().data;',
                         'pm.collectionVariables.set("token", d.token);',
                         'pm.collectionVariables.set("refreshToken", d.refresh_token);',
                         'pm.test("发放新token", () => pm.expect(d.token).to.be.a("string").and.not.empty);'])),
]

# ================= 2 用户资料与社交 =================
user_items = [
    req("2.1 个人资料-带token", "GET", "/api/users/me/profile", auth="bearer",
        tests="\n".join([status(200), code_is(0),
                         'pm.test("含 user_id", () => pm.expect(pm.response.json().data).to.have.property("user_id"));'])),
    req("2.2 个人资料-无token", "GET", "/api/users/me/profile", auth="none",
        tests="\n".join([status(401), code_is(40101)])),
    req("2.3 在线状态", "GET", "/api/users/me/status", auth="bearer",
        tests="\n".join([status(200), code_is(0),
                         'pm.test("online 为真", () => pm.expect(pm.response.json().data.online).to.eql(true));'])),
    req("2.4 动态流 feed", "GET", "/api/users/me/feed", auth="bearer",
        tests="\n".join([status(200), code_is(0),
                         'pm.test("items 为数组", () => pm.expect(pm.response.json().data.items).to.be.an("array"));'])),
]

# ================= 3 图谱查询 =================
graph_items = [
    req("3.1 根话题 roots", "GET", "/api/nodes/roots", auth="bearer",
        tests="\n".join([status(200), code_is(0),
                         'pm.test("data 为数组", () => pm.expect(pm.response.json().data).to.be.an("array"));'])),
    req("3.2 节点详情-非法UUID格式", "GET", "/api/nodes/not-a-uuid", auth="bearer",
        tests="\n".join([status(400), code_is(40001),
                         'pm.test("提示需UUID", () => pm.expect(pm.response.json().message).to.include("UUID"));'])),
    req("3.3 节点详情-合法但不存在", "GET", "/api/nodes/00000000-0000-0000-0000-000000000000", auth="bearer",
        tests="\n".join([status(404), code_is(40401),
                         'pm.test("提示未找到", () => pm.expect(pm.response.json().message).to.include("not found"));'])),
]

# ================= 4 认证收尾 =================
logout_items = [
    req("4.1 登出", "POST", "/api/auth/logout", auth="bearer",
        tests="\n".join([status(200), code_is(0)])),
    req("4.2 登出后复用旧token", "GET", "/api/auth/me", auth="bearer",
        tests="\n".join([status(401), code_is(40101),
                         'pm.test("提示token已吊销", () => pm.expect(pm.response.json().message).to.include("revoked"));'])),
]

collection = {
    "info": {
        "name": "RhizoDelta 接口测试",
        "description": "基于对运行中实例 http://localhost:8090 的实测编写。模块: 认证授权/用户资料/图谱查询。",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
    },
    "auth": {"type": "bearer", "bearer": [{"key": "token", "value": "{{token}}", "type": "string"}]},
    "variable": [
        {"key": "pwd", "value": PWD},
        {"key": "runUser", "value": ""},
        {"key": "token", "value": ""},
        {"key": "refreshToken", "value": ""},
        {"key": "userId", "value": ""},
    ],
    "item": [
        {"name": "1 认证授权", "item": auth_items},
        {"name": "2 用户资料与社交", "item": user_items},
        {"name": "3 图谱查询", "item": graph_items},
        {"name": "4 认证收尾", "item": logout_items},
    ],
}

environment = {
    "name": "RhizoDelta Local",
    "values": [
        {"key": "baseUrl", "value": "http://localhost:8090", "enabled": True},
        {"key": "pwd", "value": PWD, "enabled": True},
    ],
    "_postman_variable_scope": "environment",
}

with open(os.path.join(OUT_DIR, "RhizoDelta.postman_collection.json"), "w", encoding="utf-8") as f:
    json.dump(collection, f, ensure_ascii=False, indent=2)
with open(os.path.join(OUT_DIR, "RhizoDelta.local.postman_environment.json"), "w", encoding="utf-8") as f:
    json.dump(environment, f, ensure_ascii=False, indent=2)

total = len(auth_items) + len(user_items) + len(graph_items) + len(logout_items)
print(f"已生成 Postman 集合，请求数={total}，输出目录={OUT_DIR}")
