# 基于人工智能课程的期末项目说明文档

## 1. 项目概述

本项目是一个面向课堂签到场景的人工智能课程期末项目，名称可概括为“ASCII 风格人脸识别智能签到系统”。系统使用 Python 和 OpenCV 完成人脸检测、人脸识别、自动签到、重复签到拦截和数据统计，同时提供 React 前端用于注册、实时签到、记录查看、统计分析和学生状态智能分析。

项目体现了人工智能课程中的两类核心能力：

1. 计算机视觉识别：通过 Haar Cascade 检测人脸，通过 LBPH 模型完成人脸身份识别。
2. 机器学习分析：通过决策树模型结合考勤和成绩数据，对学生状态进行低风险、中风险、高风险分类。

系统整体流程如下：

```text
学生注册人脸样本
-> 训练 LBPH 人脸识别模型
-> 摄像头采集实时画面
-> 图像预处理与人脸检测
-> 人脸身份识别与置信度判断
-> 自动签到或重复签到拦截
-> 识别事件与签到结果写入 SQLite
-> 前端展示记录、统计和 ASCII 实时画面
-> 生成演示班级数据
-> 训练决策树学生风险模型
-> 输出学生状态评估报告
```

## 2. 项目目录与文件说明

### 2.1 根目录文件

| 路径 | 作用 |
| --- | --- |
| `README.md` | 项目主说明文档，介绍功能范围、数据库设计、机器学习智能分析、安装依赖和运行方式。 |
| `MVP_项目方案.md` | 项目 MVP 方案，说明项目定位、目标、功能范围、AI 课程知识结合点和系统模块设计。 |
| `requirements.txt` | Python 后端依赖，主要包含 `opencv-contrib-python`、`numpy`、`scikit-learn`、`joblib`。 |
| `《人工智能基础与应用》期末考查方案.docx` | 课程期末考查要求文档。 |
| `.gitignore` | Git 忽略规则。 |

### 2.2 `app/` 后端与算法目录

`app/` 是 Python 后端核心目录，包含命令行入口、本地 HTTP API、图像处理、人脸识别、签到记录、事件日志、统计分析和学生风险模型。

| 文件 | 作用 |
| --- | --- |
| `app/__init__.py` | 将 `app` 声明为 Python 包，并保存项目简介。 |
| `app/main.py` | 命令行入口。支持 `register`、`run`、`stats`、`serve`、`demo-checkin` 等命令。 |
| `app/config.py` | 集中配置路径和参数，例如数据目录、模型文件、摄像头参数、人脸图片尺寸、LBPH 置信度阈值、ASCII 字符集。 |
| `app/camera.py` | 使用 OpenCV 打开本机摄像头，并设置画面宽高。 |
| `app/preprocess.py` | 图像预处理模块，负责缩放、灰度化、直方图均衡化，以及为 ASCII 渲染准备灰度图。 |
| `app/face_detect.py` | 人脸检测模块，加载 OpenCV Haar Cascade 分类器，检测图像中的人脸区域，并提供最大人脸选择函数。 |
| `app/face_recognize.py` | 人脸注册、样本归一化、LBPH 模型训练、模型加载和人脸匹配模块。 |
| `app/attendance.py` | 签到决策模块，负责写入签到记录，并阻止同一用户同一天重复写入。 |
| `app/events.py` | 识别事件日志模块，生成事件 ID，并记录 `success`、`duplicate`、`recognized`、`unknown`、`no_model` 等事件。 |
| `app/storage.py` | 数据存储模块，负责创建 SQLite 表、读写签到记录、读写事件日志、导入旧 CSV、导出 CSV。 |
| `app/analytics.py` | 统计分析模块，计算签到人数、重复签到次数、未知人脸次数、出勤率、识别成功率等指标。 |
| `app/student_analysis.py` | 机器学习智能分析模块，生成演示班级数据，训练决策树模型，并输出学生风险评估报告。 |
| `app/api_server.py` | 本地 HTTP API 服务，供 React 前端调用。处理注册、样本校验、识别签到、记录查询、统计查询、CSV 导出、学生分析等接口。 |
| `app/ascii_render.py` | 后端 ASCII 渲染模块，将视频帧按亮度映射为字符画。 |

### 2.3 `data/` 数据目录

`data/` 是运行时数据目录，主要用于保存本地数据库、人脸样本、人脸模型、导出文件和机器学习模型。

