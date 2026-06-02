import React, { useState, useEffect } from 'react';
import { Play, Square, ScanFace, UserCheck, AlertTriangle } from 'lucide-react';

const mockAsciiFrames = [
  `
  @@@@@@@@@@@@@@@@@@@@@@@@@@
  @@@@@@@@@@......@@@@@@@@@@
  @@@@@@..............@@@@@@
  @@@@@.......++.......@@@@@
  @@@@....++++++++++....@@@@
  @@@...++++++++++++++...@@@
  @@...++++++++++++++++...@@
  @@...++++++++++++++++...@@
  @@@...++++++++++++++...@@@
  @@@@....++++++++++....@@@@
  @@@@@.......++.......@@@@@
  @@@@@@..............@@@@@@
  @@@@@@@@@@......@@@@@@@@@@
  @@@@@@@@@@@@@@@@@@@@@@@@@@
  `,
  `
  @@@@@@@@@@@@@@@@@@@@@@@@@@
  @@@@@@@@........@@@@@@@@@@
  @@@@@..............@@@@@@@
  @@@@.......++++.......@@@@
  @@@.....++++++++++.....@@@
  @@....++++++++++++++....@@
  @@...++++++++++++++++...@@
  @@...++++++++++++++++...@@
  @@....++++++++++++++....@@
  @@@.....++++++++++.....@@@
  @@@@.......++++.......@@@@
  @@@@@..............@@@@@@@
  @@@@@@@@........@@@@@@@@@@
  @@@@@@@@@@@@@@@@@@@@@@@@@@
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
        const rand = Math.random();
        if (rand > 0.85) {
           setStatus('success');
           setRecognizedUser('张三 (2026001)');
        } else if (rand > 0.92) {
           setStatus('unknown');
           setRecognizedUser(null);
        } else if (status !== 'success' && status !== 'unknown') {
           setStatus('recognizing');
           setRecognizedUser(null);
        }
      }, 300);
    }
    return () => clearInterval(interval);
  }, [isRunning, status]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: '24px' }}>
      {/* Header Actions */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 className="glow-text" style={{ margin: 0, fontSize: '1.5rem' }}>&gt; /live_stream_feed</h2>
          <div style={{ color: 'var(--text-dim)', fontSize: '0.8rem', marginTop: '4px' }}>INITIALIZING HARDWARE BINDINGS...</div>
        </div>
        <div style={{ display: 'flex', gap: '16px' }}>
          <button className="cyber-button" onClick={() => { setIsRunning(true); setStatus('idle'); }} disabled={isRunning}>
            <Play size={16} /> INITIALIZE_CAM
          </button>
          <button className="cyber-button" onClick={() => setIsRunning(false)} disabled={!isRunning} style={{ borderColor: 'var(--warning-color)', color: isRunning ? 'var(--warning-color)' : 'var(--text-dark)' }}>
            <Square size={16} /> TERMINATE_CONN
          </button>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '32px', flex: 1, minHeight: 0 }}>
        {/* Left: Camera Feed */}
        <div className="cyber-card" style={{ flex: 2, display: 'flex', flexDirection: 'column', padding: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px' }}>
            <span style={{ color: 'var(--text-dim)', fontSize: '0.8rem' }}>CAM_01 [OPENCV_ASCII_RENDER_V1]</span>
            <span style={{ color: isRunning ? 'var(--accent-color)' : 'var(--error-color)', fontSize: '0.8rem' }} className={isRunning ? 'blinker' : ''}>
              {isRunning ? '● LIVE' : '○ OFFLINE'}
            </span>
          </div>
          
          <div className="ascii-monitor" style={{ flex: 1 }}>
            <div style={{ 
              fontSize: '18px',
              lineHeight: '1.1',
              whiteSpace: 'pre',
              fontFamily: 'var(--font-mono)',
              color: status === 'success' ? 'var(--accent-color)' : (status === 'unknown' ? 'var(--error-color)' : 'var(--text-color)'),
              transition: 'color 0.3s'
            }}>
              {isRunning ? mockAsciiFrames[frameIndex] : '\\n\\n    [ SIGNAL_LOST ]\\n    AWAITING_CONNECTION...'}
            </div>
          </div>
        </div>

        {/* Right: HUD / Status */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Status Box */}
          <div className="cyber-card" style={{ flex: 1 }}>
            <h3 style={{ fontSize: '0.9rem', marginBottom: '16px', color: 'var(--cyan-color)' }}>[ CURRENT_STATE ]</h3>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: 'calc(100% - 40px)' }}>
              
              {status === 'idle' && (
                <>
                  <ScanFace size={48} color="var(--text-dim)" style={{ marginBottom: '16px' }} />
                  <div style={{ fontSize: '1.2rem', color: 'var(--text-dim)' }}>AWAITING_SUBJECT...</div>
                </>
              )}
              
              {status === 'recognizing' && (
                <>
                  <ScanFace size={48} color="var(--cyan-color)" className="blinker" style={{ marginBottom: '16px' }} />
                  <div className="glow-cyan" style={{ fontSize: '1.2rem' }}>EXTRACTING_FEATURES...</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginTop: '8px' }}>MATCHING LBPH_MODEL</div>
                </>
              )}

              {status === 'success' && (
                <>
                  <UserCheck size={48} color="var(--accent-color)" style={{ marginBottom: '16px' }} />
                  <div className="glow-text" style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>ACCESS_GRANTED</div>
                  <div style={{ fontSize: '0.9rem', color: 'var(--accent-color)', marginTop: '8px' }}>ATTENDANCE_LOGGED</div>
                </>
              )}

              {status === 'unknown' && (
                <>
                  <AlertTriangle size={48} color="var(--error-color)" style={{ marginBottom: '16px' }} />
                  <div className="glow-error" style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>ACCESS_DENIED</div>
                  <div style={{ fontSize: '0.9rem', color: 'var(--error-color)', marginTop: '8px' }}>SUBJECT_UNRECOGNIZED</div>
                </>
              )}

            </div>
          </div>

          {/* User Info Box */}
          <div className="cyber-card" style={{ flex: 1 }}>
            <h3 style={{ fontSize: '0.9rem', marginBottom: '16px', color: 'var(--cyan-color)' }}>[ SUBJECT_DATA ]</h3>
            {status === 'success' && recognizedUser ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>IDENTITY:</div>
                  <div className="glow-text" style={{ fontSize: '1.4rem' }}>{recognizedUser}</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>TIMESTAMP:</div>
                  <div style={{ fontSize: '1rem' }}>{new Date().toLocaleTimeString()}</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>CONFIDENCE_SCORE:</div>
                  <div style={{ fontSize: '1rem', color: 'var(--cyan-color)' }}>94.2% [HIGH]</div>
                </div>
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
