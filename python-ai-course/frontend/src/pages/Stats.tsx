import React, { useEffect, useState } from 'react';
import type { StatsResponse } from '../api';
import { fetchStats } from '../api';

const emptyStats: StatsResponse = {
  total_records: 0,
  status_counts: {},
  user_counts: {},
};

const Stats: React.FC = () => {
  const [stats, setStats] = useState<StatsResponse>(emptyStats);
  const [errorMessage, setErrorMessage] = useState('');

  const loadStats = async () => {
    try {
      const response = await fetchStats();
      setStats(response);
      setErrorMessage('');
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '统计加载失败');
    }
  };

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadStats();
    }, 0);
    return () => window.clearTimeout(timer);
  }, []);

  const successCount = stats.status_counts.success ?? 0;
  const duplicateCount = stats.status_counts.duplicate ?? 0;
  const userEntries = Object.entries(stats.user_counts);
  const maxUserCount = Math.max(1, ...userEntries.map(([, value]) => value));

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h2 className="glow" style={{ margin: 0 }}>&gt; /analytics</h2>
        <button onClick={loadStats}>REFRESH</button>
      </div>

      {errorMessage && <div style={{ marginBottom: '16px', color: 'var(--error-color)' }}>ERROR: {errorMessage}</div>}

      <div style={{ display: 'flex', gap: '24px', marginBottom: '32px' }}>
        <div style={{ flex: 1, border: '1px solid var(--border-color)', padding: '24px', backgroundColor: '#050505' }}>
          <div style={{ color: 'var(--text-dim)', marginBottom: '8px' }}>SUCCESS_ATTENDANCE</div>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold' }} className="glow">{successCount}</div>
          <div style={{ color: 'var(--text-dim)', marginTop: '8px', fontSize: '0.8rem' }}>SIGNED_RECORDS</div>
        </div>

        <div style={{ flex: 1, border: '1px solid var(--border-color)', padding: '24px', backgroundColor: '#050505' }}>
          <div style={{ color: 'var(--text-dim)', marginBottom: '8px' }}>DUPLICATE_ATTEMPTS</div>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'orange' }}>{duplicateCount}</div>
          <div style={{ color: 'var(--text-dim)', marginTop: '8px', fontSize: '0.8rem' }}>INTERCEPTED</div>
        </div>

        <div style={{ flex: 1, border: '1px solid var(--border-color)', padding: '24px', backgroundColor: '#050505' }}>
          <div style={{ color: 'var(--text-dim)', marginBottom: '8px' }}>TOTAL_RECORDS</div>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold' }}>{stats.total_records}</div>
          <div style={{ color: 'var(--text-dim)', marginTop: '8px', fontSize: '0.8rem' }}>CSV_ROWS</div>
        </div>
      </div>

      <div style={{ border: '1px solid var(--border-color)', padding: '24px', backgroundColor: '#050505' }}>
        <div style={{ color: 'var(--text-dim)', marginBottom: '16px' }}>USER_SIGN_IN_COUNTS</div>
        {userEntries.length === 0 ? (
          <div style={{ color: 'var(--text-dim)' }}>NO_SUCCESS_RECORDS</div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {userEntries.map(([name, count]) => (
              <div key={name}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span>{name}</span>
                  <span>{count}</span>
                </div>
                <div style={{ height: '18px', border: '1px solid var(--border-color)' }}>
                  <div style={{ height: '100%', width: `${(count / maxUserCount) * 100}%`, backgroundColor: 'var(--accent-color)' }} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Stats;