| 路径 | 作用 |
| --- | --- |
| `data/attendance.db` | SQLite 主数据库，保存签到记录、识别事件、学生、成绩和训练样本。 |
| `data/attendance.csv` | 旧版或兼容用签到 CSV 数据。当前主存储是 SQLite。 |
| `data/event_log.csv` | 旧版或兼容用识别事件 CSV 数据。 |
| `data/faces/` | 保存用户注册时的原始图片和归一化后的人脸样本。 |
| `data/encodings/labels.json` | 保存注册用户与 LBPH label 的映射关系。 |
| `data/encodings/lbph_model.yml` | OpenCV LBPH 人脸识别模型文件。 |
| `data/exports/attendance_records.csv` | 从 SQLite 导出的签到记录 CSV。 |
| `data/exports/recognition_events.csv` | 从 SQLite 导出的识别事件 CSV。 |
| `data/models/student_risk_model.joblib` | scikit-learn 决策树学生风险模型文件。 |
| `data/**/.gitkeep` | 用于让空目录能被 Git 保留。 |

### 2.4 `frontend/` 前端目录

`frontend/` 是 React + Vite 前端工程，负责浏览器页面交互、摄像头采集、ASCII 实时展示和 API 调用。

| 文件或目录 | 作用 |
| --- | --- |
| `frontend/package.json` | 前端依赖和脚本定义，包含 `dev`、`build`、`lint`、`preview`。 |
| `frontend/package-lock.json` | 前端依赖锁定文件。 |
| `frontend/vite.config.ts` | Vite 构建配置。 |
| `frontend/index.html` | 前端 HTML 入口。 |
| `frontend/tsconfig*.json` | TypeScript 配置文件。 |
| `frontend/eslint.config.js` | ESLint 代码检查配置。 |
| `frontend/public/favicon.svg` | 浏览器 favicon。 |
| `frontend/public/icons.svg` | 前端图标资源。 |
| `frontend/dist/` | 前端构建产物目录。 |
| `frontend/node_modules/` | 前端依赖安装目录，不属于业务源码。 |

### 2.5 `frontend/src/` 前端源码

| 文件 | 作用 |
| --- | --- |
| `frontend/src/main.tsx` | React 应用入口，挂载 `App`，引入 Ant Design 样式和主题 Provider。 |
| `frontend/src/App.tsx` | 前端路由配置，定义实时监控、用户注册、数据中心、系统分析、智能分析页面。 |
| `frontend/src/api.ts` | 前端 API 封装，负责请求 Python 后端，规范化响应数据，处理 CSV 下载。 |
| `frontend/src/constants.ts` | 前端常量，例如 ASCII 字符集、ASCII 宽度、渲染间隔、识别请求间隔。 |
| `frontend/src/index.css` | 全局样式，包括布局、卡片、表格、ASCII 画面和主题相关样式。 |
| `frontend/src/components/Layout.tsx` | 应用主布局，提供侧边导航、移动端抽屉菜单、主题切换和页面内容区。 |
| `frontend/src/components/PageHeader.tsx` | 统一页面标题组件。 |
| `frontend/src/theme/themeContext.ts` | 明暗主题上下文定义。 |
| `frontend/src/theme/ThemeProvider.tsx` | Ant Design 主题配置和明暗模式切换逻辑。 |
| `frontend/src/pages/LiveAttendance.tsx` | 实时签到页面，调用浏览器摄像头，生成 ASCII 画面，并定时向后端发送识别请求。 |
| `frontend/src/pages/Register.tsx` | 用户注册页面，采集 3 张人脸样本，调用样本校验接口和注册接口。 |
| `frontend/src/pages/Records.tsx` | 数据中心页面，展示签到记录和识别事件日志，并支持 CSV 导出。 |
| `frontend/src/pages/Stats.tsx` | 系统分析页面，展示出勤率、识别成功率、事件分布和用户签到次数。 |
| `frontend/src/pages/StudentAnalysis.tsx` | 智能分析页面，生成演示数据、训练模型、刷新分析，并展示学生风险报告。 |

### 2.6 `tests/` 测试目录

| 文件 | 作用 |
| --- | --- |
| `tests/test_api_server.py` | 测试 API 注册参数、三样本人脸注册、样本校验和错误响应格式。 |
| `tests/test_attendance.py` | 测试同一用户同一天重复签到会被拦截。 |
| `tests/test_event_log.py` | 测试识别事件统计、旧 CSV 兼容升级、CSV 导出和出勤率计算。 |
| `tests/test_student_analysis.py` | 测试演示数据生成、决策树模型训练、学生风险报告输出，以及只读分析接口不会自动生成数据。 |

