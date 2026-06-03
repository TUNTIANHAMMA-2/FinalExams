import React, { useEffect, useRef, useState } from 'react';
import { Badge, Button, Card, Col, Descriptions, Empty, Flex, Row, Space, Typography, theme } from 'antd';
import { AlertTriangle, Play, ScanFace, Search, Square, UserCheck } from 'lucide-react';
import type { RecognitionResponse } from '../api';
import { recognizeFrame } from '../api';
import { ASCII_CHARS, ASCII_WIDTH, ASCII_FRAME_INTERVAL_MS, RECOGNITION_INTERVAL_MS } from '../constants';

type StreamStatus = 'idle' | 'starting' | 'running' | 'error';
type DisplayStatus = 'idle' | 'recognizing' | 'recognized' | 'success' | 'unknown' | 'no_face' | 'no_model' | 'error';

/**
 * 将视频帧转换为 ASCII 字符画字符串。
 * 
 * 此函数通过 Canvas 获取视频图像数据，计算像素亮度，并映射到预定义的 ASCII 字符集。
 * 同时应用了简单的边缘检测算法以增强视觉对比度。
 * 
 * @param video - 视频源 HTMLVideoElement。
 * @param canvas - 用于图像处理的 Canvas 元素。
 * @returns 转换后的 ASCII 字符字符串，各行通过换行符分隔。
 */
function frameToAscii(video: HTMLVideoElement, canvas: HTMLCanvasElement): string {
  if (!video.videoWidth || !video.videoHeight) {
    return '正在等待摄像头画面...';
  }

  const aspectRatio = video.videoHeight / video.videoWidth;
  const width = ASCII_WIDTH;
  const height = Math.max(1, Math.round(width * aspectRatio * 0.55)); // 调整比例，使画面更接近原比例
  const context = canvas.getContext('2d');

  if (!context) {
    return '无法读取 Canvas 上下文';
  }

  canvas.width = width;
  canvas.height = height;
  // 增强对比度和亮度，使 ASCII 效果更鲜明
  context.filter = 'contrast(1.5) saturate(0.5) brightness(1.2)';
  context.drawImage(video, 0, 0, width, height);
  context.filter = 'none';

  const { data } = context.getImageData(0, 0, width, height);
  const lines: string[] = [];

  for (let y = 0; y < height; y += 1) {
    let line = '';
    for (let x = 0; x < width; x += 1) {
      const offset = (y * width + x) * 4;
      // 使用简单的亮度计算
      const brightness = data[offset] * 0.2126 + data[offset + 1] * 0.7152 + data[offset + 2] * 0.0722;
      
      // 锐化边缘：检测邻近像素亮度差
      const leftOffset = (y * width + Math.max(0, x - 1)) * 4;
      const topOffset = (Math.max(0, y - 1) * width + x) * 4;
      const leftBrightness = data[leftOffset] * 0.2126 + data[leftOffset + 1] * 0.7152 + data[leftOffset + 2] * 0.0722;
      const topBrightness = data[topOffset] * 0.2126 + data[topOffset + 1] * 0.7152 + data[topOffset + 2] * 0.0722;
      
      const edge = Math.abs(brightness - leftBrightness) + Math.abs(brightness - topBrightness);
      const enhanced = Math.min(255, brightness + edge * 2.5); // 增强边缘

      const charIndex = Math.floor((enhanced / 255) * (ASCII_CHARS.length - 1));
      line += ASCII_CHARS[charIndex];
    }
    lines.push(line);
  }

  return lines.join('\n');
}

function captureImage(video: HTMLVideoElement, canvas: HTMLCanvasElement) {
  const context = canvas.getContext('2d');
  if (!context) {
    throw new Error('无法读取摄像头画面');
  }

  canvas.width = video.videoWidth || 640;
  canvas.height = video.videoHeight || 480;
  context.drawImage(video, 0, 0, canvas.width, canvas.height);
  return canvas.toDataURL('image/jpeg', 0.85);
}

