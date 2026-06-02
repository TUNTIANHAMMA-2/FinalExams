import React, { useState } from 'react';
import { Camera, Upload, CheckCircle, AlertCircle } from 'lucide-react';

const Register: React.FC = () => {
  const [userId, setUserId] = useState('');
  const [name, setName] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setStatus('loading');
    
    // Mock API call
    setTimeout(() => {
      if (userId && name) {
        setStatus('success');
        setUserId('');
        setName('');
        // Reset after success
        setTimeout(() => setStatus('idle'), 3000);
      } else {
        setStatus('error');
        setTimeout(() => setStatus('idle'), 3000);
      }
    }, 1500);
  };

  return (
    <div style={{ maxWidth: '800px' }}>
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
                onChange={(e) => setUserId(e.target.value)} 
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
                onChange={(e) => setName(e.target.value)} 
                placeholder="e.g. 張三"
                required
              />
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label style={{ color: 'var(--cyan-color)', fontSize: '0.8rem', letterSpacing: '1px' }}>[ BIOMETRIC_CAPTURE ]</label>
            <div style={{ 
              height: '240px', 
              border: '1px dashed var(--border-color)', 
              background: 'rgba(0, 10, 0, 0.3)',
              display: 'flex', 
              flexDirection: 'column',
              alignItems: 'center', 
              justifyContent: 'center',
              color: 'var(--text-dim)',
              gap: '16px'
            }}>
              <Camera size={48} opacity={0.5} />
              <div>CAM_PREVIEW_FEED_OFFLINE</div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-dark)' }}>Please ensure subject is facing the camera directly in good lighting.</div>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid var(--border-color)', paddingTop: '24px' }}>
            <div style={{ fontSize: '0.8rem' }}>
              {status === 'success' && (
                <span className="glow-text" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <CheckCircle size={16} /> ENROLLMENT_SUCCESSFUL
                </span>
              )}
              {status === 'error' && (
                <span className="glow-error" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <AlertCircle size={16} /> ENROLLMENT_FAILED: VALIDATION_ERROR
                </span>
              )}
              {status === 'loading' && (
                <span className="glow-cyan blinker" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  EXTRACTING_FEATURES_AND_TRAINING_MODEL...
                </span>
              )}
            </div>

            <button 
              className="cyber-button"
              type="submit" 
              disabled={status === 'loading'}
            >
              <Upload size={18} /> {status === 'loading' ? 'PROCESSING...' : 'EXECUTE_ENROLLMENT'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Register;