### 2.7 `docs/` 文档目录

| 文件 | 作用 |
| --- | --- |
| `docs/defense_outline.md` | 答辩提纲，说明项目背景、目标、系统流程、核心模块、创新点和演示步骤。 |
| `docs/frontend_logic.md` | 前端逻辑设计，说明页面职责、接口草案和交互流程。 |
| `docs/project_explanation.md` | 当前文档，用于系统性解释项目目录、文件、核心方法和业务逻辑。 |

### 2.8 其他目录

| 路径 | 作用 |
| --- | --- |
| `PIc/ASCIIPage.png` | 项目展示图片资源。 |
| `images/` | 图片资源目录，当前未包含核心源码文件。 |
| `generated/` | 生成文件目录，当前未包含核心源码文件。 |
| `.venv/` | Python 虚拟环境目录，不属于业务源码。 |
| `app/__pycache__/`、`tests/__pycache__/` | Python 缓存目录，不属于业务源码。 |
| `.agents/`、`.claude/`、`.codex/` | 本地开发或智能体工具配置目录，不属于项目业务功能。 |

## 3. 后端核心方法与逻辑

### 3.1 命令行入口逻辑

核心文件：`app/main.py`

`build_parser()` 定义命令行参数，系统支持以下命令：

| 命令 | 作用 |
| --- | --- |
| `python -m app.main serve` | 启动本地 HTTP API，供前端调用。 |
| `python -m app.main register --user-id ... --name ... --image ...` | 通过命令行注册一张图片。 |
| `python -m app.main run` | 通过本机摄像头启动命令行实时签到流程。 |
| `python -m app.main stats` | 输出签到统计结果。 |
| `python -m app.main demo-checkin` | 写入一条演示签到记录，便于验证数据链路。 |

`main()` 会先调用 `storage.ensure_data_dirs()` 创建数据目录，然后根据命令分发到对应处理函数。

### 3.2 图像采集与预处理逻辑

核心文件：`app/camera.py`、`app/preprocess.py`

图像采集逻辑：

1. `camera.open_camera()` 使用 `cv2.VideoCapture(config.CAMERA_INDEX)` 打开摄像头。
2. 设置摄像头宽度和高度，默认 640 x 480。
3. 如果摄像头无法打开，则抛出异常。

图像预处理逻辑：

1. `preprocess.prepare_frame(frame, scale)` 按比例缩小原始帧，默认缩放比例是 `0.25`。
2. 将 BGR 彩色图转成灰度图。
3. 使用 `cv2.equalizeHist()` 做直方图均衡化，提高光照变化下的识别稳定性。

预处理的意义是减少计算量，并让人脸检测和识别模型获得更稳定的输入。

### 3.3 人脸检测逻辑

核心文件：`app/face_detect.py`

系统使用 OpenCV 自带的 Haar Cascade 正脸检测器：

```text
cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
```

核心方法：

| 方法 | 作用 |
| --- | --- |
| `get_detector()` | 加载并缓存 Haar 人脸检测器。 |
| `locate_faces(gray_frame)` | 在灰度图中检测人脸，返回 `(x, y, width, height)` 列表。 |
| `largest_face(face_locations)` | 在多个人脸框中选择面积最大的人脸。 |

注册阶段使用 `largest_face()` 选择训练样本中的主要人脸。识别阶段会对检测到的每个人脸进行匹配。

### 3.4 人脸注册与 LBPH 模型训练逻辑

核心文件：`app/face_recognize.py`

前端注册流程要求采集 3 张有效人脸样本，对应正脸、左偏、右偏三个角度。后端注册逻辑如下：

1. `register_face_samples(user_id, name, image_paths)` 接收用户 ID、姓名和图片路径列表。
2. 对每张图片调用 `_load_gray_image()` 读取并转为灰度图。
3. 调用 `face_detect.locate_faces()` 检测人脸。
4. 调用 `face_detect.largest_face()` 选择最大人脸区域。
5. 调用 `_normalize_face()` 截取人脸区域、缩放到 `200 x 200`，并进行直方图均衡化。
6. 从 `data/encodings/labels.json` 读取用户注册表。
7. 如果用户已存在，沿用原 label；如果是新用户，分配新的整数 label。
8. 将归一化样本保存到 `data/faces/{user_id}/sample_001.png` 等文件。
9. 更新 `labels.json`。
10. 调用 `rebuild_model()` 重新训练 LBPH 模型。

