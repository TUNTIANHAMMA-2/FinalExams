import React, { useState } from 'react';
import { Download, Search, FileText } from 'lucide-react';

const mockRecords = [
  { id: 1, date: '2026-06-02', time: '08:30:12', userId: '2026001', name: '张三', status: 'SUCCESS' },
  { id: 2, date: '2026-06-02', time: '08:31:05', userId: '2026002', name: '李四', status: 'SUCCESS' },
  { id: 3, date: '2026-06-02', time: '08:32:50', userId: '2026001', name: '张三', status: 'DUPLICATE' },
  { id: 4, date: '2026-06-02', time: '08:45:22', userId: 'UNKNOWN', name: 'UNKNOWN', status: 'FAILED' },
  { id: 5, date: '2026-06-02', time: '08:50:11', userId: '2026005', name: '王五', status: 'SUCCESS' },
];

const Records: React.FC = () => {
  const [filterName, setFilterName] = useState('');

  const filteredRecords = mockRecords.filter(r => r.name.includes(filterName) || r.userId.includes(filterName));

  return (
    <div>
      <div style={{ marginBottom: '32px' }}>
        <h2 className="glow-text" style={{ margin: 0, fontSize: '1.5rem' }}>&gt; /attendance_logs</h2>
        <div style={{ color: 'var(--text-dim)', fontSize: '0.8rem', marginTop: '4px' }}>QUERY AND EXPORT SYSTEM RECOGNITION LOGS</div>
      </div>
      
      <div style={{ display: 'flex', gap: '16px', marginBottom: '24px', alignItems: 'center' }}>
        <div style={{ position: 'relative', width: '350px' }}>
          <Search size={18} style={{ position: 'absolute', left: '12px', top: '13px', color: 'var(--text-dim)' }} />
          <input 
            className="cyber-input"
            type="text" 
            placeholder="QUERY BY NAME OR ID..." 
            value={filterName}
            onChange={(e) => setFilterName(e.target.value)}
            style={{ paddingLeft: '40px' }}
          />
        </div>
        <button className="cyber-button" style={{ marginLeft: 'auto' }}>
          <Download size={18} /> EXPORT_DATASET (CSV)
        </button>
      </div>

      <div className="cyber-card" style={{ padding: '0', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
          <thead style={{ backgroundColor: 'rgba(0, 50, 0, 0.3)', borderBottom: '1px solid var(--accent-color)' }}>
            <tr>
              <th style={{ padding: '16px 24px', color: 'var(--cyan-color)', fontWeight: 'normal' }}>DATE</th>
              <th style={{ padding: '16px 24px', color: 'var(--cyan-color)', fontWeight: 'normal' }}>TIME</th>
              <th style={{ padding: '16px 24px', color: 'var(--cyan-color)', fontWeight: 'normal' }}>SUBJECT_ID</th>
              <th style={{ padding: '16px 24px', color: 'var(--cyan-color)', fontWeight: 'normal' }}>IDENTITY</th>
              <th style={{ padding: '16px 24px', color: 'var(--cyan-color)', fontWeight: 'normal' }}>RESULT_CODE</th>
            </tr>
          </thead>
          <tbody>
            {filteredRecords.map(record => (
              <tr 
                key={record.id} 
                style={{ borderBottom: '1px solid var(--border-color)', transition: 'background 0.2s' }}
                onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(0, 255, 65, 0.05)'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
              >
                <td style={{ padding: '16px 24px' }}>{record.date}</td>
                <td style={{ padding: '16px 24px' }}>{record.time}</td>
                <td style={{ padding: '16px 24px' }}>{record.userId}</td>
                <td style={{ padding: '16px 24px' }}>{record.name}</td>
                <td style={{ 
                  padding: '16px 24px',
                  color: record.status === 'SUCCESS' ? 'var(--accent-color)' : 
                         record.status === 'FAILED' ? 'var(--error-color)' : 'var(--warning-color)'
                }}>
                  [{record.status}]
                </td>
              </tr>
            ))}
            {filteredRecords.length === 0 && (
              <tr>
                <td colSpan={5} style={{ padding: '48px', textAlign: 'center', color: 'var(--text-dim)' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
                    <FileText size={32} opacity={0.5} />
                    NO_MATCHING_RECORDS_FOUND
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Records;
