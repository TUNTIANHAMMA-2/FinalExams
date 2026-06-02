import React, { useEffect, useRef, useState } from 'react';
import { registerFace } from '../api';

const Register: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const [userId, setUserId] = useState('');
  const [name, setName] = useState('');
  const [status, setStatus] = useState<'idle' | 'camera' | 'loading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');
  const [snapshot, setSnapshot] = useState('');

  const stopCamera = () => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' }, audio: false });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setStatus('camera');
      setMessage('摄像头已启动，请保持正脸清晰');
    } catch (error) {
      setStatus('error');
      setMessage(error instanceof Error ? error.message : '摄像头启动失败');
    }
  };

  const captureFrame = () => {
    if (!videoRef.current || !canvasRef.current) {
      throw new Error('摄像头画面未准备好');
    }
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const context = canvas.getContext('2d');
    if (!context) {
      throw new Error('无法读取画面');
    }
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg', 0.9);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      setStatus('loading');
      setMessage('正在检测人脸并训练 LBPH 模型...');
      const imageData = captureFrame();
      setSnapshot(imageData);
      const response = await registerFace(userId, name, imageData);
      setStatus('success');
      setMessage(response.message);
    } catch (error) {
      setStatus('error');
      setMessage(error instanceof Error ? error.message : '注册失败');
    }
  };

  useEffect(() => {
    return () => stopCamera();
  }, []);

  return (
    <div>
      <h2 className="glow" style={{ marginBottom: '24px' }}>&gt; /register_face</h2>
      <canvas ref={canvasRef} style={{ display: 'none' }} />

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(320px, 520px) 1fr', gap: '24px' }}>
        <div style={{ border: '1px solid var(--border-color)', padding: '24px', backgroundColor: '#050505' }}>
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ color: 'var(--text-dim)', fontSize: '0.9rem' }}>USER_ID</label>
              <input
                type="text"
                value={userId}
                onChange={(event) => setUserId(event.target.value)}
                placeholder="e.g. 2026001"
                required
              />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ color: 'var(--text-dim)', fontSize: '0.9rem' }}>FULL_NAME</label>
              <input
                type="text"
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="e.g. 张三"
                required
              />
            </div>

            <button type="button" onClick={startCamera} disabled={status === 'loading'}>
              START_CAMERA
            </button>
            <button type="submit" disabled={status === 'loading' || !userId || !name}>
              {status === 'loading' ? 'TRAINING_MODEL...' : 'CAPTURE_AND_REGISTER'}
            </button>
          </form>

          {message && (
            <div style={{ marginTop: '16px', color: status === 'error' ? 'var(--error-color)' : 'var(--accent-color)' }}>
              [{status.toUpperCase()}] {message}
            </div>
          )}
        </div>

        <div style={{ border: '1px solid var(--border-color)', padding: '16px', backgroundColor: '#050505' }}>
          <div style={{ marginBottom: '12px', color: 'var(--text-dim)' }}>CAMERA_PREVIEW</div>
          <video
            ref={videoRef}
            playsInline
            muted
            style={{ width: '100%', maxHeight: '360px', objectFit: 'cover', border: '1px solid var(--border-color)' }}
          />
          {snapshot && (
            <div style={{ marginTop: '16px' }}>
              <div style={{ marginBottom: '8px', color: 'var(--text-dim)' }}>LAST_CAPTURE</div>
              <img src={snapshot} alt="Last captured face" style={{ width: '180px', border: '1px solid var(--border-color)' }} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Register;