`rebuild_model()` 会读取所有已注册用户的人脸样本，将样本数组和 label 数组传给 OpenCV 的 LBPH 识别器：

```text
cv2.face.LBPHFaceRecognizer_create()
recognizer.train(samples, labels)
recognizer.write(data/encodings/lbph_model.yml)
```

这里使用 `opencv-contrib-python` 是必要的，因为普通 `opencv-python` 不包含 `cv2.face` 模块。

### 3.5 人脸识别与置信度判断逻辑

核心文件：`app/face_recognize.py`

识别流程由 `match_faces(gray_frame, face_locations, known_faces, threshold)` 完成：

1. 如果没有检测到人脸，直接返回空列表。
2. 如果尚未训练模型，返回未匹配结果。
3. 对每个人脸区域调用 `_normalize_face()`，得到与训练样本同尺寸、同处理方式的人脸图。
4. 调用 `known_faces.recognizer.predict(sample)` 得到预测 label 和 confidence。
5. 根据 label 从 `faces_by_label` 中找到用户信息。
6. 判断 `confidence <= config.LBPH_CONFIDENCE_THRESHOLD` 时才认为匹配成功。

默认阈值：

```text
LBPH_CONFIDENCE_THRESHOLD = 75.0
```

LBPH 中 confidence 可以理解为距离或误差，数值越小表示越相似。因此项目使用“小于等于阈值”作为可信识别条件。

### 3.6 签到决策与防重复逻辑

核心文件：`app/attendance.py`

`mark_attendance(user_id, name, confidence, event_id)` 负责写入签到结果。逻辑如下：

1. 获取当前日期和时间。
2. 读取现有签到记录。
3. 如果同一 `user_id` 在当天已经有签到记录，返回 `duplicate`，不再写入新行。
4. 如果当天未签到，写入一条 `success` 签到记录。

这种设计保证 `attendance` 表只保存真正生效的签到结果，避免重复识别造成业务数据污染。

### 3.7 识别事件日志逻辑

核心文件：`app/events.py`

项目把“识别过程”和“签到结果”分开保存：

| 数据 | 存储位置 | 说明 |
| --- | --- | --- |
| 签到结果 | `attendance` 表 | 只保存真实生效的签到记录。 |
| 识别事件 | `event_log` 表 | 保存识别过程，包括成功、重复、未知人脸、模型未训练等。 |

`next_event_id()` 根据时间戳和计数器生成事件 ID。`append_event()` 负责写入事件日志。

常见事件类型：

| 类型 | 含义 |
| --- | --- |
| `success` | 识别成功并成功签到。 |
| `duplicate` | 识别成功，但当天已签到，因此拦截重复写入。 |
| `recognized` | 识别成功，但本次请求只预览，不写签到表。 |
| `unknown` | 检测到人脸，但没有匹配到注册用户。 |
| `no_model` | 检测到人脸，但尚未训练 LBPH 模型。 |
| `no_face` | 未检测到人脸。项目中正常空帧不写入事件表，避免产生大量无意义日志。 |

### 3.8 SQLite 存储与 CSV 导出逻辑

核心文件：`app/storage.py`

项目使用 SQLite 作为主存储，表结构由 `_init_db()` 创建。

主要数据表：

| 表 | 作用 |
| --- | --- |
| `attendance` | 保存签到结果。 |
| `event_log` | 保存识别事件日志。 |
| `storage_meta` | 保存存储迁移状态，例如旧 CSV 是否已导入。 |
| `students` | 保存学生基础信息。 |
| `grades` | 保存学生成绩。 |
| `ml_training_samples` | 保存机器学习训练样本。 |

核心存储方法：

| 方法 | 作用 |
| --- | --- |
| `ensure_data_dirs()` | 创建 `data/`、`faces/`、`encodings/`、`exports/`、`models/` 等目录。 |
| `initialize_database()` | 初始化 SQLite 数据库。 |
| `append_attendance()` | 写入签到记录。 |
| `read_attendance()` | 按日期和时间倒序读取签到记录。 |
| `append_event()` | 写入识别事件。 |
| `read_events()` | 按时间倒序读取识别事件。 |
| `query()`、`execute_write()`、`execute_many()` | 通用 SQL 查询和写入封装。 |
| `export_attendance_csv()` | 从 SQLite 导出签到 CSV。 |
| `export_events_csv()` | 从 SQLite 导出识别事件 CSV。 |

