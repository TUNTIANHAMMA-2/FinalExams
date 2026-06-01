# ASCII 风格人脸识别签到系统

一个面向课堂签到场景的 Python MVP 项目，使用 OpenCV 完成人脸检测与摄像头采集，结合人脸特征编码实现身份识别，并提供 ASCII 风格实时预览、签到记录保存和基础统计能力。

## 当前范围

- 人脸注册
- 实时识别
- 自动签到
- 防重复打卡
- ASCII 风格预览
- 签到记录保存
- 基础统计

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
  ascii_render.py
  storage.py
  analytics.py
data/
  faces/
  encodings/
  exports/
docs/
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行方式

```bash
python3 -m app.main register --user-id 2026001 --name 张三 --image data/faces/zhangsan.jpg
python3 -m app.main run
python3 -m app.main stats
python3 -m app.main demo-checkin --user-id 2026001 --name 张三
```

说明：

- `register` 用于注册用户并生成人脸编码
- `run` 启动摄像头签到流程
- `stats` 输出签到统计结果
- `demo-checkin` 写入一条演示签到记录，便于在未安装摄像头依赖时验证数据链路

## 答辩重点

- 图像预处理
- 人脸检测与特征提取
- 相似度匹配和阈值判定
- 签到状态机与防重复逻辑
- ASCII 风格显示与创新性表达
