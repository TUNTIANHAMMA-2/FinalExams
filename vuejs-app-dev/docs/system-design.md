# 系统设计说明

## 1. 总体架构

RhizoDelta 前端采用 React + TypeScript + Vite 的单页应用架构。页面通过 React Router 管理，业务数据通过统一 API 客户端访问后端，跨组件状态由 Zustand 维护，图谱画布使用 React Flow 及布局算法呈现。

整体链路可以概括为：

用户操作页面 -> 组件调用 store action -> store 调用 API 模块 -> API 客户端请求后端 -> 后端返回 REST 数据或 SSE 事件 -> store 更新状态 -> 组件重新渲染。

正式报告中的配图可参考：

- `../images/01_fullstack_architecture.png`
- `../images/03_frontend_architecture.png`
- `../images/04_backend_async_flow.png`

## 2. 技术栈选择

| 技术 | 用途 | 选择原因 |
|---|---|---|
| React 19 | UI 组件开发 | 适合复杂交互和组件拆分 |
| TypeScript | 类型约束 | 降低接口字段和组件 props 使用错误 |
| Vite | 开发与构建 | 启动快，配置轻，适合课程项目展示 |
| React Router | 前端路由 | 管理登录页、首页、工作区、设置页 |
| Zustand | 状态管理 | 写法轻量，适合按业务 store 拆分 |
| React Flow | 图谱画布 | 支持节点、边、缩放和交互 |
| Tailwind CSS | 样式实现 | 便于快速构建响应式界面 |
| SSE | 实时事件 | 适合后端持续推送节点、边和状态变化 |
| Vitest | 测试 | 与 Vite 项目集成自然 |

## 3. 路由设计

路由入口位于 `src/App.tsx`。核心设计是把公开路由和受保护路由分开：

- `/login`：未登录用户访问，已登录用户自动跳转首页。
- `/`：登录后的首页。
- `/workspace`：默认工作区，加载第一个根话题。
- `/workspace/:rhizomeId`：指定根话题工作区。
- `/settings`：个人资料和界面偏好设置。

`RequireAuth` 负责检查 token 和恢复会话。未登录用户访问业务页面时跳转到 `/login`。这个设计避免每个页面重复写鉴权逻辑。

## 4. 前端模块划分

### 4.1 页面和壳层

`src/App.tsx` 只负责路由装配、懒加载和错误边界。具体页面逻辑下沉到组件目录：

- `components/home/*`：首页。
- `components/DesktopGraphWorkspace.tsx`：桌面端工作区。
- `components/mobile/*`：移动端讨论树。
- `components/settings/*`：设置页。
- `components/chrome/*`：Header、通知、面包屑等通用界面。

### 4.2 图谱工作区

工作区由三部分组成：

- 左侧话题列表：选择根话题。
- 中间画布：展示谱系视图或探索视图。
- 右侧面板：展示节点详情、编辑草稿、复核操作。

`GraphWorkspace` 根据视口判断使用桌面端还是移动端：

- 桌面端：`DesktopGraphWorkspace` + `DagCanvas` / `ExploreCanvas`。
- 移动端：`MobileDiscussionTreeView` + `CommentTreeItem`。

这样避免在小屏设备上强行展示复杂图谱，降低阅读和操作成本。

### 4.3 API 层

`src/api/client.ts` 是统一请求入口，负责：

- 拼接基础地址。
- 自动附加 `Authorization: Bearer <token>`。
- 处理 `FormData` 和 JSON 请求头。
- 遇到 401 时清除登录状态。
- 解析后端统一响应 `{ code, message, data }`。
- 将错误集中转换为 `Error`。

业务 API 再按领域拆分，例如：

- `auth.ts`：认证。
- `nodes.ts`：节点。
- `posts.ts`：发帖。
- `decisions.ts`：决策。
- `associations.ts`：关联。
- `audit.ts`：审计。
- `search.ts`：检索。
- `profile.ts`：用户资料。

这个分层让页面组件不用直接关心底层请求细节。

### 4.4 状态管理