为了兼容旧数据，`_import_legacy_csv()` 会把旧版 `attendance.csv` 和 `event_log.csv` 导入 SQLite，并通过 `storage_meta` 避免重复导入。

### 3.9 统计分析逻辑

核心文件：`app/analytics.py`

`summarize_attendance()` 读取签到记录、识别事件和注册用户信息，输出前端统计页面需要的数据。

主要统计指标：

| 指标 | 说明 |
| --- | --- |
| `total_records` | 非演示签到记录总数。 |
| `status_counts` | 按签到状态统计记录数量。 |
| `valid_status_counts` | 只统计注册用户的有效签到。 |
| `event_total` | 非演示识别事件总数。 |
| `event_counts` | 按事件类型统计识别事件数量。 |
| `user_counts` | 按姓名统计成功签到次数。 |
| `registered_user_count` | 当前注册用户数量。 |
| `attendance_rate` | 成功签到用户数 / 注册用户数。 |
| `recognition_success_rate` | `(success + duplicate + recognized) / (success + duplicate + recognized + unknown)`。 |

统计时会排除 `event_id` 以 `demo-` 开头的演示数据，避免演示数据影响真实签到统计。

### 3.10 本地 HTTP API 逻辑

核心文件：`app/api_server.py`

后端 API 使用 Python 标准库 `http.server` 实现，不依赖 Flask 或 FastAPI。`ThreadingHTTPServer` 支持多请求处理。

主要接口：

| 接口 | 方法 | 作用 |
| --- | --- | --- |
| `/api/health` | GET | 健康检查。 |
| `/api/register` | POST | 注册用户人脸样本。 |
| `/api/validate-face` | POST | 校验当前图片中是否恰好有 1 张人脸。 |
| `/api/recognize` | POST | 识别当前帧，可选择是否写入签到。 |
| `/api/records` | GET | 获取签到记录。 |
| `/api/events` | GET | 获取识别事件日志。 |
| `/api/export/attendance` | GET | 导出签到 CSV。 |
| `/api/export/events` | GET | 导出识别事件 CSV。 |
| `/api/stats` | GET | 获取统计分析结果。 |
| `/api/users` | GET | 获取已注册用户。 |
| `/api/student-analysis` | GET | 获取学生风险分析结果。 |
| `/api/student-analysis/demo-data` | POST | 生成演示班级数据，并训练模型。 |
| `/api/student-analysis/train` | POST | 训练学生风险模型。 |

`recognize_from_payload()` 是实时识别的 API 核心逻辑：

1. 从前端接收 base64 图片。
2. 解码成 OpenCV BGR 图像。
3. 转灰度并均衡化。
4. 调用 Haar 检测人脸。
5. 加载 LBPH 模型和注册用户映射。
6. 调用 `match_faces()` 匹配身份。
7. 如果匹配成功，根据 `mark_attendance` 决定是否写签到。
8. 写入识别事件日志。
9. 返回识别状态、人脸数量、主匹配用户、事件和所有匹配结果。

### 3.11 ASCII 渲染逻辑

核心文件：`app/ascii_render.py`、`frontend/src/pages/LiveAttendance.tsx`

后端命令行模式使用 `app/ascii_render.py`：

1. 将视频帧缩放到指定宽度。
2. 转为灰度图。
3. 将每个像素亮度映射到字符集中的一个字符。
4. 拼接成多行字符串输出到终端。

前端实时页面也实现了 ASCII 渲染：

1. 浏览器摄像头画面绘制到 Canvas。
2. 读取像素数据。
3. 根据 RGB 计算亮度。
4. 对左侧相邻像素做简单边缘增强。
5. 将亮度映射为 ASCII 字符。
6. 使用 `<pre>` 展示字符画，并根据容器宽度动态计算字号和高度。

ASCII 渲染不是识别算法本身，而是视觉展示层。它增强了项目演示效果，也体现了图像灰度映射和数据可视化思想。

## 4. 机器学习智能分析逻辑

核心文件：`app/student_analysis.py`

智能分析模块用于体现课程中的监督学习和分类模型思想。它不是人脸识别的替代功能，而是基于签到数据和成绩数据做进一步分析。

### 4.1 特征设计

模型使用 6 个特征：

