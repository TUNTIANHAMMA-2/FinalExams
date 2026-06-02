import React, { useState } from 'react';

const mockRecords = [
  { id: 1, date: '2026-06-02', time: '08:30:12', userId: '2026001', name: '张三', status: 'SUCCESS' },
  { id: 2, date: '2026-06-02', time: '08:31:05', userId: '2026002', name: '李四', status: 'SUCCESS' },
  { id: 3, date: '2026-06-02', time: '08:32:50', userId: '2026001', name: '张三', status: 'DUPLICATE' },
  { id: 4, date: '2026-06-02', time: '08:45:22', userId: 'UNKNOWN', name: 'UNKNOWN', status: 'FAILED' },
];

const Records: React.FC = () => {
  const [filterName, setFilterName] = useState('');

  const filteredRecords = mockRecords.filter(r => r.name.includes(filterName) || r.userId.includes(filterName));

  return (
    <div>
      <h2 className="glow" style={{ marginBottom: '24px' }}>&gt; /attendance_records</h2>
      
      <div style={{ display: 'flex', gap: '16px', marginBottom: '24px' }}>
        <input 
          type="text" 
          placeholder="FILTER BY NAME OR ID..." 
          value={filterName}
          onChange={(e) => setFilterName(e.target.value)}
          style={{ width: '300px' }}
        />
        <button>EXPORT_CSV</button>
      </div>

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
            {filteredRecords.map(record => (
              <tr key={record.id} style={{ borderBottom: '1px dashed #003b00' }}>
                <td style={{ padding: '12px' }}>{record.date}</td>
                <td style={{ padding: '12px' }}>{record.time}</td>
                <td style={{ padding: '12px' }}>{record.userId}</td>
                <td style={{ padding: '12px' }}>{record.name}</td>
                <td style={{ 
                  padding: '12px',
                  color: record.status === 'SUCCESS' ? 'var(--accent-color)' : 
                         record.status === 'FAILED' ? 'var(--error-color)' : 'orange'
                }}>
                  [{record.status}]
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
