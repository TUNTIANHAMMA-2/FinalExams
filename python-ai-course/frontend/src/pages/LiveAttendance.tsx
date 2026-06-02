import React, { useEffect, useRef, useState } from 'react';
import { AlertTriangle, Play, ScanFace, Square, UserCheck } from 'lucide-react';
import type { RecognitionResponse } from '../api';
import { recognizeFrame } from '../api';

const ASCII_CHARS = '@#S%?*+;:,. ';
const ASCII_WIDTH = 96;
const ASCII_FRAME_INTERVAL_MS = 80;
const RECOGNITION_INTERVAL_MS = 1600;

type StreamStatus = 'idle' | 'starting' | 'running' | 'error';

function frameToAscii(video: HTMLVideoElement, canvas: HTMLCanvasElement) {
  if (!video.videoWidth || !video.videoHeight) {
    return '正在等待摄像头画面...';
  }

  const aspectRatio = video.videoHeight / video.videoWidth;
  const width = ASCII_WIDTH;
  const height = Math.max(1, Math.round(width * aspectRatio * 0.46));
  const context = canvas.getContext('2d');

  if (!context) {
    return '无法读取 Canvas 上下文';
  }

  canvas.width = width;
  canvas.height = height;
  context.drawImage(video, 0, 0, width, height);

  const { data } = context.getImageData(0, 0, width, height);
  const lines: string[] = [];

  for (let y = 0; y < height; y += 1) {
    let line = '';
    for (let x = 0; x < width; x += 1) {
      const offset = (y * width + x) * 4;
      const brightness = data[offset] * 0.299 + data[offset + 1] * 0.587 + data[offset + 2] * 0.114;
      const charIndex = Math.min(
        ASCII_CHARS.length - 1,
        Math.floor((brightness / 255) * (ASCII_CHARS.length - 1)),
      );
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
  const recognitionStatus = (() => {
    if (streamStatus === 'error') return 'error';
    if (!recognition) return streamStatus === 'running' ? 'recognizing' : 'idle';
    if (recognition.status === 'success' || recognition.status === 'duplicate') return 'success';
    if (recognition.status === 'unknown') return 'unknown';
    return 'recognizing';
  })();

  const recognitionText = (() => {
    if (streamStatus === 'error') return '摄像头异常';
    if (!recognition) return streamStatus === 'running' ? '识别中...' : '等待识别...';
    if (recognition.status === 'success') return '签到成功';
    if (recognition.status === 'duplicate') return '重复签到';
    if (recognition.status === 'no_model') return '尚未注册人脸模型';
    if (recognition.status === 'no_face') return '未检测到人脸';
    if (recognition.status === 'unknown') return '未识别用户';
    return recognition.status;
  })();

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', height: '100%' }}>
      <video ref={videoRef} playsInline muted style={{ display: 'none' }} />
      <canvas ref={asciiCanvasRef} style={{ display: 'none' }} />
      <canvas ref={captureCanvasRef} style={{ display: 'none' }} />

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 600, margin: '0 0 4px 0' }}>实时签到</h2>
          <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '0.875rem' }}>使用浏览器摄像头 + Python OpenCV API 完成人脸识别与自动签到</p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button className="btn" onClick={startCamera} disabled={streamStatus === 'starting' || streamStatus === 'running'}>
            <Play size={16} /> 启动摄像头
          </button>
          <button className="btn btn-outline" onClick={stopCamera} disabled={streamStatus === 'idle'}>
            <Square size={16} /> 停止
          </button>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '24px', flex: 1, minHeight: 0 }}>
        <div className="card" style={{ flex: 2, display: 'flex', flexDirection: 'column', padding: '0' }}>
          <div style={{ padding: '16px 24px', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontWeight: 500 }}>摄像头画面 (ASCII 渲染)</span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: streamStatus === 'running' ? 'var(--success)' : 'var(--danger)' }} />
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                {streamStatus === 'running' ? '运行中 (Live)' : '未启动 (Offline)'}
              </span>
            </div>
          </div>

          <div style={{ padding: '24px', flex: 1, display: 'flex', flexDirection: 'column' }}>
            <div className="ascii-cam" style={{ flex: 1 }}>
              <pre style={{
                fontSize: '10px',
                lineHeight: '1',
                whiteSpace: 'pre',
                fontFamily: 'var(--font-mono)',
                color: recognitionStatus === 'success' ? '#10b981' : (recognitionStatus === 'unknown' || recognitionStatus === 'error' ? '#ef4444' : '#e5e7eb'),
                transition: 'color 0.3s',
                margin: 0,
                overflow: 'hidden',
              }}>
                {asciiFrame}
              </pre>
            </div>
          </div>
        </div>

        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
            <h3 style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '24px', alignSelf: 'flex-start', width: '100%' }}>当前状态</h3>

            {recognitionStatus === 'success' && <UserCheck size={48} color="var(--success)" style={{ marginBottom: '16px' }} />}
            {recognitionStatus === 'unknown' || recognitionStatus === 'error' ? <AlertTriangle size={48} color="var(--danger)" style={{ marginBottom: '16px' }} /> : null}
            {recognitionStatus === 'idle' || recognitionStatus === 'recognizing' ? <ScanFace size={48} color="var(--primary)" style={{ marginBottom: '16px' }} /> : null}

            <div style={{
              fontSize: '1.25rem',
              fontWeight: 600,
              color: recognitionStatus === 'success' ? 'var(--success)' : (recognitionStatus === 'unknown' || recognitionStatus === 'error' ? 'var(--danger)' : 'var(--primary)'),
            }}>
              {recognitionText}
            </div>
            <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '8px' }}>
              FACE_COUNT: {recognition?.face_count ?? 0}
            </div>
            {errorMessage && <div style={{ color: 'var(--danger)', fontSize: '0.75rem', marginTop: '12px' }}>ERROR: {errorMessage}</div>}
          </div>

          <div className="card" style={{ flex: 1 }}>
            <h3 style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '16px' }}>识别结果</h3>

            {primary ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px' }}>姓名及学号</div>
                  <div style={{ fontSize: '1.125rem', fontWeight: 600 }}>{primary.name} ({primary.user_id})</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px' }}>签到时间</div>
                  <div style={{ fontSize: '0.875rem' }}>{primary.attendance ? `${primary.attendance.date} ${primary.attendance.time}` : 'N/A'}</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px' }}>LBPH 置信度</div>
                  <div style={{ fontSize: '0.875rem', fontWeight: 500 }}>{primary.confidence?.toFixed(2) ?? 'N/A'}</div>
                </div>
              </div>
            ) : (
              <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                暂无人员数据
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveAttendance;