| 特征 | 含义 |
| --- | --- |
| `attendance_rate_30d` | 近 30 天出勤率。 |
| `late_count_7d` | 近 7 天迟到次数。 |
| `absent_count_30d` | 近 30 天缺勤天数。 |
| `duplicate_count_30d` | 近 30 天重复签到事件数。 |
| `avg_score` | 历史平均成绩。 |
| `score_delta` | 最近一次成绩相对上一次成绩的变化。 |

风险标签：

| 标签值 | 风险等级 |
| --- | --- |
| `0` | 低风险 |
| `1` | 中风险 |
| `2` | 高风险 |

### 4.2 演示数据生成

`generate_demo_data()` 会生成可重复的演示班级数据：

1. 固定随机种子 `Random(20260603)`，保证每次生成结果稳定。
2. 创建 5 名演示学生。
3. 为每名学生生成两次成绩：期中考试和阶段测验。
4. 根据设定出勤率生成近 30 天签到记录。
5. 根据设定迟到次数生成迟到时间。
6. 生成重复签到事件。
7. 生成 5 条真实演示学生训练样本。
8. 额外生成 80 条 synthetic 训练样本，增强模型训练数据量。
9. 写入 `students`、`grades`、`attendance`、`event_log`、`ml_training_samples` 表。

演示数据写入真实 SQLite 表，不是前端静态假数据，因此可以完整演示数据采集、训练、预测和报告输出链路。

### 4.3 风险标签规则

`_risk_label(attendance_rate, late_count, score_delta)` 根据规则生成训练标签：

1. 出勤率低于 0.8 加 30 分，低于 0.9 加 15 分。
2. 迟到次数大于等于 3 加 30 分，大于等于 1 加 15 分。
3. 成绩下降大于等于 10 分加 40 分，下降大于等于 5 分加 20 分。
4. 总分大于等于 60 为高风险，大于等于 30 为中风险，否则为低风险。

这个规则用于构造训练样本标签，后续决策树会学习这些特征与标签之间的关系。

### 4.4 模型训练

`train_model()` 训练学生风险分类模型：

1. 从 `ml_training_samples` 表读取训练样本。
2. 如果样本少于 10 条，自动生成演示数据。
3. 将 6 个特征组成特征矩阵 `X`。
4. 将 `risk_label` 组成标签向量 `y`。
5. 使用 `DecisionTreeClassifier(max_depth=5, random_state=42)` 训练模型。
6. 使用 `joblib.dump()` 保存到 `data/models/student_risk_model.joblib`。

选择决策树的原因：

1. 适合小型课程项目和 MVP。
2. 训练速度快。
3. 输出结果容易解释。
4. 能直观体现监督学习中的分类思想。

### 4.5 学生风险预测与报告生成

`analyze_students()` 输出智能分析页面的数据：

1. 读取 `students` 表中的学生。
2. 检查模型文件是否存在。
3. 对每名学生调用 `_student_features()` 提取当前特征。
4. 加载决策树模型。
5. 调用 `model.predict()` 得到风险标签。
6. 调用 `model.predict_proba()` 得到模型置信度。
7. 调用 `_risk_score()` 计算业务风险分值。
8. 调用 `_summary()` 生成中文摘要和教师建议。
9. 汇总风险分布和学生报告列表。

报告内容包括：

| 字段 | 含义 |
| --- | --- |
| `risk_level` | 低风险、中风险或高风险。 |
| `risk_score` | 0 到 100 的业务风险分。 |
| `confidence` | 模型预测置信度。 |
| `features` | 该学生的 6 个特征。 |
| `summary` | 自动生成的状态摘要。 |
| `suggestion` | 对教师的关注或干预建议。 |

## 5. 前端核心逻辑

### 5.1 路由与整体布局

核心文件：`frontend/src/App.tsx`、`frontend/src/components/Layout.tsx`

前端使用 React Router：

| 路由 | 页面 |
| --- | --- |
| `/live` | 实时监控页面。 |
| `/register` | 用户注册页面。 |
| `/records` | 数据中心页面。 |
| `/stats` | 系统分析页面。 |
| `/analysis` | 智能分析页面。 |

`Layout.tsx` 提供左侧导航栏、移动端抽屉菜单、当前时间显示、明暗主题切换和主内容区。

### 5.2 API 封装

核心文件：`frontend/src/api.ts`

`api.ts` 的职责：

