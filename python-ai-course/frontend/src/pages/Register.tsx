import React, { useEffect, useRef, useState } from 'react';
import { AlertCircle, Camera, CheckCircle, Loader2 } from 'lucide-react';
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
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <canvas ref={canvasRef} style={{ display: 'none' }} />

      <div style={{ marginBottom: '32px' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, margin: '0 0 8px 0' }}>人脸注册</h2>
        <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '0.875rem' }}>录入学生基本信息并采集面部特征模型</p>
      </div>

      <div className="card">
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div style={{ display: 'flex', gap: '24px' }}>
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ fontSize: '0.875rem', fontWeight: 500, color: 'var(--text-main)' }}>学号 (User ID)</label>
              <input
                className="input-field"
                type="text"
                value={userId}
                onChange={(event) => setUserId(event.target.value)}
                placeholder="例如: 2026001"
                required
              />
            </div>

            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ fontSize: '0.875rem', fontWeight: 500, color: 'var(--text-main)' }}>姓名 (Full Name)</label>
              <input
                className="input-field"
                type="text"
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="例如: 张三"
                required
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 180px', gap: '16px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ fontSize: '0.875rem', fontWeight: 500, color: 'var(--text-main)' }}>面部特征采集</label>
              <div style={{
                height: '280px',
                border: '2px dashed var(--border)',
                borderRadius: 'var(--radius)',
                backgroundColor: '#f8fafc',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--text-muted)',
                overflow: 'hidden',
              }}>
                <video
                  ref={videoRef}
                  playsInline
                  muted
                  style={{ width: '100%', height: '100%', objectFit: 'cover', display: status === 'camera' || status === 'loading' || status === 'success' ? 'block' : 'none' }}
                />
                {status === 'idle' && (
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
                    <Camera size={48} strokeWidth={1.5} />
                    <div style={{ fontWeight: 500 }}>摄像头未开启</div>
                    <div style={{ fontSize: '0.75rem' }}>先点击“启动摄像头”，再采集并注册</div>
                  </div>
                )}
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ fontSize: '0.875rem', fontWeight: 500, color: 'var(--text-main)' }}>最近采集</label>
              <div style={{ minHeight: '130px', border: '1px solid var(--border)', borderRadius: 'var(--radius)', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden' }}>
                {snapshot ? <img src={snapshot} alt="最近采集" style={{ width: '100%' }} /> : <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>暂无</span>}
              </div>
            </div>
          </div>

          {message && (
            <div style={{
              padding: '12px',
              borderRadius: '6px',
              backgroundColor: status === 'error' ? 'var(--danger-bg)' : 'var(--success-bg)',
              color: status === 'error' ? '#991b1b' : '#065f46',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '0.875rem',
            }}>
              {status === 'error' ? <AlertCircle size={18} /> : <CheckCircle size={18} />}
              {message}
            </div>
          )}

          <div style={{ borderTop: '1px solid var(--border)', paddingTop: '24px', display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
            <button className="btn btn-outline" type="button" onClick={startCamera} disabled={status === 'loading'}>
              <Camera size={16} /> 启动摄像头
            </button>
            <button className="btn" type="submit" disabled={status === 'loading' || !userId || !name}>
              {status === 'loading' ? (
                <><Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} /> 处理中...</>
              ) : (
                <><Camera size={16} /> 采集并注册</>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Register;