const LiveAttendance: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const asciiCanvasRef = useRef<HTMLCanvasElement | null>(null);
  const captureCanvasRef = useRef<HTMLCanvasElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const asciiIntervalRef = useRef<number | null>(null);
  const recognitionIntervalRef = useRef<number | null>(null);
  const recognizingRef = useRef(false);

  const { token } = theme.useToken();

  const [streamStatus, setStreamStatus] = useState<StreamStatus>('idle');
  const [asciiFrame, setAsciiFrame] = useState('请点击右上角“启动摄像头”');
  const [recognition, setRecognition] = useState<RecognitionResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState('');

  const stopCamera = () => {
    if (asciiIntervalRef.current !== null) {
      window.clearInterval(asciiIntervalRef.current);
      asciiIntervalRef.current = null;
    }
    if (recognitionIntervalRef.current !== null) {
      window.clearInterval(recognitionIntervalRef.current);
      recognitionIntervalRef.current = null;
    }

    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    setStreamStatus('idle');
    setAsciiFrame('请点击右上角“启动摄像头”');
  };

  const recognizeCurrentFrame = async () => {
    if (recognizingRef.current || !videoRef.current || !captureCanvasRef.current) {
      return;
    }

    recognizingRef.current = true;
    try {
      const imageData = captureImage(videoRef.current, captureCanvasRef.current);
      const result = await recognizeFrame(imageData, true);
      setRecognition(result);
      setErrorMessage('');
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '识别请求失败');
    } finally {
      recognizingRef.current = false;
    }
  };

  const startCamera = async () => {
    if (!navigator.mediaDevices?.getUserMedia) {
      setStreamStatus('error');
      setErrorMessage('当前浏览器不支持摄像头 API');
      return;
    }

    try {
      setStreamStatus('starting');
      setErrorMessage('');

      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' },
        audio: false,
      });

      streamRef.current = stream;

      if (!videoRef.current || !asciiCanvasRef.current) {
        throw new Error('视频渲染节点未初始化');
      }

      videoRef.current.srcObject = stream;
      await videoRef.current.play();

      setStreamStatus('running');
      asciiIntervalRef.current = window.setInterval(() => {
        if (videoRef.current && asciiCanvasRef.current) {
          setAsciiFrame(frameToAscii(videoRef.current, asciiCanvasRef.current));
        }
      }, ASCII_FRAME_INTERVAL_MS);
      recognitionIntervalRef.current = window.setInterval(() => {
        void recognizeCurrentFrame();
      }, RECOGNITION_INTERVAL_MS);
      void recognizeCurrentFrame();
    } catch (error) {
      stopCamera();
      setStreamStatus('error');
      setErrorMessage(error instanceof Error ? error.message : '摄像头启动失败');
    }
  };

  useEffect(() => {
    return () => stopCamera();
  }, []);

  const primary = recognition?.primary_match;
  const recognitionStatus: DisplayStatus = (() => {
    if (streamStatus === 'error') return 'error';
    if (!recognition) return streamStatus === 'running' ? 'recognizing' : 'idle';
    if (recognition.status === 'recognized') return 'recognized';
    if (recognition.status === 'success' || recognition.status === 'duplicate') return 'success';
    if (recognition.status === 'no_face') return 'no_face';
    if (recognition.status === 'no_model') return 'no_model';
    if (recognition.status === 'unknown') return 'unknown';
    return 'recognizing';
  })();

  const recognitionText = (() => {
    if (streamStatus === 'error') return '摄像头异常';
    if (!recognition) return streamStatus === 'running' ? '识别中...' : '等待识别...';
    if (recognition.status === 'recognized') return '识别成功（未写入签到）';
    if (recognition.status === 'success') return '签到成功';
    if (recognition.status === 'duplicate') return '重复签到';
    if (recognition.status === 'no_model') return '尚未注册人脸模型';
    if (recognition.status === 'no_face') return '未检测到人脸';
    if (recognition.status === 'unknown') return '未识别用户';
    return recognition.status;
  })();

  const isError = recognitionStatus === 'unknown' || recognitionStatus === 'error' || recognitionStatus === 'no_model';
  const isNeutral = recognitionStatus === 'no_face' || recognitionStatus === 'idle' || recognitionStatus === 'recognizing';
  const statusColor = recognitionStatus === 'success'
    ? token.colorSuccess
    : isError
      ? token.colorError
      : recognitionStatus === 'no_face'
        ? token.colorTextSecondary
        : token.colorPrimary;
  const asciiColor = recognitionStatus === 'success'
    ? '#34d399'
    : recognitionStatus === 'recognized'
      ? '#38bdf8'
      : isError
        ? '#f87171'
        : '#e5e7eb';

  return (
    <Space direction="vertical" size={24} style={{ width: '100%' }}>
      <video ref={videoRef} playsInline muted style={{ display: 'none' }} />
      <canvas ref={asciiCanvasRef} style={{ display: 'none' }} />
      <canvas ref={captureCanvasRef} style={{ display: 'none' }} />

      <Flex justify="space-between" align="flex-start" wrap gap={16}>
        <div style={{ textAlign: 'left' }}>
          <Typography.Title level={3} style={{ margin: 0 }}>
            实时签到
          </Typography.Title>
          <Typography.Text type="secondary">
            使用浏览器摄像头 + Python OpenCV API 完成人脸识别与自动签到
          </Typography.Text>
        </div>
        <Space wrap>
          <Button
            type="primary"
            icon={<Play size={16} />}
            onClick={startCamera}
            loading={streamStatus === 'starting'}
            disabled={streamStatus === 'starting' || streamStatus === 'running'}
          >
            启动摄像头
          </Button>
          <Button icon={<Square size={16} />} onClick={stopCamera} disabled={streamStatus === 'idle'}>
            停止
          </Button>
        </Space>
      </Flex>

      <Row gutter={[24, 24]}>
        <Col xs={24} xl={16}>
          <Card
            title="摄像头画面 (ASCII 渲染)"
            extra={
              <Badge
                status={streamStatus === 'running' ? 'success' : 'error'}
                text={streamStatus === 'running' ? '运行中 (Live)' : '未启动 (Offline)'}
              />
            }
          >
            <div className="ascii-cam" style={{ minHeight: 480 }}>
              <pre style={{ color: asciiColor }}>{asciiFrame}</pre>
            </div>
          </Card>
        </Col>

        <Col xs={24} xl={8}>
          <Space direction="vertical" size={24} style={{ width: '100%' }}>
            <Card title="当前状态">
              <Flex vertical align="center" gap={4} style={{ textAlign: 'center', padding: '8px 0' }}>
                {recognitionStatus === 'success' && <UserCheck size={48} color={token.colorSuccess} />}
                {isError && <AlertTriangle size={48} color={token.colorError} />}
                {recognitionStatus === 'no_face' && <Search size={48} color={token.colorTextSecondary} />}
                {recognitionStatus === 'recognized' && <ScanFace size={48} color={token.colorPrimary} />}
                {(recognitionStatus === 'idle' || recognitionStatus === 'recognizing') && (
                  <ScanFace size={48} color={token.colorPrimary} />
                )}
                <Typography.Title level={4} style={{ color: statusColor, margin: '12px 0 0' }}>
                  {recognitionText}
                </Typography.Title>
                <Typography.Text type="secondary">FACE_COUNT: {recognition?.face_count ?? 0}</Typography.Text>
                {recognitionStatus === 'no_face' && (
                  <Typography.Text type="secondary" style={{ fontSize: 12, marginTop: 8 }}>
                    这是正常空帧状态，不计为识别异常。
                  </Typography.Text>
                )}
                {errorMessage && (
                  <Typography.Text type="danger" style={{ fontSize: 12, marginTop: 8 }}>
                    ERROR: {errorMessage}
                  </Typography.Text>
                )}
              </Flex>
            </Card>

            <Card title="识别结果">
              {primary ? (
                <Descriptions column={1} size="small" colon={false}>
                  <Descriptions.Item label="姓名及学号">
                    <Typography.Text strong>
                      {primary.name} ({primary.user_id})
                    </Typography.Text>
                  </Descriptions.Item>
                  <Descriptions.Item label="签到时间">
                    {primary.attendance ? `${primary.attendance.date} ${primary.attendance.time}` : 'N/A'}
                  </Descriptions.Item>
                  <Descriptions.Item label="LBPH 置信度">
                    {primary.confidence?.toFixed(2) ?? 'N/A'}
                  </Descriptions.Item>
                </Descriptions>
              ) : (
                <Empty
                  image={Empty.PRESENTED_IMAGE_SIMPLE}
                  description={isNeutral ? '当前没有可签到人员' : '暂无人员数据'}
                />
              )}
            </Card>
          </Space>
        </Col>
      </Row>
    </Space>
  );
};

export default LiveAttendance;
