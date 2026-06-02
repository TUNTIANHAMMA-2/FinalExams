import React, { useEffect, useState } from 'react';
import { Activity, AlertTriangle, BarChart2, RefreshCw, Users } from 'lucide-react';
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
  const unknownCount = stats.status_counts.unknown ?? 0;
  const userEntries = Object.entries(stats.user_counts);
  const maxUserCount = Math.max(1, ...userEntries.map(([, value]) => value));

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
        <div>
          <h2 className="glow-text" style={{ margin: 0, fontSize: '1.5rem' }}>&gt; /system_analytics</h2>
          <div style={{ color: 'var(--text-dim)', fontSize: '0.8rem', marginTop: '4px' }}>TELEMETRY AND ATTENDANCE METRICS</div>
        </div>
        <button className="cyber-button" onClick={loadStats}>
          <RefreshCw size={18} /> REFRESH
        </button>
      </div>

      {errorMessage && <div className="glow-error" style={{ marginBottom: '16px' }}>ERROR: {errorMessage}</div>}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px', marginBottom: '32px' }}>
        <div className="cyber-card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--cyan-color)' }}>
            <span style={{ fontSize: '0.8rem', letterSpacing: '1px' }}>[ SUCCESSFUL_LOGINS ]</span>
            <Users size={18} />
          </div>
          <div style={{ fontSize: '3rem', lineHeight: '1' }} className="glow-text">{successCount}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
            SIGNED ATTENDANCE RECORDS
          </div>
        </div>

        <div className="cyber-card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--warning-color)' }}>
            <span style={{ fontSize: '0.8rem', letterSpacing: '1px' }}>[ DUPLICATE_INTERCEPTS ]</span>
            <Activity size={18} />
          </div>
          <div style={{ fontSize: '3rem', lineHeight: '1', color: 'var(--warning-color)' }} className="glow-warning">{duplicateCount}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
            SYSTEM PREVENTED RE-ENTRY
          </div>
        </div>

        <div className="cyber-card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--error-color)' }}>
            <span style={{ fontSize: '0.8rem', letterSpacing: '1px' }}>[ UNKNOWN_ENTITIES ]</span>
            <AlertTriangle size={18} />
          </div>
          <div style={{ fontSize: '3rem', lineHeight: '1', color: 'var(--error-color)' }} className="glow-error">{unknownCount}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
            UNMATCHED OR WARNING EVENTS
          </div>
        </div>
      </div>

      <div className="cyber-card" style={{ padding: '32px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px', alignItems: 'center' }}>
          <div style={{ color: 'var(--cyan-color)', fontSize: '0.9rem', letterSpacing: '1px' }}>[ USER_SIGN_IN_COUNTS ]</div>
          <BarChart2 size={20} color="var(--cyan-color)" />
        </div>

        {userEntries.length === 0 ? (
          <div style={{ color: 'var(--text-dim)' }}>NO_SUCCESS_RECORDS</div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {userEntries.map(([name, count]) => (
              <div key={name}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <span>{name}</span>
                  <span>{count}</span>
                </div>
                <div style={{ height: '22px', border: '1px solid var(--border-light)', background: 'rgba(0, 255, 65, 0.04)' }}>
                  <div style={{ height: '100%', width: `${(count / maxUserCount) * 100}%`, background: 'rgba(0, 255, 65, 0.35)', borderRight: '1px solid var(--accent-color)' }} />
                </div>
              </div>
            ))}
          </div>
        )}

        <div style={{ marginTop: '24px', color: 'var(--text-dim)', fontSize: '0.75rem' }}>
          TOTAL_RECORDS: {stats.total_records}
        </div>
      </div>
    </div>
  );
};

export default Stats;
