import React, { useEffect, useRef, useState } from 'react';
import { Alert, App, Button, Card, Col, Form, Input, Row, Space, Typography, theme } from 'antd';
import { Camera, RotateCcw, UserPlus } from 'lucide-react';
import { registerFace, validateFaceSample } from '../api';
import { useThemeMode } from '../theme/themeContext';
import PageHeader from '../components/PageHeader';

type RegisterValues = { userId: string; name: string };
type SubmitResult = { type: 'success' | 'error'; text: string };

const REQUIRED_SAMPLE_COUNT = 3;
const SAMPLE_HINTS = ['正脸', '左偏', '右偏'];

const Register: React.FC = () => {
  const { message } = App.useApp();
  const { token } = theme.useToken();
  const { mode } = useThemeMode();

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const [cameraOn, setCameraOn] = useState(false);
  const [loading, setLoading] = useState(false);
  const [capturing, setCapturing] = useState(false);
  const [snapshots, setSnapshots] = useState<string[]>([]);
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

  const resetSamples = () => {
    setSnapshots([]);
    setResult(null);
  };

  const captureSample = async () => {
    try {
      setCapturing(true);
      setResult(null);
      const imageData = captureFrame();
      const validation = await validateFaceSample(imageData);
      if (!validation.valid) {
        setResult({ type: 'error', text: validation.message });
        message.warning(validation.message);
        return;
      }

      setSnapshots((prev) => [...prev, imageData].slice(0, REQUIRED_SAMPLE_COUNT));
      message.success(`样本 ${snapshots.length + 1} / ${REQUIRED_SAMPLE_COUNT} 采集成功`);
    } catch (error) {
      const text = error instanceof Error ? error.message : '样本采集失败';
      setResult({ type: 'error', text });
      message.error(text);
    } finally {
      setCapturing(false);
    }
  };

  const onFinish = async (values: RegisterValues) => {
    try {
      setLoading(true);
      setResult(null);

      if (snapshots.length !== REQUIRED_SAMPLE_COUNT) {
        throw new Error(`请先手动采集 ${REQUIRED_SAMPLE_COUNT} 张有效人脸样本`);
      }

      const response = await registerFace(values.userId, values.name, snapshots);
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
    borderRadius: 0,
    background: mode === 'dark' ? 'rgba(255,255,255,0.04)' : 'rgba(15,23,42,0.025)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
    border: `1px solid ${token.colorBorderSecondary}`,
    transition: 'all 0.25s ease',
  };

  return (
    <Space direction="vertical" size={24} style={{ width: '100%' }}>
      <canvas ref={canvasRef} style={{ display: 'none' }} />

      <PageHeader
        title="新用户注册"
        kicker="Enrollment"
        subtitle="录入学生信息并采集面部多角度特征模型"
      />

      <Form<RegisterValues> layout="vertical" onFinish={onFinish} requiredMark="optional">
        <Row gutter={[24, 24]}>
          <Col xs={24} lg={15}>
            <Card title={<span style={{ fontWeight: 600 }}>特征采集窗口</span>}>
              <div
                className="camera-viewport-container"
                style={{ height: 440, position: 'relative', borderRadius: 0 }}
              >
                <div className="ascii-cam" style={{ padding: 0, background: '#0a0a0a', minHeight: 0, height: '100%' }}>
                  <video
                    ref={videoRef}
                    playsInline
                    muted
                    style={{
                      width: '100%',
                      height: '100%',
                      objectFit: 'cover',
                      display: cameraOn ? 'block' : 'none',
                    }}
                  />
                  {!cameraOn && (
                    <Space direction="vertical" align="center" style={{ color: '#a1a1aa' }}>
                      <Camera size={56} strokeWidth={1.4} />
                      <span style={{ fontSize: 12 }}>摄像头待机</span>
                    </Space>
                  )}
                  {cameraOn && (
                    <div
                      style={{
                        position: 'absolute',
                        top: 16,
                        right: 16,
                        display: 'flex',
                        alignItems: 'center',
                        gap: 8,
                        padding: '5px 11px',
                        borderRadius: 0,
                        background: 'rgba(0,0,0,0.55)',
                      }}
                    >
                      <span className="beacon beacon--live" />
                      <span style={{ color: '#fff', fontSize: 11 }}>实时</span>
                    </div>
                  )}
                </div>
              </div>
              <div style={{ marginTop: 16, display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
                <Button onClick={startCamera} disabled={cameraOn} style={{ height: 40 }}>
                  启动预览
                </Button>
                <Button
                  type="primary"
                  icon={<Camera size={16} />}
                  onClick={() => void captureSample()}
                  loading={capturing}
                  disabled={!cameraOn || snapshots.length >= REQUIRED_SAMPLE_COUNT}
                  style={{ height: 40, paddingInline: 22 }}
                >
                  采集快照
                </Button>
                <Button
                  icon={<RotateCcw size={16} />}
                  onClick={resetSamples}
                  disabled={snapshots.length === 0}
                  style={{ height: 40 }}
                >
                  重置样本
                </Button>
              </div>
            </Card>
          </Col>

          <Col xs={24} lg={9}>
            <Space direction="vertical" size={16} style={{ width: '100%' }}>
              <Card title={<span style={{ fontWeight: 600 }}>基本资料</span>}>
                <Form.Item label="学号 (User ID)" name="userId" rules={[{ required: true, message: '请输入学号' }]}>
                  <Input size="large" placeholder="例如: 2026001" variant="filled" />
                </Form.Item>
                <Form.Item label="姓名 (Full Name)" name="name" rules={[{ required: true, message: '请输入姓名' }]} style={{ marginBottom: 0 }}>
                  <Input size="large" placeholder="例如: 张三" variant="filled" />
                </Form.Item>
              </Card>

              <Card
                title={
                  <span style={{ fontWeight: 600 }}>
                    采集进度{' '}
                    <span className="mono" style={{ color: token.colorPrimary }}>
                      {snapshots.length}/{REQUIRED_SAMPLE_COUNT}
                    </span>
                  </span>
                }
              >
                <Row gutter={12}>
                  {[0, 1, 2].map((i) => (
                    <Col key={i} span={8}>
                      <div
                        style={{
                          ...previewBox,
                          minHeight: 96,
                          borderStyle: snapshots[i] ? 'solid' : 'dashed',
                          borderColor: snapshots[i] ? token.colorPrimary : token.colorBorderSecondary,
                          background: snapshots[i] ? '#000' : 'transparent',
                          position: 'relative',
                        }}
                      >
                        {snapshots[i] ? (
                          <img
                            src={snapshots[i]}
                            alt={`样本${i + 1}`}
                            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                          />
                        ) : (
                          <span className="mono" style={{ color: token.colorTextTertiary, fontSize: 18, fontWeight: 600 }}>
                            {String(i + 1).padStart(2, '0')}
                          </span>
                        )}
                      </div>
                      <div
                        className="mono"
                        style={{ textAlign: 'center', fontSize: 11, marginTop: 6, color: token.colorTextSecondary }}
                      >
                        {SAMPLE_HINTS[i]}
                      </div>
                    </Col>
                  ))}
                </Row>
                <Typography.Text type="secondary" style={{ fontSize: 12, display: 'block', marginTop: 14 }}>
                  提示：请采集正脸、左偏、右偏三个角度以提高识别率。
                </Typography.Text>
              </Card>

              {result && <Alert type={result.type} showIcon message={result.text} />}

              <Button
                type="primary"
                htmlType="submit"
                size="large"
                block
                icon={<UserPlus size={18} />}
                loading={loading}
                disabled={snapshots.length !== REQUIRED_SAMPLE_COUNT || capturing}
                style={{ height: 52, fontSize: 16, fontWeight: 500 }}
              >
                完成并保存注册
              </Button>
            </Space>
          </Col>
        </Row>
      </Form>
    </Space>
  );
};

export default Register;
