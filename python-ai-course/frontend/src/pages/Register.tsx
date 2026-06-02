import React, { useState } from 'react';

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
      } else {
        setStatus('error');
      }
    }, 1500);
  };

  return (
    <div>
      <h2 className="glow" style={{ marginBottom: '24px' }}>&gt; /register_face</h2>
      
      <div style={{ 
        border: '1px solid var(--border-color)', 
        padding: '24px', 
        maxWidth: '500px',
        backgroundColor: '#050505'
      }}>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label style={{ color: 'var(--text-dim)', fontSize: '0.9rem' }}>USER_ID</label>
            <input 
              type="text" 
              value={userId} 
              onChange={(e) => setUserId(e.target.value)} 
              placeholder="e.g. 2026001"
              required
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label style={{ color: 'var(--text-dim)', fontSize: '0.9rem' }}>FULL_NAME</label>
            <input 
              type="text" 
              value={name} 
              onChange={(e) => setName(e.target.value)} 
              placeholder="e.g. 张三"
              required
            />
          </div>

          <div style={{ 
            height: '150px', 
            border: '1px dashed var(--border-color)', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            color: 'var(--text-dim)'
          }}>
            [CAMERA_PREVIEW_PLACEHOLDER]
          </div>

          <button 
            type="submit" 
            disabled={status === 'loading'}
            style={{ marginTop: '12px' }}
          >
            {status === 'loading' ? 'EXTRACTING_FEATURES...' : 'CAPTURE_AND_REGISTER'}
          </button>
        </form>

        {status === 'success' && (
          <div style={{ marginTop: '16px', color: 'var(--accent-color)' }}>
            [SUCCESS] Face registered successfully.
          </div>
        )}
        {status === 'error' && (
          <div style={{ marginTop: '16px', color: 'var(--error-color)' }}>
            [ERROR] Failed to register. Check inputs.
          </div>
        )}
      </div>
    </div>
  );
};

export default Register;
