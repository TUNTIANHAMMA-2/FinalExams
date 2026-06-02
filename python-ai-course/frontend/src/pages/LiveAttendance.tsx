import React, { useEffect, useRef, useState } from 'react';
import type { RecognitionResponse } from '../api';
import { recognizeFrame } from '../api';

const ASCII_CHARS = '@#S%?*+;:,. ';
const ASCII_WIDTH = 96;
const ASCII_FRAME_INTERVAL_MS = 80;
const RECOGNITION_INTERVAL_MS = 1600;

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

function captureImage(video: HTMLVideoElement, canvas: HTMLCanvasElement) {
  const videoWidth = video.videoWidth || 640;
  const videoHeight = video.videoHeight || 480;
  const context = canvas.getContext('2d');

  if (!context) {
    throw new Error('无法读取摄像头画面');
  }

  canvas.width = videoWidth;
  canvas.height = videoHeight;
  context.drawImage(video, 0, 0, videoWidth, videoHeight);
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

  const [status, setStatus] = useState<StreamStatus>('idle');
  const [asciiFrame, setAsciiFrame] = useState('CAMERA_OFFLINE');
  const [errorMessage, setErrorMessage] = useState('');
  const [recognition, setRecognition] = useState<RecognitionResponse | null>(null);

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

    setStatus('idle');
    setAsciiFrame('CAMERA_OFFLINE');
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
      setStatus('error');
      setErrorMessage('当前浏览器不支持摄像头 API');
      return;
    }

    try {
      setStatus('starting');
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

      setStatus('running');
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

  const primary = recognition?.primary_match;
  const recognitionLabel = (() => {
    if (!recognition) return 'WAITING_FOR_FRAME';
    if (recognition.status === 'success') return 'SIGN_IN_SUCCESS';
    if (recognition.status === 'duplicate') return 'DUPLICATE_SIGN_IN';
    if (recognition.status === 'no_model') return 'NO_REGISTERED_MODEL';
    if (recognition.status === 'no_face') return 'NO_FACE_DETECTED';
    if (recognition.status === 'unknown') return 'UNKNOWN_FACE';
    return recognition.status.toUpperCase();
  })();

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <video ref={videoRef} playsInline muted style={{ display: 'none' }} />
      <canvas ref={asciiCanvasRef} style={{ display: 'none' }} />
      <canvas ref={captureCanvasRef} style={{ display: 'none' }} />

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
            <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: status === 'error' ? 'var(--error-color)' : 'var(--text-color)' }}>
              {statusLabel}
            </div>
          </div>

          <div style={{ border: '1px solid var(--border-color)', padding: '16px', flex: 1 }}>
            <h3 style={{ fontSize: '1rem', marginBottom: '16px', color: 'var(--text-dim)' }}>RECOGNITION</h3>
            <div style={{ fontSize: '1.2rem', color: recognition?.status === 'unknown' ? 'var(--error-color)' : 'var(--accent-color)' }}>
              {recognitionLabel}
            </div>
            <div style={{ marginTop: '12px', color: 'var(--text-dim)' }}>FACE_COUNT: {recognition?.face_count ?? 0}</div>
            {primary && (
              <div style={{ marginTop: '16px' }}>
                <div className="glow" style={{ fontSize: '1.4rem' }}>{primary.name} ({primary.user_id})</div>
                <div style={{ color: 'var(--text-dim)' }}>CONFIDENCE: {primary.confidence?.toFixed(2) ?? 'N/A'}</div>
                {primary.attendance && (
                  <div style={{ color: 'var(--text-dim)' }}>TIME: {primary.attendance.date} {primary.attendance.time}</div>
                )}
              </div>
            )}
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
