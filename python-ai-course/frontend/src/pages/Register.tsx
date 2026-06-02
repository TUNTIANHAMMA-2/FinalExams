import React, { useEffect, useRef, useState } from 'react';
import { AlertCircle, Camera, CheckCircle, Upload } from 'lucide-react';
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
    if (!navigator.mediaDevices?.getUserMedia) {
      setStatus('error');
      setMessage('当前浏览器不支持摄像头 API');
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' }, audio: false });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setStatus('camera');
      setMessage('CAMERA_ONLINE: 请保持正脸清晰并点击执行注册');
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
    const context = canvas.getContext('2d');
    if (!context) {
      throw new Error('无法读取画面');
    }

    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg', 0.9);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      setStatus('loading');
      setMessage('EXTRACTING_FEATURES_AND_TRAINING_MODEL...');
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
    <div style={{ maxWidth: '1000px' }}>
      <canvas ref={canvasRef} style={{ display: 'none' }} />

      <div style={{ marginBottom: '32px' }}>
        <h2 className="glow-text" style={{ margin: 0, fontSize: '1.5rem' }}>&gt; /register_identity</h2>
        <div style={{ color: 'var(--text-dim)', fontSize: '0.8rem', marginTop: '4px' }}>ENROLL NEW SUBJECT INTO RECOGNITION DATABASE</div>
      </div>

      <div className="cyber-card">
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
          <div style={{ display: 'flex', gap: '24px' }}>
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ color: 'var(--cyan-color)', fontSize: '0.8rem', letterSpacing: '1px' }}>[ SUBJECT_ID ]</label>
              <input
                className="cyber-input"
                type="text"
                value={userId}
                onChange={(event) => setUserId(event.target.value)}
                placeholder="e.g. 2026001"
                required
              />
            </div>

            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ color: 'var(--cyan-color)', fontSize: '0.8rem', letterSpacing: '1px' }}>[ FULL_NAME ]</label>
              <input
                className="cyber-input"
                type="text"
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="e.g. 张三"
                required
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 180px', gap: '16px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ color: 'var(--cyan-color)', fontSize: '0.8rem', letterSpacing: '1px' }}>[ BIOMETRIC_CAPTURE ]</label>
              <div style={{
                minHeight: '280px',
                border: '1px dashed var(--border-color)',
                background: 'rgba(0, 10, 0, 0.3)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--text-dim)',
              }}>
                <video
                  ref={videoRef}
                  playsInline
                  muted
                  style={{ width: '100%', height: '280px', objectFit: 'cover', display: status === 'camera' || status === 'loading' || status === 'success' ? 'block' : 'none' }}
                />
                {status === 'idle' && (
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
                    <Camera size={48} opacity={0.5} />
                    <div>CAM_PREVIEW_FEED_OFFLINE</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-dark)' }}>Click START_CAMERA before enrollment.</div>
                  </div>
                )}
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ color: 'var(--cyan-color)', fontSize: '0.8rem', letterSpacing: '1px' }}>[ LAST_CAPTURE ]</label>
              <div style={{ border: '1px solid var(--border-color)', minHeight: '140px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {snapshot ? <img src={snapshot} alt="Last captured face" style={{ width: '100%' }} /> : <span style={{ color: 'var(--text-dark)', fontSize: '0.75rem' }}>NO_CAPTURE</span>}
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid var(--border-color)', paddingTop: '24px' }}>
            <div style={{ fontSize: '0.8rem' }}>
              {message && status !== 'loading' && (
                <span className={status === 'error' ? 'glow-error' : 'glow-text'} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  {status === 'error' ? <AlertCircle size={16} /> : <CheckCircle size={16} />} {message}
                </span>
              )}
              {status === 'loading' && (
                <span className="glow-cyan blinker" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  EXTRACTING_FEATURES_AND_TRAINING_MODEL...
                </span>
              )}
            </div>

            <div style={{ display: 'flex', gap: '12px' }}>
              <button className="cyber-button" type="button" onClick={startCamera} disabled={status === 'loading'}>
                <Camera size={18} /> START_CAMERA
              </button>
              <button className="cyber-button" type="submit" disabled={status === 'loading' || !userId || !name}>
                <Upload size={18} /> {status === 'loading' ? 'PROCESSING...' : 'EXECUTE_ENROLLMENT'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Register;
