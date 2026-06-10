import React, { useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { Button, Card, Col, Descriptions, Empty, Flex, Row, Space, Tag, Typography, theme } from 'antd';
import { AlertTriangle, Play, ScanFace, Search, Square, UserCheck } from 'lucide-react';
import type { RecognitionResponse } from '../api';
import { recognizeFrame } from '../api';
import {
  ASCII_CHARS,
  ASCII_WIDTH,
  ASCII_FRAME_INTERVAL_MS,
  RECOGNITION_INTERVAL_MS,
  ASCII_LINE_HEIGHT,
  ASCII_CHAR_ASPECT,
} from '../constants';
import PageHeader from '../components/PageHeader';

type StreamStatus = 'idle' | 'starting' | 'running' | 'error';
type DisplayStatus = 'idle' | 'recognizing' | 'recognized' | 'success' | 'unknown' | 'no_face' | 'no_model' | 'error';

/**
 * 将视频帧转换为 ASCII 字符画字符串。
 * heightScale = 字符宽比 / 行高，使采样网格的像素比 = 视频真实比例。
 */
function frameToAscii(video: HTMLVideoElement, canvas: HTMLCanvasElement, heightScale: number): string {
  if (!video.videoWidth || !video.videoHeight) {
    return '正在等待摄像头画面...';
  }

  const aspectRatio = video.videoHeight / video.videoWidth;
  const width = ASCII_WIDTH;
  const height = Math.max(1, Math.round(width * aspectRatio * heightScale));
  const context = canvas.getContext('2d');

  if (!context) {
    return '无法读取 Canvas 上下文';
  }

  canvas.width = width;
  canvas.height = height;

  // 增强对比度，使边缘更清晰
  context.filter = 'contrast(1.6) brightness(1.1) saturate(0)';
  context.drawImage(video, 0, 0, width, height);
  context.filter = 'none';

  const { data } = context.getImageData(0, 0, width, height);
  const lines: string[] = [];

  for (let y = 0; y < height; y += 1) {
    let line = '';
    for (let x = 0; x < width; x += 1) {
      const offset = (y * width + x) * 4;
      const r = data[offset];
      const g = data[offset + 1];
      const b = data[offset + 2];

      // 基础亮度
      let brightness = r * 0.2126 + g * 0.7152 + b * 0.0722;

      // 简易边缘增强：对比左侧像素
      if (x > 0) {
        const prevOffset = (y * width + (x - 1)) * 4;
        const prevBrightness = data[prevOffset] * 0.2126 + data[prevOffset + 1] * 0.7152 + data[prevOffset + 2] * 0.0722;
        const diff = Math.abs(brightness - prevBrightness);
        brightness += diff * 0.5; // 增强边缘对比
      }

      const charIndex = Math.min(ASCII_CHARS.length - 1, Math.floor((brightness / 255) * ASCII_CHARS.length));
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

function formatErrorMessage(error: unknown, fallback: string) {
  if (error instanceof DOMException && error.name) {
    return `${error.name}: ${error.message || fallback}`;
  }
  if (error instanceof Error) {
    return error.message || fallback;
  }
  return fallback;
}

function waitForVideoReady(video: HTMLVideoElement) {
  if (video.readyState >= HTMLMediaElement.HAVE_METADATA && video.videoWidth > 0) {
    return Promise.resolve();
  }

  return new Promise<void>((resolve, reject) => {
    const cleanup = () => {
      window.clearTimeout(timeoutId);
      video.removeEventListener('loadedmetadata', handleReady);
      video.removeEventListener('canplay', handleReady);
    };
    const handleReady = () => {
      cleanup();
      resolve();
    };
    const timeoutId = window.setTimeout(() => {
      cleanup();
      reject(new Error('摄像头画面初始化超时'));
    }, 4000);

    video.addEventListener('loadedmetadata', handleReady, { once: true });
    video.addEventListener('canplay', handleReady, { once: true });
  });
}

async function requestCameraStream() {
  const registerPageConstraints: MediaStreamConstraints = {
    video: { facingMode: 'user' },
    audio: false,
  };
  const fallbackConstraints: MediaStreamConstraints = {
    video: true,
    audio: false,
  };

  try {
    return await navigator.mediaDevices.getUserMedia(registerPageConstraints);
  } catch (error) {
    const isPermissionError =
      error instanceof DOMException && (error.name === 'NotAllowedError' || error.name === 'SecurityError');
    if (isPermissionError) {
      throw error;
    }
    return navigator.mediaDevices.getUserMedia(fallbackConstraints);
  }
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

  // ===== ASCII 自适应：实测容器宽度 + 实测等宽字符宽比 =====
  const asciiBoxRef = useRef<HTMLDivElement | null>(null);
  const [boxWidth, setBoxWidth] = useState(0);
  const [maxHeight, setMaxHeight] = useState(540); // ASCII 画面高度上限，运行时按视口实测
  const [charAspect, setCharAspect] = useState(ASCII_CHAR_ASPECT);
  const heightScaleRef = useRef(ASCII_CHAR_ASPECT / ASCII_LINE_HEIGHT);

  useEffect(() => {
    heightScaleRef.current = charAspect / ASCII_LINE_HEIGHT;
  }, [charAspect]);

  // 一次性测量等宽字符真实宽高比，消除横向拉伸残差
  useEffect(() => {
    const frameId = window.requestAnimationFrame(() => {
      const probe = document.createElement('pre');
      probe.textContent = 'M'.repeat(100);
      probe.style.cssText =
        'position:absolute;visibility:hidden;left:-9999px;top:0;margin:0;white-space:pre;' +
        `font-family:var(--font-mono);font-size:100px;line-height:${ASCII_LINE_HEIGHT};letter-spacing:0;`;
      document.body.appendChild(probe);
      const advance = probe.getBoundingClientRect().width / 100 / 100; // px/字符 ÷ 字号 → em 比
      document.body.removeChild(probe);
      if (advance > 0.2 && advance < 1.2) {
        setCharAspect(advance);
      }
    });

    return () => window.cancelAnimationFrame(frameId);
  }, []);

  // 跟随 ASCII 容器宽度变化（高度由 JS 按画面自然比例设定）
  useEffect(() => {
    const el = asciiBoxRef.current;
    if (!el) return;
    const observer = new ResizeObserver((entries) => {
      const width = entries[0]?.contentRect.width;
      if (width) {
        setBoxWidth(width);
      }
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  // ASCII 画面的高度上限 = 视口高 − 画面区顶部位置 − 下方留白，
  // 让相机面板始终落在首屏内、绝不超出 100vh（画面区顶已含页头与相机头条）。
  // 仅在挂载与窗口尺寸变化时实测；画面区顶不随自身高度变化，故无回环。
  useLayoutEffect(() => {
    const VERTICAL_RESERVE = 88; // 画面与下方卡片之间的呼吸留白
    const measure = () => {
      const el = asciiBoxRef.current;
      if (!el) return;
      const top = el.getBoundingClientRect().top;
      const available = window.innerHeight - top - VERTICAL_RESERVE;
      setMaxHeight(Math.max(280, available)); // 不低于 280，保证小窗口仍可用
    };
    measure();
    window.addEventListener('resize', measure);
    return () => window.removeEventListener('resize', measure);
  }, []);

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
      setAsciiFrame('正在请求摄像头权限...');

      const stream = await requestCameraStream();

      streamRef.current = stream;

      if (!videoRef.current || !asciiCanvasRef.current) {
        throw new Error('视频渲染节点未初始化');
      }

      videoRef.current.srcObject = stream;
      setAsciiFrame('正在初始化摄像头画面...');
      await videoRef.current.play();
      await waitForVideoReady(videoRef.current);

      setStreamStatus('running');
      setAsciiFrame(frameToAscii(videoRef.current, asciiCanvasRef.current, heightScaleRef.current));
      asciiIntervalRef.current = window.setInterval(() => {
        if (videoRef.current && asciiCanvasRef.current) {
          setAsciiFrame(frameToAscii(videoRef.current, asciiCanvasRef.current, heightScaleRef.current));
        }
      }, ASCII_FRAME_INTERVAL_MS);
      recognitionIntervalRef.current = window.setInterval(() => {
        void recognizeCurrentFrame();
      }, RECOGNITION_INTERVAL_MS);
      void recognizeCurrentFrame();
    } catch (error) {
      stopCamera();
      setStreamStatus('error');
      setErrorMessage(formatErrorMessage(error, '摄像头启动失败'));
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
    ? '#86efac'
    : isError
      ? '#fca5a5'
      : '#d4d4d8';

  const beaconClass =
    recognitionStatus === 'success' || recognitionStatus === 'recognized'
      ? 'beacon--live'
      : isError
        ? 'beacon--alert'
        : streamStatus === 'running'
          ? 'beacon--scan'
          : 'beacon--idle is-static';

  // 字号取「按容器宽铺满」与「按视口高上限铺满」中的较小值（object-fit: contain）：
  // 画面在 (boxWidth × maxHeight) 内等比完整显示，绝不超出视口高度。
  // 普通/竖屏由宽度收口 → 满宽无黑边（行为不变）；
  // 宽屏由高度收口 → 画面在黑色面板内水平居中，形成自然 pillarbox。
  const asciiLayout = useMemo(() => {
    const lines = asciiFrame.split('\n');
    const rows = lines.length;
    const cols = lines.reduce((max, line) => Math.max(max, line.length), 0);
    const isGrid = rows >= 8 && cols >= 8 && boxWidth > 0;
    if (!isGrid) {
      // 占位文案：4:3 盒子，同样受视口高度上限约束
      const height = Math.min(boxWidth > 0 ? boxWidth * 0.75 : 360, maxHeight);
      return { fontSize: 14, lineHeight: 1.5, height };
    }
    const fontByWidth = boxWidth / (cols * charAspect);
    const fontByHeight = maxHeight / (rows * ASCII_LINE_HEIGHT);
    const fontSize = Math.max(1, Math.min(fontByWidth, fontByHeight));
    const height = rows * ASCII_LINE_HEIGHT * fontSize;
    return { fontSize, lineHeight: ASCII_LINE_HEIGHT, height };
  }, [asciiFrame, boxWidth, charAspect, maxHeight]);

  return (
    <Space direction="vertical" size={24} style={{ width: '100%' }}>
      <video
        ref={videoRef}
        playsInline
        muted
        style={{
          position: 'fixed',
          left: 0,
          top: 0,
          width: 1,
          height: 1,
          opacity: 0,
          pointerEvents: 'none',
        }}
      />
      <canvas ref={asciiCanvasRef} style={{ display: 'none' }} />
      <canvas ref={captureCanvasRef} style={{ display: 'none' }} />

      <PageHeader
        title="实时监控"
        kicker="Live · Real-time"
        subtitle="基于 OpenCV 与 ASCII 渲染的实时人脸识别签到"
        actions={
          <>
            <Button
              type="primary"
              icon={<Play size={16} />}
              onClick={startCamera}
              loading={streamStatus === 'starting'}
              disabled={streamStatus === 'starting' || streamStatus === 'running'}
              style={{ height: 40, paddingInline: 22 }}
            >
              启动摄像头
            </Button>
            <Button
              icon={<Square size={16} />}
              onClick={stopCamera}
              disabled={streamStatus === 'idle'}
              style={{ height: 40 }}
            >
              停止
            </Button>
          </>
        }
      />

      {/* 相机区：整行满宽 */}
      <div className="camera-viewport-container">
        <div className="camera-header-accessory">
          <div className="camera-chip">
            <span className={`beacon ${streamStatus === 'running' ? 'beacon--live' : 'beacon--idle'}`} />
            {streamStatus === 'running' ? '实时画面' : '摄像头待机'}
          </div>
          <div className="camera-chip">人脸&nbsp;{recognition?.face_count ?? 0}</div>
        </div>
        <div
          className="ascii-cam"
          ref={asciiBoxRef}
          style={{ flex: 'none', padding: 0, minHeight: 0, height: asciiLayout.height, maxHeight }}
        >
          <pre
            style={{
              color: asciiColor,
              fontSize: `${asciiLayout.fontSize}px`,
              lineHeight: asciiLayout.lineHeight,
            }}
          >
            {asciiFrame}
          </pre>
        </div>
      </div>

      {/* 下方一行：识别状态 + 身份信息 */}
      <Row gutter={[24, 24]} align="stretch">
        <Col xs={24} md={10} lg={8}>
          <Card className="is-interactive" style={{ height: '100%' }} styles={{ body: { padding: '30px 24px' } }}>
            <Flex vertical align="center" justify="center" gap={16} style={{ textAlign: 'center', height: '100%' }}>
              <div
                style={{
                  padding: 18,
                  borderRadius: '50%',
                  background: token.colorFillSecondary,
                  color: statusColor,
                }}
              >
                {recognitionStatus === 'success' && <UserCheck size={46} />}
                {isError && <AlertTriangle size={46} />}
                {recognitionStatus === 'no_face' && <Search size={46} />}
                {(recognitionStatus === 'recognized' ||
                  recognitionStatus === 'idle' ||
                  recognitionStatus === 'recognizing') && <ScanFace size={46} />}
              </div>
              <div>
                <div
                  className="metric-label"
                  style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, marginBottom: 6 }}
                >
                  <span className={`beacon ${beaconClass}`} /> 状态
                </div>
                <Typography.Title level={4} style={{ color: statusColor, margin: 0, fontWeight: 600 }}>
                  {recognitionText}
                </Typography.Title>
                <Typography.Text className="mono" type="secondary" style={{ fontSize: 12 }}>
                  检测人脸 {recognition?.face_count ?? 0}
                </Typography.Text>
              </div>
            </Flex>
          </Card>
        </Col>

        <Col xs={24} md={14} lg={16}>
          <Card title={<span style={{ fontWeight: 600 }}>身份信息</span>} style={{ height: '100%' }}>
            {primary ? (
              <Descriptions column={{ xs: 1, sm: 2 }} size="small" colon={false}>
                <Descriptions.Item label={<span className="metric-label">姓名</span>}>
                  <Typography.Text strong style={{ fontSize: 15 }}>
                    {primary.name}
                  </Typography.Text>
                </Descriptions.Item>
                <Descriptions.Item label={<span className="metric-label">学号</span>}>
                  <span className="mono">{primary.user_id}</span>
                </Descriptions.Item>
                <Descriptions.Item label={<span className="metric-label">时间</span>}>
                  <span className="mono">
                    {primary.attendance ? `${primary.attendance.date} ${primary.attendance.time}` : '等待同步…'}
                  </span>
                </Descriptions.Item>
                <Descriptions.Item label={<span className="metric-label">置信度</span>}>
                  <Tag bordered={false} className="mono">
                    {primary.confidence?.toFixed(2) ?? 'N/A'}
                  </Tag>
                </Descriptions.Item>
              </Descriptions>
            ) : (
              <Empty
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                description={isNeutral ? '正等待扫描人脸…' : '未发现匹配数据'}
              />
            )}
          </Card>
        </Col>
      </Row>

      {errorMessage && (
        <Card
          styles={{ body: { padding: '12px 16px' } }}
          style={{ border: `1px solid ${token.colorErrorBorder}`, background: token.colorErrorBg }}
        >
          <Typography.Text type="danger" style={{ fontSize: 13 }}>
            <AlertTriangle size={14} style={{ marginRight: 8, verticalAlign: 'middle' }} />
            {errorMessage}
          </Typography.Text>
        </Card>
      )}
    </Space>
  );
};

export default LiveAttendance;
