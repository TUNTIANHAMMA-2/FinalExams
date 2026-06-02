import React from 'react';

const Stats: React.FC = () => {
  return (
    <div>
      <h2 className="glow" style={{ marginBottom: '24px' }}>&gt; /analytics</h2>

      <div style={{ display: 'flex', gap: '24px', marginBottom: '32px' }}>
        <div style={{ flex: 1, border: '1px solid var(--border-color)', padding: '24px', backgroundColor: '#050505' }}>
          <div style={{ color: 'var(--text-dim)', marginBottom: '8px' }}>TODAY_ATTENDANCE</div>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold' }} className="glow">42</div>
          <div style={{ color: 'var(--text-dim)', marginTop: '8px', fontSize: '0.8rem' }}>TARGET: 50</div>
        </div>
        
        <div style={{ flex: 1, border: '1px solid var(--border-color)', padding: '24px', backgroundColor: '#050505' }}>
          <div style={{ color: 'var(--text-dim)', marginBottom: '8px' }}>DUPLICATE_ATTEMPTS</div>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'orange' }}>5</div>
          <div style={{ color: 'var(--text-dim)', marginTop: '8px', fontSize: '0.8rem' }}>INTERCEPTED</div>
        </div>

        <div style={{ flex: 1, border: '1px solid var(--border-color)', padding: '24px', backgroundColor: '#050505' }}>
          <div style={{ color: 'var(--text-dim)', marginBottom: '8px' }}>UNRECOGNIZED</div>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--error-color)' }}>2</div>
          <div style={{ color: 'var(--text-dim)', marginTop: '8px', fontSize: '0.8rem' }}>WARNINGS_LOGGED</div>
        </div>
      </div>

      <div style={{ border: '1px solid var(--border-color)', padding: '24px', backgroundColor: '#050505' }}>
        <div style={{ color: 'var(--text-dim)', marginBottom: '16px' }}>ATTENDANCE_TREND (MOCK)</div>
        <div style={{ display: 'flex', alignItems: 'flex-end', height: '200px', gap: '8px', borderBottom: '1px solid var(--text-dim)', borderLeft: '1px solid var(--text-dim)', padding: '8px' }}>
          {[30, 45, 20, 50, 42].map((val, idx) => (
            <div key={idx} style={{ 
              flex: 1, 
              backgroundColor: 'var(--accent-color)', 
              height: `${(val / 50) * 100}%`,
              opacity: 0.8,
              position: 'relative'
            }}>
              <span style={{ position: 'absolute', top: '-24px', width: '100%', textAlign: 'center', fontSize: '0.8rem' }}>{val}</span>
            </div>
          ))}
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px', color: 'var(--text-dim)', fontSize: '0.8rem' }}>
          <span>MON</span>
          <span>TUE</span>
          <span>WED</span>
          <span>THU</span>
          <span>FRI</span>
        </div>
      </div>
    </div>
  );
};

export default Stats;
