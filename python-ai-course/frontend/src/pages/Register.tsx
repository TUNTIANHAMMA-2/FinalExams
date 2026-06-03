import React, { useEffect, useRef, useState } from 'react';
import { Alert, App, Button, Card, Col, Form, Input, Row, Space, Typography, theme } from 'antd';
import { Camera } from 'lucide-react';
import { registerFace } from '../api';

type RegisterValues = { userId: string; name: string };
type SubmitResult = { type: 'success' | 'error'; text: string };

const Register: React.FC = () => {
  const { message } = App.useApp();
  const { token } = theme.useToken();

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const [cameraOn, setCameraOn] = useState(false);
  const [loading, setLoading] = useState(false);
  const [snapshot, setSnapshot] = useState('');
  const [result, setResult] = useState<SubmitResult | null>(null);

  const stopCamera = () => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setCameraOn(false);
  };

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

  const onFinish = async (values: RegisterValues) => {
    try {
      setLoading(true);
      setResult(null);
      const imageData = captureFrame();
      setSnapshot(imageData);
      const response = await registerFace(values.userId, values.name, imageData);
      setResult({ type: 'success', text: response.message });
      message.success('注册成功');
    } catch (error) {
      const text = error instanceof Error ? error.message : '注册失败';
      setResult({ type: 'error', text });
      message.error(text);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    return () => stopCamera();
  }, []);

  const previewBox: React.CSSProperties = {
    height: 300,
    borderRadius: token.borderRadius,
    background: token.colorFillQuaternary,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
  };

  return (
    <div style={{ maxWidth: 980, margin: '0 auto' }}>
      <canvas ref={canvasRef} style={{ display: 'none' }} />

      <div style={{ marginBottom: 24 }}>
        <Typography.Title level={3} style={{ margin: 0 }}>
          人脸注册
        </Typography.Title>
        <Typography.Text type="secondary">录入学生基本信息并采集面部特征模型</Typography.Text>
      </div>

      <Card>
        <Form<RegisterValues> layout="vertical" onFinish={onFinish} requiredMark="optional">
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
            <Col xs={24} md={16}>
              <Form.Item label="面部特征采集">
                <div style={{ ...previewBox, border: `2px dashed ${token.colorBorder}` }}>
                  <video
                    ref={videoRef}
                    playsInline
                    muted
                    style={{ width: '100%', height: '100%', objectFit: 'cover', display: cameraOn ? 'block' : 'none' }}
                  />
                  {!cameraOn && (
                    <Space direction="vertical" align="center" style={{ color: token.colorTextSecondary }}>
                      <Camera size={48} strokeWidth={1.5} />
                      <Typography.Text type="secondary">摄像头未开启</Typography.Text>
                      <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                        先点击“启动摄像头”，再采集并注册
                      </Typography.Text>
                    </Space>
                  )}
                </div>
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item label="最近采集">
                <div style={{ ...previewBox, border: `1px solid ${token.colorBorderSecondary}` }}>
                  {snapshot ? (
                    <img src={snapshot} alt="最近采集" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                  ) : (
                    <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                      暂无
                    </Typography.Text>
                  )}
                </div>
              </Form.Item>
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
                采集并注册
              </Button>
            </div>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default Register;