1. 统一配置 API 地址，默认 `http://127.0.0.1:8765`。
2. 封装 JSON 请求和错误处理。
3. 定义 TypeScript 类型，例如 `AttendanceRecord`、`RecognitionResponse`、`StatsResponse`、`StudentRiskReport`。
4. 将后端响应规范化为前端可直接使用的数据结构。
5. 封装 CSV 下载逻辑。

### 5.3 实时签到页面

核心文件：`frontend/src/pages/LiveAttendance.tsx`

主要逻辑：

1. 点击“启动摄像头”后调用 `navigator.mediaDevices.getUserMedia()` 获取浏览器摄像头。
2. 每 `ASCII_FRAME_INTERVAL_MS` 毫秒把视频帧转为 ASCII 字符画。
3. 每 `RECOGNITION_INTERVAL_MS` 毫秒截取当前视频帧，编码为 JPEG base64。
4. 调用 `recognizeFrame(imageData, true)` 请求后端识别并签到。
5. 根据返回状态展示“签到成功”“重复签到”“未检测到人脸”“未知用户”“模型未训练”等结果。
6. 页面卸载或点击停止时关闭摄像头和定时器。

该页面是项目演示的核心页面，串联了浏览器摄像头、ASCII 渲染、后端识别、签到写入和状态展示。

### 5.4 用户注册页面

核心文件：`frontend/src/pages/Register.tsx`

主要逻辑：

1. 输入学号和姓名。
2. 启动摄像头预览。
3. 手动采集 3 张人脸样本。
4. 每次采集后调用 `/api/validate-face`，确保画面中恰好有 1 张人脸。
5. 三张样本齐全后调用 `/api/register`。
6. 后端保存样本并重新训练 LBPH 模型。

三样本设计可以提高模型对轻微角度和光照变化的适应能力。

### 5.5 数据中心页面

核心文件：`frontend/src/pages/Records.tsx`

主要逻辑：

1. 调用 `/api/records` 获取签到记录。
2. 调用 `/api/events` 获取识别事件。
3. 支持按姓名或学号筛选。
4. 使用表格分别展示签到记录和识别日志。
5. 调用 CSV 导出接口下载数据文件。

数据中心用于展示业务结果和识别过程，便于答辩时说明系统不是只显示结果，也保留了过程数据。

### 5.6 系统分析页面

核心文件：`frontend/src/pages/Stats.tsx`

主要逻辑：

1. 调用 `/api/stats` 获取统计结果。
2. 展示成功签到数、重复拦截数、未知人脸数。
3. 展示出勤率和识别成功率。
4. 展示识别事件类型分布。
5. 展示用户签到次数。

该页面体现数据分析能力，把原始记录转化为可解释指标。

### 5.7 智能分析页面

核心文件：`frontend/src/pages/StudentAnalysis.tsx`

主要逻辑：

1. 调用 `/api/student-analysis` 获取当前模型状态和学生报告。
2. 点击“生成演示数据”调用 `/api/student-analysis/demo-data`。
3. 点击“训练模型”调用 `/api/student-analysis/train`。
4. 展示模型状态、学生数、高风险人数、训练样本数。
5. 展示学生风险预测表格。
6. 选中学生后展示风险分、特征明细、摘要和建议。

该页面体现机器学习分类模型在教育场景中的应用。

## 6. 系统主流程说明

### 6.1 注册流程

```text
前端 Register 页面
-> 浏览器摄像头采集样本
-> /api/validate-face 校验单人脸
-> 累计 3 张有效样本
-> /api/register 提交 user_id、name、image_data_list
-> api_server 保存 source 图片
-> face_recognize.register_face_samples()
-> Haar 检测人脸
-> 人脸裁剪、缩放、均衡化
-> 保存归一化样本
-> 更新 labels.json
-> 重新训练 LBPH 模型
-> 写入 lbph_model.yml
```

### 6.2 实时签到流程

```text
前端 LiveAttendance 页面
-> 浏览器摄像头启动
-> Canvas 截取当前视频帧
-> /api/recognize 提交 base64 图片
-> 后端解码图片
-> 灰度化与直方图均衡化
-> Haar 检测人脸
-> LBPH 预测 label 和 confidence
-> confidence <= 75 判定为已注册用户
-> attendance.mark_attendance()
-> 当天未签到则写入 success
-> 当天已签到则返回 duplicate
-> events.append_event() 写识别事件
-> 前端展示识别状态和身份信息
```

