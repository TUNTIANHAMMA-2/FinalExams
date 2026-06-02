import React from 'react';
import { BarChart2, Activity, Users, AlertTriangle } from 'lucide-react';

const Stats: React.FC = () => {
  return (
    <div>
      <div style={{ marginBottom: '32px' }}>
        <h2 className="glow-text" style={{ margin: 0, fontSize: '1.5rem' }}>&gt; /system_analytics</h2>
        <div style={{ color: 'var(--text-dim)', fontSize: '0.8rem', marginTop: '4px' }}>TELEMETRY AND ATTENDANCE METRICS</div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px', marginBottom: '32px' }}>
        
        {/* Stat Card 1 */}
        <div className="cyber-card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--cyan-color)' }}>
            <span style={{ fontSize: '0.8rem', letterSpacing: '1px' }}>[ SUCCESSFUL_LOGINS ]</span>
            <Users size={18} />
          </div>
          <div style={{ fontSize: '3rem', lineHeight: '1' }} className="glow-text">42</div>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center', fontSize: '0.75rem', color: 'var(--text-dim)' }}>
            <div style={{ flex: 1, height: '4px', background: 'var(--border-color)' }}>
              <div style={{ width: '84%', height: '100%', background: 'var(--accent-color)' }}></div>
            </div>
            <span>84% OF TARGET (50)</span>
          </div>
        </div>
        
        {/* Stat Card 2 */}
        <div className="cyber-card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--warning-color)' }}>
            <span style={{ fontSize: '0.8rem', letterSpacing: '1px' }}>[ DUPLICATE_INTERCEPTS ]</span>
            <Activity size={18} />
          </div>
          <div style={{ fontSize: '3rem', lineHeight: '1', color: 'var(--warning-color)' }} className="glow-warning">05</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
            SYSTEM PREVENTED RE-ENTRY
          </div>
        </div>

        {/* Stat Card 3 */}
        <div className="cyber-card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--error-color)' }}>
            <span style={{ fontSize: '0.8rem', letterSpacing: '1px' }}>[ UNRECOGNIZED_ENTITIES ]</span>
            <AlertTriangle size={18} />
          </div>
          <div style={{ fontSize: '3rem', lineHeight: '1', color: 'var(--error-color)' }} className="glow-error">02</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
            SECURITY WARNINGS LOGGED
          </div>
        </div>

      </div>

      <div className="cyber-card" style={{ padding: '32px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px', alignItems: 'center' }}>
          <div style={{ color: 'var(--cyan-color)', fontSize: '0.9rem', letterSpacing: '1px' }}>[ 5_DAY_ATTENDANCE_TREND ]</div>
          <BarChart2 size={20} color="var(--cyan-color)" />
        </div>
        
        <div style={{ 
          display: 'flex', 
          alignItems: 'flex-end', 
          height: '240px', 
          gap: '16px', 
          borderBottom: '1px solid var(--border-light)', 
          padding: '16px 8px 0 8px',
          position: 'relative'
        }}>
          {/* Y Axis Guide lines */}
          {[100, 75, 50, 25].map(tick => (
            <div key={tick} style={{ 
              position: 'absolute', 
              bottom: `${tick}%`,
              left: 0, 
              right: 0, 
              borderTop: '1px dashed rgba(0, 255, 65, 0.1)', 
              zIndex: 0 
            }}>
              <span style={{ position: 'absolute', left: '-30px', top: '-8px', fontSize: '0.7rem', color: 'var(--text-dim)' }}>{tick}</span>
            </div>
          ))}

          {[
            { label: 'MON', val: 30 }, 
            { label: 'TUE', val: 45 }, 
            { label: 'WED', val: 20 }, 
            { label: 'THU', val: 50 }, 
            { label: 'FRI', val: 42 }
          ].map((item, idx) => (
            <div key={idx} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', zIndex: 1 }}>
              <div style={{ 
                width: '60%', 
                backgroundColor: 'rgba(0, 255, 65, 0.2)', 
                border: '1px solid var(--accent-color)',
                borderBottom: 'none',
                height: `${(item.val / 50) * 100}%`,
                position: 'relative',
                transition: 'height 0.5s ease-out'
              }}>
                <div style={{ 
                  position: 'absolute', 
                  top: '-24px', 
                  width: '100%', 
                  textAlign: 'center', 
                  fontSize: '0.8rem',
                  color: 'var(--text-color)',
                  fontWeight: 'bold'
                }}>{item.val}</div>
              </div>
              <div style={{ marginTop: '16px', color: 'var(--text-dim)', fontSize: '0.8rem' }}>{item.label}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Stats;
