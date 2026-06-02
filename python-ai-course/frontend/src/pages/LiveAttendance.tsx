import React, { useState, useEffect } from 'react';

const mockAsciiFrames = [
  `
  @@@@@@@@@@@@@@@@@@@@
  @@@@@@@@....@@@@@@@@
  @@@@@..........@@@@@
  @@@@....++++....@@@@
  @@@...++++++++...@@@
  @@...++++++++++...@@
  @@...++++++++++...@@
  @@@...++++++++...@@@
  @@@@....++++....@@@@
  @@@@@..........@@@@@
  @@@@@@@@....@@@@@@@@
  @@@@@@@@@@@@@@@@@@@@
  `,
  `
  @@@@@@@@@@@@@@@@@@@@
  @@@@@@@......@@@@@@@
  @@@@............@@@@
  @@@......++......@@@
  @@....++++++++....@@
  @...++++++++++++...@
  @...++++++++++++...@
  @@....++++++++....@@
  @@@......++......@@@
  @@@@............@@@@
  @@@@@@@......@@@@@@@
  @@@@@@@@@@@@@@@@@@@@
  `
];

const LiveAttendance: React.FC = () => {
  const [frameIndex, setFrameIndex] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [status, setStatus] = useState<'idle' | 'recognizing' | 'success' | 'unknown'>('idle');
  const [recognizedUser, setRecognizedUser] = useState<string | null>(null);

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (isRunning) {
      interval = setInterval(() => {
        setFrameIndex((prev) => (prev + 1) % mockAsciiFrames.length);
        
        // Mock recognition logic
        if (Math.random() > 0.9) {
           setStatus('success');
           setRecognizedUser('张三 (2026001)');
        } else if (Math.random() > 0.95) {
           setStatus('unknown');
           setRecognizedUser(null);
        } else if (status !== 'success' && status !== 'unknown') {
           setStatus('recognizing');
           setRecognizedUser(null);
        }
      }, 500);
    }
    return () => clearInterval(interval);
  }, [isRunning, status]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 className="glow" style={{ margin: 0 }}>&gt; /live_stream</h2>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button onClick={() => { setIsRunning(true); setStatus('idle'); }}>Start</button>
          <button onClick={() => setIsRunning(false)}>Pause</button>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '32px', flex: 1 }}>
        <div style={{ 
          flex: 2, 
          border: '1px solid var(--border-color)', 
          padding: '16px',
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: '#050505'
        }}>
          <div style={{ marginBottom: '16px', color: 'var(--text-dim)', fontSize: '0.8rem' }}>
            CAMERA_01 [ASCII_RENDER_ENG_V1]
          </div>
          <div style={{ 
            flex: 1, 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            fontSize: '14px',
            lineHeight: '1.2',
            whiteSpace: 'pre',
            fontFamily: 'var(--font-mono)'
          }}>
            {isRunning ? mockAsciiFrames[frameIndex] : 'CAMERA_OFFLINE'}
          </div>
        </div>

        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div style={{ border: '1px solid var(--border-color)', padding: '16px' }}>
            <h3 style={{ fontSize: '1rem', marginBottom: '16px', color: 'var(--text-dim)' }}>STATUS</h3>
            <div style={{ 
              fontSize: '1.2rem', 
              fontWeight: 'bold',
              color: status === 'success' ? 'var(--accent-color)' : status === 'unknown' ? 'var(--error-color)' : 'var(--text-color)'
            }}>
              {status === 'idle' && 'WAITING...'}
              {status === 'recognizing' && 'RECOGNIZING...'}
              {status === 'success' && 'SIGN-IN SUCCESS'}
              {status === 'unknown' && 'UNRECOGNIZED'}
            </div>
          </div>

          <div style={{ border: '1px solid var(--border-color)', padding: '16px', flex: 1 }}>
            <h3 style={{ fontSize: '1rem', marginBottom: '16px', color: 'var(--text-dim)' }}>LAST_RECOGNIZED</h3>
            {status === 'success' && recognizedUser ? (
              <div>
                <div style={{ fontSize: '1.5rem', marginBottom: '8px' }} className="glow">{recognizedUser}</div>
                <div style={{ color: 'var(--text-dim)' }}>TIME: {new Date().toLocaleTimeString()}</div>
              </div>
            ) : (
              <div style={{ color: 'var(--text-dim)' }}>No recent data.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveAttendance;
