import React, { useEffect, useState } from 'react';
import { Download, FileText, RefreshCw, Search } from 'lucide-react';
import type { AttendanceRecord } from '../api';
import { fetchRecords } from '../api';

const Records: React.FC = () => {
  const [records, setRecords] = useState<AttendanceRecord[]>([]);
  const [filterName, setFilterName] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const loadRecords = async () => {
    try {
      const response = await fetchRecords();
      setRecords(response.records);
      setErrorMessage('');
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '记录加载失败');
    }
  };

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadRecords();
    }, 0);
    return () => window.clearTimeout(timer);
  }, []);

  const filteredRecords = records.filter((record) => (
    record.name.includes(filterName) || record.user_id.includes(filterName)
  ));

  const exportCsv = () => {
    const header = 'date,time,user_id,name,status';
    const rows = filteredRecords.map((record) => [
      record.date,
      record.time,
      record.user_id,
      record.name,
      record.status,
    ].join(','));
    const blob = new Blob([[header, ...rows].join('\n')], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'attendance_records.csv';
    anchor.click();
    URL.revokeObjectURL(url);
  };

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
            onChange={(event) => setFilterName(event.target.value)}
            style={{ paddingLeft: '40px' }}
          />
        </div>
        <button className="cyber-button" onClick={loadRecords}>
          <RefreshCw size={18} /> REFRESH
        </button>
        <button className="cyber-button" onClick={exportCsv} style={{ marginLeft: 'auto' }}>
          <Download size={18} /> EXPORT_DATASET (CSV)
        </button>
      </div>

      {errorMessage && <div className="glow-error" style={{ marginBottom: '16px' }}>ERROR: {errorMessage}</div>}

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
            {filteredRecords.map((record, index) => (
              <tr key={`${record.date}-${record.time}-${record.user_id}-${index}`} style={{ borderBottom: '1px solid var(--border-color)', transition: 'background 0.2s' }}>
                <td style={{ padding: '16px 24px' }}>{record.date}</td>
                <td style={{ padding: '16px 24px' }}>{record.time}</td>
                <td style={{ padding: '16px 24px' }}>{record.user_id}</td>
                <td style={{ padding: '16px 24px' }}>{record.name}</td>
                <td style={{
                  padding: '16px 24px',
                  color: record.status === 'success' ? 'var(--accent-color)' : 'var(--warning-color)',
                }}>
                  [{record.status.toUpperCase()}]
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