状态按业务职责拆分到多个 Zustand store：

| Store | 主要职责 |
|---|---|
| `authStore` | token、当前用户、登录状态 |
| `graphStore` | 节点、边、当前选中节点、根话题、图谱加载 |
| `sseStore` | SSE 连接状态和编排状态 |
| `homeStore` | 首页动态、列表数据 |
| `discussionTreeStore` | 移动端讨论树、待发送评论、刷新状态 |
| `uiStore` | 侧边栏、右侧面板、画布模式、toast、命令面板 |
| `notificationStore` | 实时通知 |

这种拆分减少了单个全局状态对象过大的问题，也方便对 store 单独测试。

## 5. 关键数据流

### 5.1 登录数据流

1. 用户在登录页提交账号密码。
2. 组件调用认证 API。
3. 登录成功后 token 写入本地存储和 `authStore`。
4. `RequireAuth` 检测到 token 后允许进入业务页面。
5. 后续 API 请求自动带上 token。
6. 如果请求返回 401，API 客户端清除 token，用户回到登录态。

### 5.2 进入工作区数据流

1. 用户进入 `/workspace/:rhizomeId`。
2. `DesktopGraphWorkspace` 读取路由参数。
3. 调用 `loadGraphForRoot` 和 `graphStore.loadTopologyContext`。
4. 后端返回根话题附近的节点和边。
5. store 更新节点、边和选择态。
6. 画布组件根据 store 状态渲染图谱。

### 5.3 发布回复数据流

1. 用户填写发布或回复内容。
2. `PostForm` 校验空内容和登录状态。
3. 调用 `createPost` 提交 `request_id`、作者、内容和目标节点。
4. 后端接受请求后异步编排，不要求前端同步等待最终结果。
5. 前端显示排队提示。
6. 后端后续通过 SSE 推送状态、节点和边。
7. `useSse` 根据事件更新图谱和移动端讨论树。

### 5.4 SSE 实时数据流

`src/hooks/useSse.ts` 监听 `/api/events/stream`。已处理的事件包括：

- `NODE_CREATED`：补拉节点并加入图谱。
- `EDGE_CREATED`：补齐端点节点后添加边。
- `EDGE_REMOVED`：移除指定关系。
- `DECISION_COMPLETE`：替换乐观节点，展示决策结果。
- `ORCHESTRATION_STATUS`：更新后端编排状态。
- `SUMMARY_GENERATED`：刷新摘要内容。
- `QUALITY_SCORED`：刷新质量评分。

SSE 连接支持断线重连、指数退避和页面可见性处理，避免隐藏页面时持续重连浪费资源。

## 6. 响应式设计

项目没有简单地把桌面图谱缩小到手机屏幕，而是按设备能力切换交互方式：

- 桌面端：三栏工作区，适合大范围查看节点关系。
- 移动端：嵌套评论树，适合阅读、回复和长按操作。

这一设计的重点是根据使用场景改变信息呈现方式，而不仅是改变 CSS 宽度。

## 7. 难点与解决策略

| 难点 | 表现 | 解决策略 |
|---|---|---|
| 图谱数据复杂 | 节点、边、关联、审计来自不同接口 | API 层和 store 层统一转换，组件只消费可渲染状态 |
| 异步处理链路长 | 发帖后结果不是立刻返回 | 使用 request_id 和 SSE 事件追踪状态 |
| 桌面移动差异大 | 小屏难以操作复杂图谱 | 桌面图谱，移动讨论树 |
| 状态共享范围广 | 多个组件需要节点、选择态和面板状态 | 按职责拆分 Zustand store |
| 认证逻辑容易重复 | 多个页面都需要登录检查 | 在路由层集中实现 `RequireAuth` |

## 8. 可扩展方向

- 增加更多答辩演示截图，使交付物更直观。
- 为关键业务 API 补充接口清单和示例响应。
- 增强图谱筛选、节点搜索和讨论路径回放。
- 为移动端补充离线提示和弱网状态。
- 提高测试覆盖，尤其是 SSE 异常、权限边界和图谱布局稳定性。
