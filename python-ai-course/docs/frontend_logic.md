# 前端逻辑设计

本项目的前端样式可以独立设计，当前文档只约定页面职责、数据流和交互逻辑。

## 1. 页面结构

### 1.1 实时签到页

核心区域：

- ASCII 摄像头预览
- 当前识别身份
- 当前签到状态
- 当前时间
- 操作按钮：开始、暂停、退出

状态：

- 未检测到人脸
- 识别中
- 签到成功
- 已签到
- 未注册用户

### 1.2 人脸注册页

核心区域：

- 学号输入
- 姓名输入
- 摄像头拍照或图片上传
- 注册结果提示

交互流程：

1. 输入学号和姓名
2. 采集人脸图片
3. 后端检测是否存在有效人脸
4. 保存人脸特征
5. 返回注册成功或失败原因

### 1.3 签到记录页

核心区域：

- 日期筛选
- 姓名筛选
- 签到记录表格
- 识别事件表格
- 从后端导出 CSV 按钮

签到记录字段：

- 日期
- 时间
- 学号
- 姓名
- 状态
- 置信度
- 事件 ID

识别事件字段：

- 事件 ID
- 时间
- 事件类型
- 学号/姓名
- 置信度
- 人脸数量
- 说明

### 1.4 数据分析页

核心区域：

- 今日签到人数
- 重复签到次数
- 未知人脸次数
- 出勤率
- 识别成功率
- 识别事件类型分布
- 用户签到排行
- 签到趋势图预留位

### 1.5 智能分析页

核心区域：

- 生成演示班级数据按钮
- 训练学生风险模型按钮
- 刷新分析按钮
- 模型状态、学生数、高风险人数、训练样本数
- 学生风险预测表格
- 风险等级分布
- 学生状态评估报告

交互流程：

1. 点击生成演示数据，后端写入学生、成绩、考勤事件和训练样本。
2. 后端使用训练样本训练决策树分类模型并保存模型文件。
3. 前端刷新分析接口，读取每名学生的风险等级、风险分值和报告文本。
4. 用户点击表格中的学生，右侧展示该学生的特征明细和干预建议。

## 2. 前后端接口草案

### 2.1 注册接口

```text
POST /api/register
```

请求数据：

```json
{
  "user_id": "2026001",
  "name": "张三",
  "image": "base64 image"
}
```

返回数据：

```json
{
  "success": true,
  "message": "注册成功"
}
```

### 2.2 实时识别接口

```text
POST /api/recognize
```

请求数据：

```json
{
  "image_data": "data:image/jpeg;base64,...",
  "mark_attendance": true
}
```

返回数据：

```json
{
  "status": "success",
  "face_count": 1,
  "event": {
    "event_id": "20260603101530000000-0001",
    "event_type": "success",
    "message": "签到成功"
  },
  "primary_match": {
    "name": "张三",
    "user_id": "2026001",
    "confidence": 42.1
  }
}
```

说明：`no_face` 表示未检测到人脸，是正常空帧状态，不展示为识别异常，也不写入事件日志。

### 2.3 识别事件接口

```text
GET /api/events
```

返回数据：

```json
{
  "events": []
}
```

### 2.4 统计接口

```text
GET /api/stats
```

返回数据：

```json
{
  "total_records": 10,
  "status_counts": {
    "success": 8
  },
  "event_total": 12,
  "event_counts": {
    "success": 8,
    "duplicate": 2,
    "unknown": 2
  },
  "attendance_rate": 0.8,
  "recognition_success_rate": 0.8333
}
```

### 2.5 智能分析接口

```text
POST /api/student-analysis/demo-data
POST /api/student-analysis/train
GET /api/student-analysis
```

分析接口返回数据：

```json
{
  "model_ready": true,
  "student_count": 5,
  "training_samples": 85,
  "risk_counts": {
    "低风险": 1,
    "中风险": 2,
    "高风险": 2
  },
  "students": [
    {
      "user_id": "2026003",
      "name": "王五",
      "risk_level": "高风险",
      "risk_score": 100,
      "confidence": 1,
      "features": {
        "attendance_rate_30d": 0.6667,
        "late_count_7d": 4,
        "absent_count_30d": 10,
        "duplicate_count_30d": 2,
        "avg_score": 70.5,
        "score_delta": -17
      },
      "summary": "王五近30天出勤率为66.7%，近7天迟到4次，最近一次成绩变化为-17.0分，系统评估为高风险。",
      "suggestion": "建议老师尽快进行学习状态沟通，并重点关注到课情况和近期成绩变化。"
    }
  ]
}
```

## 3. 给样式实现者的说明

视觉方向建议：

- 整体风格偏科技感和终端感
- ASCII 画面作为第一视觉中心
- 识别状态需要清晰突出
- 不要让装饰样式遮挡签到状态
- 数据页面以可读性优先

前端只需要按以上页面逻辑实现样式，后端接口可在后续开发时对接。