### 6.3 数据统计流程

```text
签到记录 attendance
+ 识别事件 event_log
+ 注册用户 labels.json
-> analytics.summarize_attendance()
-> 计算出勤率、识别成功率、事件分布、用户签到次数
-> /api/stats 返回给前端
-> Stats 页面展示图表和指标
```

### 6.4 智能分析流程

```text
生成演示学生、成绩、签到、事件、训练样本
-> 从 ml_training_samples 读取 X 和 y
-> 使用 DecisionTreeClassifier 训练模型
-> 保存 student_risk_model.joblib
-> 从 students、attendance、event_log、grades 提取学生特征
-> 模型预测风险等级
-> 生成风险分、摘要和建议
-> StudentAnalysis 页面展示学生状态评估报告
```

## 7. 与人工智能课程知识的对应关系

| 课程知识点 | 项目体现 |
| --- | --- |
| 数据采集 | 使用摄像头采集人脸图像，生成签到、事件、成绩和训练样本数据。 |
| 数据预处理 | 对图像进行缩放、灰度化、直方图均衡化，对学生数据提取结构化特征。 |
| 计算机视觉 | 使用 Haar Cascade 在图像中检测人脸位置。 |
| 特征提取 | 使用 LBPH 将人脸图像转换为局部纹理特征。 |
| 模式识别 | 使用 LBPH 模型根据人脸特征预测用户 label。 |
| 阈值判定 | 根据 confidence 阈值判断识别是否可信。 |
| 业务决策 | 根据识别结果决定签到成功、重复签到、未知用户或模型未训练。 |
| 数据存储 | 使用 SQLite 保存签到、事件、学生、成绩和训练样本。 |
| 数据分析 | 统计出勤率、识别成功率、事件分布和用户签到次数。 |
| 监督学习 | 使用带标签训练样本训练学生风险分类模型。 |
| 分类模型 | 使用决策树输出低风险、中风险、高风险。 |
| 结果解释 | 自动生成学生状态摘要和教师建议。 |
| 可视化表达 | 使用 ASCII 字符画展示实时摄像头画面。 |

## 8. 项目特点与创新点

1. 将人脸识别与课堂签到业务结合，形成完整的 AI 应用闭环。
2. 使用三张样本人脸注册，提高注册数据的稳定性。
3. 使用 LBPH 置信度阈值，避免只按最近标签盲目识别。
4. 签到结果和识别事件分离存储，既保证业务表干净，也方便分析识别质量。
5. 自动拦截同一用户同一天重复签到。
6. 使用 SQLite 作为主存储，部署简单，适合课程项目。
7. 支持 CSV 导出，方便提交课程材料或继续做数据分析。
8. 使用 ASCII 字符画作为实时视觉展示，增强演示辨识度。
9. 增加决策树学生风险分析，将签到数据扩展为教育状态预警。
10. 前后端分离，既可用命令行演示，也可用 Web 页面交互演示。

## 9. 运行方式概述

安装 Python 依赖：

```bash
pip install -r requirements.txt
```

启动后端 API：

```bash
python -m app.main serve
```

启动前端：

```bash
cd frontend
npm install
npm run dev
```

命令行演示：

```bash
python -m app.main register --user-id 2026001 --name 张三 --image data/faces/zhangsan.jpg
python -m app.main run
python -m app.main stats
python -m app.main demo-checkin --user-id 2026001 --name 张三
```

## 10. 答辩讲解建议

答辩时可以按以下顺序讲：

1. 先说明项目场景：课堂签到效率低、容易代签、数据统计不方便。
2. 再说明 AI 解决方案：用人脸检测和识别替代人工确认身份。
3. 讲注册流程：三张样本、检测人脸、归一化、训练 LBPH 模型。
4. 讲识别流程：摄像头帧、预处理、Haar 检测、LBPH 预测、阈值判断。
5. 讲业务逻辑：识别成功后签到，同一天重复识别只记录事件不重复写签到。
6. 讲数据层：SQLite 保存签到结果和识别事件，CSV 只作为导出。
7. 讲统计页面：出勤率、识别成功率、重复签到和未知人脸事件。
8. 讲智能分析：用出勤率、迟到、缺勤、重复签到、成绩均值、成绩变化训练决策树。
9. 讲创新点：ASCII 实时画面加学生风险预警。
10. 最后说明可扩展方向：活体检测、多摄像头、真实班级长期数据、更复杂模型和图表分析。
