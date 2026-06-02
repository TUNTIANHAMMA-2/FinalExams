import React, { useEffect, useState } from 'react';
import { Download, Inbox, RefreshCw, Search } from 'lucide-react';
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
    const rows = filteredRecords.map((record) => [record.date, record.time, record.user_id, record.name, record.status].join(','));
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
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, margin: '0 0 8px 0' }}>签到记录</h2>
        <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '0.875rem' }}>查询与导出历史签到日志数据</p>
      </div>

      <div style={{ display: 'flex', gap: '16px', marginBottom: '24px', alignItems: 'center' }}>
        <div style={{ position: 'relative', width: '320px' }}>
          <Search size={18} style={{ position: 'absolute', left: '12px', top: '10px', color: 'var(--text-muted)' }} />
          <input
            className="input-field"
            type="text"
            placeholder="搜索姓名或学号..."
            value={filterName}
            onChange={(event) => setFilterName(event.target.value)}
            style={{ paddingLeft: '38px' }}
          />
        </div>
        <button className="btn btn-outline" onClick={loadRecords}>
          <RefreshCw size={16} /> 刷新
        </button>
        <button className="btn btn-outline" onClick={exportCsv} style={{ marginLeft: 'auto' }}>
          <Download size={16} /> 导出为 CSV
        </button>
      </div>

      {errorMessage && <div style={{ marginBottom: '16px', color: 'var(--danger)' }}>ERROR: {errorMessage}</div>}

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
          <thead style={{ backgroundColor: '#f8fafc', borderBottom: '1px solid var(--border)' }}>
            <tr>
              <th style={{ padding: '16px 24px', fontWeight: 500, color: 'var(--text-muted)' }}>日期</th>
              <th style={{ padding: '16px 24px', fontWeight: 500, color: 'var(--text-muted)' }}>时间</th>
              <th style={{ padding: '16px 24px', fontWeight: 500, color: 'var(--text-muted)' }}>学号</th>
              <th style={{ padding: '16px 24px', fontWeight: 500, color: 'var(--text-muted)' }}>姓名</th>
              <th style={{ padding: '16px 24px', fontWeight: 500, color: 'var(--text-muted)' }}>状态</th>
            </tr>
          </thead>
          <tbody>
            {filteredRecords.map((record, index) => (
              <tr key={`${record.date}-${record.time}-${record.user_id}-${index}`} style={{ borderBottom: '1px solid var(--border)' }}>
                <td style={{ padding: '16px 24px' }}>{record.date}</td>
                <td style={{ padding: '16px 24px' }}>{record.time}</td>
                <td style={{ padding: '16px 24px' }}>{record.user_id}</td>
                <td style={{ padding: '16px 24px', fontWeight: 500 }}>{record.name}</td>
                <td style={{ padding: '16px 24px' }}>
                  {record.status === 'success' && <span className="badge badge-success">签到成功</span>}
                  {record.status === 'duplicate' && <span className="badge badge-warning">重复签到</span>}
                  {record.status !== 'success' && record.status !== 'duplicate' && <span className="badge badge-danger">{record.status}</span>}
                </td>
              </tr>
            ))}
            {filteredRecords.length === 0 && (
              <tr>
                <td colSpan={5} style={{ padding: '48px', textAlign: 'center', color: 'var(--text-muted)' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
                    <Inbox size={40} strokeWidth={1} />
                    <p style={{ margin: 0 }}>没有找到匹配的记录</p>
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
