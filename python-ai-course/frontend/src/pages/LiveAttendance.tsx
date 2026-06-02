import React, { useEffect, useRef, useState } from 'react';

const ASCII_CHARS = '@#S%?*+;:,. ';
const ASCII_WIDTH = 96;
const FRAME_INTERVAL_MS = 80;

type StreamStatus = 'idle' | 'starting' | 'running' | 'error';

function frameToAscii(video: HTMLVideoElement, canvas: HTMLCanvasElement) {
  const videoWidth = video.videoWidth;
  const videoHeight = video.videoHeight;

  if (!videoWidth || !videoHeight) {
    return 'WAITING_FOR_CAMERA_FRAME';
  }

  const aspectRatio = videoHeight / videoWidth;
  const width = ASCII_WIDTH;
  const height = Math.max(1, Math.round(width * aspectRatio * 0.46));
  const context = canvas.getContext('2d');

  if (!context) {
    return 'CANVAS_CONTEXT_UNAVAILABLE';
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
      const red = data[offset];
      const green = data[offset + 1];
      const blue = data[offset + 2];
      const brightness = red * 0.299 + green * 0.587 + blue * 0.114;
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

const LiveAttendance: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const intervalRef = useRef<number | null>(null);

  const [status, setStatus] = useState<StreamStatus>('idle');
  const [asciiFrame, setAsciiFrame] = useState('CAMERA_OFFLINE');
  const [errorMessage, setErrorMessage] = useState('');

  const stopCamera = () => {
    if (intervalRef.current !== null) {
      window.clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    setStatus('idle');
    setAsciiFrame('CAMERA_OFFLINE');
  };

  const startCamera = async () => {
    if (!navigator.mediaDevices?.getUserMedia) {
      setStatus('error');
      setErrorMessage('当前浏览器不支持摄像头 API');
      return;
    }

    try {
      setStatus('starting');
      setErrorMessage('');

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user',
        },
        audio: false,
      });

      streamRef.current = stream;

      if (!videoRef.current || !canvasRef.current) {
        throw new Error('视频渲染节点未初始化');
      }

      videoRef.current.srcObject = stream;
      await videoRef.current.play();

      setStatus('running');
      intervalRef.current = window.setInterval(() => {
        if (videoRef.current && canvasRef.current) {
          setAsciiFrame(frameToAscii(videoRef.current, canvasRef.current));
        }
      }, FRAME_INTERVAL_MS);
    } catch (error) {
      stopCamera();
      setStatus('error');
      setErrorMessage(error instanceof Error ? error.message : '摄像头启动失败');
    }
  };

  useEffect(() => {
    return () => stopCamera();
  }, []);

  const statusLabel = {
    idle: 'CAMERA_OFFLINE',
    starting: 'REQUESTING_CAMERA',
    running: 'CAMERA_STREAMING',
    error: 'CAMERA_ERROR',
  }[status];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <video ref={videoRef} playsInline muted style={{ display: 'none' }} />
      <canvas ref={canvasRef} style={{ display: 'none' }} />

      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 className="glow" style={{ margin: 0 }}>&gt; /live_stream</h2>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button onClick={startCamera} disabled={status === 'starting' || status === 'running'}>Start</button>
          <button onClick={stopCamera} disabled={status === 'idle'}>Stop</button>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '32px', flex: 1 }}>
        <div style={{
          flex: 2,
          border: '1px solid var(--border-color)',
          padding: '16px',
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: '#050505',
          overflow: 'hidden',
        }}>
          <div style={{ marginBottom: '16px', color: 'var(--text-dim)', fontSize: '0.8rem' }}>
            BROWSER_CAMERA [ASCII_RENDER_REALTIME]
          </div>
          <pre style={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '10px',
            lineHeight: '1',
            whiteSpace: 'pre',
            fontFamily: 'var(--font-mono)',
            overflow: 'hidden',
            color: 'var(--text-color)',
          }}>
            {asciiFrame}
          </pre>
        </div>

        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div style={{ border: '1px solid var(--border-color)', padding: '16px' }}>
            <h3 style={{ fontSize: '1rem', marginBottom: '16px', color: 'var(--text-dim)' }}>STATUS</h3>
            <div style={{
              fontSize: '1.2rem',
              fontWeight: 'bold',
              color: status === 'error' ? 'var(--error-color)' : 'var(--text-color)',
            }}>
              {statusLabel}
            </div>
          </div>

          <div style={{ border: '1px solid var(--border-color)', padding: '16px', flex: 1 }}>
            <h3 style={{ fontSize: '1rem', marginBottom: '16px', color: 'var(--text-dim)' }}>RECOGNITION</h3>
            <div style={{ color: 'var(--text-dim)' }}>
              前端当前负责调用浏览器摄像头并渲染 ASCII 画面；人脸识别签到仍由 Python OpenCV 命令行流程执行。
            </div>
            {errorMessage && (
              <div style={{ marginTop: '16px', color: 'var(--error-color)' }}>
                ERROR: {errorMessage}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveAttendance;
