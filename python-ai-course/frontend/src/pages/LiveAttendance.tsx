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

  const [status, setStatus] = useState<StreamStatus>('idle');
  const [asciiFrame, setAsciiFrame] = useState('\n\n    [ SIGNAL_LOST ]\n    AWAITING_CONNECTION...');
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
    setAsciiFrame('\n\n    [ SIGNAL_LOST ]\n    AWAITING_CONNECTION...');
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

  const primary = recognition?.primary_match;
  const recognitionLabel = (() => {
    if (status === 'error') return 'CAMERA_ERROR';
    if (!recognition) return status === 'running' ? 'SCANNING_FRAME...' : 'AWAITING_SUBJECT...';
    if (recognition.status === 'success') return 'ACCESS_GRANTED';
    if (recognition.status === 'duplicate') return 'DUPLICATE_SIGN_IN';
    if (recognition.status === 'no_model') return 'NO_REGISTERED_MODEL';
    if (recognition.status === 'no_face') return 'NO_FACE_DETECTED';
    if (recognition.status === 'unknown') return 'ACCESS_DENIED';
    return recognition.status.toUpperCase();
  })();

  const isPositive = recognition?.status === 'success' || recognition?.status === 'duplicate';
  const isNegative = status === 'error' || recognition?.status === 'unknown';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: '24px' }}>
      <video ref={videoRef} playsInline muted style={{ display: 'none' }} />
      <canvas ref={asciiCanvasRef} style={{ display: 'none' }} />
      <canvas ref={captureCanvasRef} style={{ display: 'none' }} />

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 className="glow-text" style={{ margin: 0, fontSize: '1.5rem' }}>&gt; /live_stream_feed</h2>
          <div style={{ color: 'var(--text-dim)', fontSize: '0.8rem', marginTop: '4px' }}>BROWSER CAMERA + PYTHON OPENCV API</div>
        </div>
        <div style={{ display: 'flex', gap: '16px' }}>
          <button className="cyber-button" onClick={startCamera} disabled={status === 'starting' || status === 'running'}>
            <Play size={16} /> INITIALIZE_CAM
          </button>
          <button className="cyber-button" onClick={stopCamera} disabled={status === 'idle'} style={{ borderColor: 'var(--warning-color)', color: status === 'running' ? 'var(--warning-color)' : 'var(--text-dark)' }}>
            <Square size={16} /> TERMINATE_CONN
          </button>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '32px', flex: 1, minHeight: 0 }}>
        <div className="cyber-card" style={{ flex: 2, display: 'flex', flexDirection: 'column', padding: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px' }}>
            <span style={{ color: 'var(--text-dim)', fontSize: '0.8rem' }}>CAM_01 [ASCII_RENDER_REALTIME]</span>
            <span style={{ color: status === 'running' ? 'var(--accent-color)' : 'var(--error-color)', fontSize: '0.8rem' }} className={status === 'running' ? 'blinker' : ''}>
              {status === 'running' ? '● LIVE' : '○ OFFLINE'}
            </span>
          </div>

          <div className="ascii-monitor" style={{ flex: 1 }}>
            <pre style={{
              fontSize: '10px',
              lineHeight: '1',
              whiteSpace: 'pre',
              fontFamily: 'var(--font-mono)',
              color: isPositive ? 'var(--accent-color)' : (isNegative ? 'var(--error-color)' : 'var(--text-color)'),
              transition: 'color 0.3s',
              overflow: 'hidden',
              margin: 0,
            }}>
              {asciiFrame}
            </pre>
          </div>
        </div>

        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div className="cyber-card" style={{ flex: 1 }}>
            <h3 style={{ fontSize: '0.9rem', marginBottom: '16px', color: 'var(--cyan-color)' }}>[ CURRENT_STATE ]</h3>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: 'calc(100% - 40px)' }}>
              {!isPositive && !isNegative && <ScanFace size={48} color="var(--cyan-color)" className={status === 'running' ? 'blinker' : ''} style={{ marginBottom: '16px' }} />}
              {isPositive && <UserCheck size={48} color="var(--accent-color)" style={{ marginBottom: '16px' }} />}
              {isNegative && <AlertTriangle size={48} color="var(--error-color)" style={{ marginBottom: '16px' }} />}
              <div className={isPositive ? 'glow-text' : (isNegative ? 'glow-error' : 'glow-cyan')} style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>
                {recognitionLabel}
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginTop: '8px' }}>
                FACE_COUNT: {recognition?.face_count ?? 0}
              </div>
              {errorMessage && <div style={{ marginTop: '12px', color: 'var(--error-color)', fontSize: '0.8rem' }}>ERROR: {errorMessage}</div>}
            </div>
          </div>

          <div className="cyber-card" style={{ flex: 1 }}>
            <h3 style={{ fontSize: '0.9rem', marginBottom: '16px', color: 'var(--cyan-color)' }}>[ SUBJECT_DATA ]</h3>
            {primary ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>IDENTITY:</div>
                  <div className="glow-text" style={{ fontSize: '1.4rem' }}>{primary.name} ({primary.user_id})</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>CONFIDENCE_SCORE:</div>
                  <div style={{ fontSize: '1rem', color: 'var(--cyan-color)' }}>{primary.confidence?.toFixed(2) ?? 'N/A'} [LBPH]</div>
                </div>
                {primary.attendance && (
                  <div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>TIMESTAMP:</div>
                    <div style={{ fontSize: '1rem' }}>{primary.attendance.date} {primary.attendance.time}</div>
                  </div>
                )}
              </div>
            ) : (
              <div style={{ color: 'var(--text-dark)', display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center' }}>
                NO_VALID_DATA_IN_BUFFER
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveAttendance;
