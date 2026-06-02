import React, { useEffect, useState } from 'react';
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
      <h2 className="glow" style={{ marginBottom: '24px' }}>&gt; /attendance_records</h2>

      <div style={{ display: 'flex', gap: '16px', marginBottom: '24px' }}>
        <input
          type="text"
          placeholder="FILTER BY NAME OR ID..."
          value={filterName}
          onChange={(event) => setFilterName(event.target.value)}
          style={{ width: '300px' }}
        />
        <button onClick={loadRecords}>REFRESH</button>
        <button onClick={exportCsv}>EXPORT_CSV</button>
      </div>

      {errorMessage && <div style={{ marginBottom: '16px', color: 'var(--error-color)' }}>ERROR: {errorMessage}</div>}

      <div style={{ border: '1px solid var(--border-color)', backgroundColor: '#050505' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-dim)' }}>
              <th style={{ padding: '12px' }}>DATE</th>
              <th style={{ padding: '12px' }}>TIME</th>
              <th style={{ padding: '12px' }}>USER_ID</th>
              <th style={{ padding: '12px' }}>NAME</th>
              <th style={{ padding: '12px' }}>STATUS</th>
            </tr>
          </thead>
          <tbody>
            {filteredRecords.map((record, index) => (
              <tr key={`${record.date}-${record.time}-${record.user_id}-${index}`} style={{ borderBottom: '1px dashed #003b00' }}>
                <td style={{ padding: '12px' }}>{record.date}</td>
                <td style={{ padding: '12px' }}>{record.time}</td>
                <td style={{ padding: '12px' }}>{record.user_id}</td>
                <td style={{ padding: '12px' }}>{record.name}</td>
                <td style={{
                  padding: '12px',
                  color: record.status === 'success' ? 'var(--accent-color)' : 'orange',
                }}>
                  [{record.status.toUpperCase()}]
                </td>
              </tr>
            ))}
            {filteredRecords.length === 0 && (
              <tr>
                <td colSpan={5} style={{ padding: '24px', textAlign: 'center', color: 'var(--text-dim)' }}>
                  NO_RECORDS_FOUND
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
