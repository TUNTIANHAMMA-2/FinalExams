# ASCII 风格人脸识别签到系统

一个面向课堂签到场景的 Python MVP 项目，使用 OpenCV 完成人脸检测与摄像头采集，结合 LBPH 人脸识别模型实现身份识别，并提供 ASCII 风格实时预览、签到记录保存、基础统计和机器学习学生风险分析能力。

## 当前范围

- 人脸注册（三张样本训练）
- 实时识别
- 自动签到
- 防重复打卡
- ASCII 风格预览
- 签到记录保存
- 识别事件日志
- 出勤率、识别成功率等基础统计
- 基于决策树模型的学生状态评估报告

## 目录结构

```text
app/
  main.py
  config.py
  camera.py
  preprocess.py
  face_detect.py
  face_recognize.py
  attendance.py
  events.py
  ascii_render.py
  storage.py
  analytics.py
  student_analysis.py
data/
  faces/
  encodings/
  exports/
  models/
  attendance.db
docs/
```

## 数据表设计

项目使用 SQLite 作为轻量级本地数据库，不依赖外部数据库服务，同时支持索引、事务和更快的查询统计。CSV 保留为导出格式，便于提交材料或答辩时直接查看数据。

- `data/attendance.db` 是主数据库文件。
- `attendance` 表是签到结果表，只保存真正生效的签到记录；同一用户同一天重复识别时不会追加新签到行。
- `event_log` 表是识别事件表，保存 `success`、`duplicate`、`recognized`、`unknown`、`no_model` 等识别过程事件，用于分析识别成功率、重复打卡次数和异常原因。
- `no_face` 表示摄像头画面中没有检测到人脸，是正常空帧状态，不写入事件日志，避免长时间运行时产生大量无意义日志。
- `event_id` 用于关联一次成功写入的签到结果与对应识别事件，便于从业务结果反查识别过程。
- `students` 表保存参与分析的学生基础信息。
- `grades` 表保存学生历史成绩，当前 MVP 使用“期中考试”和“阶段测验”两次成绩计算平均分与成绩变化。
- `ml_training_samples` 表保存机器学习训练样本，每条样本包含出勤率、迟到次数、缺勤次数、重复签到次数、平均成绩、成绩变化和风险标签。
- `data/exports/attendance_records.csv` 和 `data/exports/recognition_events.csv` 是从 SQLite 导出的 CSV 文件，不作为主存储。

## 机器学习智能分析

项目新增“智能分析”功能，作为课程要求中的第二个 AI 功能点。由于当前没有真实班级长期数据，系统提供可重复生成的演示班级数据，用于演示完整机器学习流程；真实部署时可以把演示数据替换成真实学生考勤和成绩数据后重新训练。

模型流程：

```text
演示班级数据/真实业务数据
-> 特征提取
-> 训练样本表 ml_training_samples
-> scikit-learn DecisionTreeClassifier
-> data/models/student_risk_model.joblib
-> 学生风险等级预测
-> 学生状态评估报告
```

当前模型使用 6 个特征：

- `attendance_rate_30d`：近 30 天出勤率
- `late_count_7d`：近 7 天迟到次数
- `absent_count_30d`：近 30 天缺勤天数
- `duplicate_count_30d`：近 30 天重复签到事件数
- `avg_score`：历史平均成绩
- `score_delta`：最近一次成绩相对上一次成绩的变化

前端“智能分析”页面提供三个动作：生成演示数据、训练模型、刷新分析。输出结果包括风险分布、学生风险表格和单个学生状态评估报告。

## 安装依赖

```bash
pip install -r requirements.txt
```

Windows 环境建议使用 `opencv-contrib-python`，不要安装 `face-recognition`。`face-recognition` 依赖 `dlib`，在 Windows 和 Python 3.14 上经常需要源码编译，容易失败。

如果之前已经安装失败过，可以先清理旧依赖：

```bash
pip uninstall face-recognition dlib face-recognition-models opencv-python -y
pip install -r requirements.txt
```

## 运行方式

完整交互版需要同时启动 Python API 和 React 前端。

后端 API：

```bash
python -m app.main serve
```

默认 API 地址是 `http://127.0.0.1:8765`。

前端页面：

```bash
cd frontend
npm install
npm run dev
```

打开 Vite 输出的地址，通常是 `http://localhost:5173/`。

交互流程：

1. 进入 `Register` 页面，填写学号和姓名，连续采集 3 张人脸样本注册人脸。
2. 进入 `Live Stream` 页面，点击 `Start`，浏览器会调用摄像头并定时请求 Python API 做人脸识别签到。
3. 进入 `Records` 页面查看真实签到记录。
4. 进入 `Analytics` 页面查看真实统计。
5. 进入 `智能分析` 页面，点击 `生成演示数据`，再查看决策树模型输出的学生风险报告。

统计口径：出勤率基于成功签到人数和注册用户数计算；识别成功率基于 `success + duplicate + recognized` 与 `unknown` 计算，排除 `no_face` 空帧。

命令行演示仍可单独运行：

```bash
python -m app.main register --user-id 2026001 --name 张三 --image data/faces/zhangsan.jpg
python -m app.main run
python -m app.main stats
python -m app.main demo-checkin --user-id 2026001 --name 张三
```

Linux/macOS 也可以使用：

```bash
python3 -m app.main register --user-id 2026001 --name 张三 --image data/faces/zhangsan.jpg
python3 -m app.main run
python3 -m app.main stats
python3 -m app.main demo-checkin --user-id 2026001 --name 张三
```

说明：

- `serve` 启动浏览器前端调用的本地 API 服务
- `register` 用于命令行注册用户并重新训练 LBPH 人脸识别模型
- `run` 启动摄像头签到流程
- `stats` 输出签到统计结果
- `demo-checkin` 写入一条演示签到记录，便于在未安装摄像头依赖时验证数据链路

## 人脸训练样本

Web 注册需要用户手动采集 3 张有效人脸样本，并使用同一个 LBPH label 训练模型。每次点击“采集当前样本”时，后端会先检测画面中是否恰好有 1 张人脸；没有人脸或多人入镜时不会保存样本。三张样本建议包含正脸、轻微左/右偏转或不同光照状态，以提高识别稳定性。旧的单张样本注册方式仍然兼容命令行流程。

## 答辩重点

- 图像预处理
- Haar 人脸检测与 LBPH 特征提取
- 置信度阈值判定
- 签到状态机与防重复逻辑
- ASCII 风格显示与创新性表达
