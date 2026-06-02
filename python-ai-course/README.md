# ASCII 风格人脸识别签到系统

一个面向课堂签到场景的 Python MVP 项目，使用 OpenCV 完成人脸检测与摄像头采集，结合 LBPH 人脸识别模型实现身份识别，并提供 ASCII 风格实时预览、签到记录保存和基础统计能力。

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

Windows 环境建议使用 `opencv-contrib-python`，不要安装 `face-recognition`。`face-recognition` 依赖 `dlib`，在 Windows 和 Python 3.14 上经常需要源码编译，容易失败。

如果之前已经安装失败过，可以先清理旧依赖：

```bash
pip uninstall face-recognition dlib face-recognition-models opencv-python -y
pip install -r requirements.txt
```

## 运行方式

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

- `register` 用于注册用户并重新训练 LBPH 人脸识别模型
- `run` 启动摄像头签到流程
- `stats` 输出签到统计结果
- `demo-checkin` 写入一条演示签到记录，便于在未安装摄像头依赖时验证数据链路

## 答辩重点

- 图像预处理
- Haar 人脸检测与 LBPH 特征提取
- 置信度阈值判定
- 签到状态机与防重复逻辑
- ASCII 风格显示与创新性表达
