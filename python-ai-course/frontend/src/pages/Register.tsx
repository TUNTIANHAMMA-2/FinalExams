import React, { useEffect, useRef, useState } from 'react';
import { Alert, App, Button, Card, Col, Form, Input, Row, Space, Typography, theme } from 'antd';
import { Camera } from 'lucide-react';
import { registerFace } from '../api';

type RegisterValues = { userId: string; name: string };
type SubmitResult = { type: 'success' | 'error'; text: string };

const REQUIRED_SAMPLE_COUNT = 3;
const SAMPLE_CAPTURE_DELAY_MS = 650;

function wait(ms: number) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}

const Register: React.FC = () => {
  const { message } = App.useApp();
  const { token } = theme.useToken();

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const [cameraOn, setCameraOn] = useState(false);
  const [loading, setLoading] = useState(false);
  const [snapshots, setSnapshots] = useState<string[]>([]);
  const [sampleProgress, setSampleProgress] = useState(0);
  const [result, setResult] = useState<SubmitResult | null>(null);

  /**
   * 关闭摄像头并停止所有活动轨道。
   * 
   * 该函数会遍历 `streamRef` 持有的所有媒体轨道并显式调用 `stop()`，
   * 同时清空 `srcObject` 以重置 `<video>` 标签状态，并将 `cameraOn` 状态重置为 `false`。
   */
  const stopCamera = () => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setCameraOn(false);
  };

  /**
   * 请求用户媒体设备权限并初始化摄像头预览。
   * 
   * 成功获取流后，将其绑定至 `videoRef` 并触发播放。
   * 如果用户拒绝权限或浏览器不支持 `getUserMedia`，将通过 Antd message 提示错误。
   * 
   * @throws 摄像头不可用、用户拒绝授权等 MediaDevices 异常。
   */
  const startCamera = async () => {
    if (!navigator.mediaDevices?.getUserMedia) {
      message.error('当前浏览器不支持摄像头 API');
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' }, audio: false });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setCameraOn(true);
      setResult(null);
    } catch (error) {
      message.error(error instanceof Error ? error.message : '摄像头启动失败');
    }
  };

  /**
   * 将当前 `<video>` 标签的画面渲染到隐蔽的 `<canvas>` 并导出。
   * 
   * 采用 `image/jpeg` 格式进行编码，压缩质量设定为 0.9。
   * 此函数通常用于人脸采集逻辑，将 Canvas 内容转为 Base64 字符串供后端使用。
   * 
   * @returns 截取图像的 Base64 编码字符串。
   * @throws 若 `videoRef` 或 `canvasRef` 未挂载，或 Canvas 上下文获取失败，则抛出 Error。
   */
  const captureFrame = () => {
    if (!videoRef.current || !canvasRef.current) {
      throw new Error('摄像头画面未准备好');
    }

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');
    if (!context) {
      throw new Error('无法读取画面');
    }

    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg', 0.9);
  };

  /**
   * 处理人脸注册表单提交逻辑。
   * 
   * 包含以下核心步骤：
   * 1. 开启加载状态并重置结果。
   * 2. 连续调用 `captureFrame` 采集 3 张训练样本。
   * 3. 将采集的图像数据与表单中的 userId, name 一并发送给后端 `registerFace` API。
   * 4. 根据请求结果更新 UI 状态 (success/error)。
   * 
   * @param values - Form.Item 中定义的表单数据对象。
   */
  const onFinish = async (values: RegisterValues) => {
    try {
      setLoading(true);
      setResult(null);
      setSampleProgress(0);

      const imageDataList: string[] = [];
      for (let index = 0; index < REQUIRED_SAMPLE_COUNT; index += 1) {
        if (index > 0) {
          await wait(SAMPLE_CAPTURE_DELAY_MS);
        }
        const imageData = captureFrame();
        imageDataList.push(imageData);
        setSnapshots((prev) => [...prev, imageData]);
        setSampleProgress(index + 1);
      }

      const response = await registerFace(values.userId, values.name, imageDataList);
      setResult({ type: 'success', text: response.message });
      message.success('注册成功');
    } catch (error) {
      const text = error instanceof Error ? error.message : '注册失败';
      setResult({ type: 'error', text });
      message.error(text);
    } finally {
      setLoading(false);
      setSampleProgress(0);
    }
  };

  useEffect(() => {
    return () => stopCamera();
  }, []);

  const previewBox: React.CSSProperties = {
    minHeight: 300,
    borderRadius: token.borderRadius,
    background: token.colorFillQuaternary,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
    aspectRatio: '4 / 3', /* 强制容器保持常用摄像头比例 */
  };

  return (
    <Space direction="vertical" size={24} style={{ width: '100%' }}>
      <canvas ref={canvasRef} style={{ display: 'none' }} />

      <div style={{ textAlign: 'left' }}>
        <Typography.Title level={3} style={{ margin: 0 }}>
          人脸注册
        </Typography.Title>
        <Typography.Text type="secondary">录入学生基本信息并采集面部特征模型</Typography.Text>
      </div>

      <Card>
        <Form<RegisterValues> layout="vertical" onFinish={onFinish} requiredMark="optional">
          <Row gutter={24}>
            <Col xs={24}>
              <Form.Item label="面部特征采集">
                <div style={{ ...previewBox, border: `2px dashed ${token.colorBorder}`, height: 400, aspectRatio: 'auto' }}>
                  <video
                    ref={videoRef}
                    playsInline
                    muted
                    style={{ width: '100%', height: '100%', objectFit: 'contain', display: cameraOn ? 'block' : 'none' }}
                  />
                  {!cameraOn && (
                    <Space direction="vertical" align="center" style={{ color: token.colorTextSecondary }}>
                      <Camera size={48} strokeWidth={1.5} />
                      <Typography.Text type="secondary">摄像头未开启</Typography.Text>
                      <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                        先点击“启动摄像头”，再连续采集 3 张训练样本
                      </Typography.Text>
                    </Space>
                  )}
                </div>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={24}>
            <Col xs={24} md={12}>
              <Form.Item label="学号 (User ID)" name="userId" rules={[{ required: true, message: '请输入学号' }]}>
                <Input placeholder="例如: 2026001" allowClear />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item label="姓名 (Full Name)" name="name" rules={[{ required: true, message: '请输入姓名' }]}>
                <Input placeholder="例如: 张三" allowClear />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={24}>
            <Col xs={24}>
              <Form.Item label={`采集样本 (已采集 ${sampleProgress}/${REQUIRED_SAMPLE_COUNT})`}>
                <Row gutter={8}>
                  {[0, 1, 2].map((i) => (
                    <Col key={i} span={8}>
                      <div style={{ ...previewBox, border: `1px solid ${token.colorBorderSecondary}`, minHeight: 120 }}>
                        {snapshots[i] ? (
                          <img src={snapshots[i]} alt={`样本${i + 1}`} style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
                        ) : (
                          <Typography.Text type="secondary" style={{ fontSize: 14 }}>
                            {i + 1}
                          </Typography.Text>
                        )}
                      </div>
                    </Col>
                  ))}
                </Row>
              </Form.Item>
              <Typography.Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 16 }}>
                {loading
                  ? `正在采集第 ${Math.max(1, sampleProgress)} / ${REQUIRED_SAMPLE_COUNT} 张，请轻微调整角度`
                  : `本次注册将连续采集 ${REQUIRED_SAMPLE_COUNT} 张样本`}
              </Typography.Text>
            </Col>
          </Row>

          {result && <Alert style={{ marginBottom: 16 }} type={result.type} showIcon message={result.text} />}

          <Form.Item style={{ marginBottom: 0 }}>
            <div
              style={{
                display: 'flex',
                justifyContent: 'flex-end',
                gap: 12,
                flexWrap: 'wrap',
                borderTop: `1px solid ${token.colorBorderSecondary}`,
                paddingTop: 24,
              }}
            >
              <Button icon={<Camera size={16} />} onClick={startCamera}>
                启动摄像头
              </Button>
              <Button type="primary" htmlType="submit" icon={<Camera size={16} />} loading={loading} disabled={!cameraOn}>
                连续采集 3 张并注册
              </Button>
            </div>
          </Form.Item>
        </Form>
      </Card>
    </Space>
  );
};

export default Register;
