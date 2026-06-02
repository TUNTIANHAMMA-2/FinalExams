import React, { useEffect, useState } from 'react';
import { AlertTriangle, RefreshCw, TrendingUp, Users, UserX } from 'lucide-react';
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
          <h2 style={{ fontSize: '1.5rem', fontWeight: 600, margin: '0 0 8px 0' }}>数据分析</h2>
          <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '0.875rem' }}>系统使用情况与出勤率统计</p>
        </div>
        <button className="btn btn-outline" onClick={loadStats}>
          <RefreshCw size={16} /> 刷新
        </button>
      </div>

      {errorMessage && <div style={{ marginBottom: '16px', color: 'var(--danger)' }}>ERROR: {errorMessage}</div>}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px', marginBottom: '32px' }}>
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.875rem', fontWeight: 500, color: 'var(--text-muted)' }}>今日签到人数</span>
            <div style={{ padding: '8px', backgroundColor: '#eff6ff', borderRadius: '8px', color: 'var(--primary)' }}>
              <Users size={20} />
            </div>
          </div>
          <div style={{ fontSize: '2.5rem', fontWeight: 700 }}>{successCount}</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.75rem' }}>
            <span style={{ color: 'var(--success)', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 500 }}>
              <TrendingUp size={14} /> 真实记录
            </span>
            <span style={{ color: 'var(--text-muted)' }}>来自 data/attendance.csv</span>
          </div>
        </div>

        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.875rem', fontWeight: 500, color: 'var(--text-muted)' }}>拦截重复签到</span>
            <div style={{ padding: '8px', backgroundColor: 'var(--warning-bg)', borderRadius: '8px', color: '#b45309' }}>
              <UserX size={20} />
            </div>
          </div>
          <div style={{ fontSize: '2.5rem', fontWeight: 700 }}>{duplicateCount}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>自动忽略重复打卡请求</div>
        </div>

        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.875rem', fontWeight: 500, color: 'var(--text-muted)' }}>未识别异常</span>
            <div style={{ padding: '8px', backgroundColor: 'var(--danger-bg)', borderRadius: '8px', color: '#b91c1c' }}>
              <AlertTriangle size={20} />
            </div>
          </div>
          <div style={{ fontSize: '2.5rem', fontWeight: 700 }}>{unknownCount}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>记录为陌生人或质量差图像</div>
        </div>
      </div>

      <div className="card">
        <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '24px' }}>用户签到次数</h3>
        {userEntries.length === 0 ? (
          <div style={{ color: 'var(--text-muted)' }}>暂无成功签到记录</div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {userEntries.map(([name, count]) => (
              <div key={name}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '0.875rem' }}>
                  <span>{name}</span>
                  <span>{count}</span>
                </div>
                <div style={{ height: '18px', backgroundColor: '#f1f5f9', borderRadius: '999px', overflow: 'hidden' }}>
                  <div style={{ height: '100%', width: `${(count / maxUserCount) * 100}%`, backgroundColor: 'var(--primary)' }} />
                </div>
              </div>
            ))}
          </div>
        )}
        <div style={{ marginTop: '20px', color: 'var(--text-muted)', fontSize: '0.75rem' }}>TOTAL_RECORDS: {stats.total_records}</div>
      </div>
    </div>
  );
};

export default Stats;
