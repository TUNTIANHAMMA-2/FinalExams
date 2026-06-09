import React, { useEffect, useMemo, useState } from 'react';
import { Alert, Button, Card, Flex, Input, Space, Table, Tabs, Tag, Typography, type TableColumnsType } from 'antd';
import { Download, RefreshCw, Search } from 'lucide-react';
import type { AttendanceRecord, RecognitionEvent } from '../api';
import { exportAttendanceCsv, exportEventsCsv, fetchEvents, fetchRecords } from '../api';
import PageHeader from '../components/PageHeader';

function statusTag(status: string) {
  if (status === 'recognized') {
    return (
      <Tag bordered={false} style={{ color: 'var(--accent-ink)', background: 'var(--accent-soft)', borderRadius: 0 }}>
        识别预览
      </Tag>
    );
  }
  const styles: Record<string, { color: string; label: string }> = {
    success: { color: 'green', label: '签到成功' },
    duplicate: { color: 'orange', label: '重复签到' },
    unknown: { color: 'red', label: '未知人脸' },
    no_model: { color: 'default', label: '模型未训练' },
  };
  const config = styles[status] || { color: 'default', label: status };
  return (
    <Tag color={config.color} bordered={false} style={{ borderRadius: 0 }}>
      {config.label}
    </Tag>
  );
}

const Records: React.FC = () => {
  const [records, setRecords] = useState<AttendanceRecord[]>([]);
  const [events, setEvents] = useState<RecognitionEvent[]>([]);
  const [filterName, setFilterName] = useState('');
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [eventApiUnavailable, setEventApiUnavailable] = useState(false);

  const loadRecords = async () => {
    try {
      setLoading(true);
      const [recordResponse, eventResponse] = await Promise.all([fetchRecords(), fetchEvents()]);
      setRecords(recordResponse.records);
      setEvents(eventResponse.events);
      setEventApiUnavailable(eventResponse.unavailable ?? false);
      setErrorMessage('');
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '记录加载失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadRecords();
    }, 0);
    return () => window.clearTimeout(timer);
  }, []);

  const filteredRecords = useMemo(
    () => records.filter((record) => record.name.includes(filterName) || record.user_id.includes(filterName)),
    [records, filterName],
  );

  const filteredEvents = useMemo(
    () => events.filter((event) => event.name.includes(filterName) || event.user_id.includes(filterName)),
    [events, filterName],
  );

  const handleExport = async (type: 'attendance' | 'events') => {
    try {
      setExporting(true);
      if (type === 'attendance') {
        await exportAttendanceCsv();
      } else {
        await exportEventsCsv();
      }
      setErrorMessage('');
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'CSV 导出失败');
    } finally {
      setExporting(false);
    }
  };

  const columns: TableColumnsType<AttendanceRecord> = [
    {
      title: '日期',
      dataIndex: 'date',
      key: 'date',
      sorter: (a, b) => a.date.localeCompare(b.date),
      defaultSortOrder: 'descend',
      render: (value: string) => <span className="mono">{value}</span>,
    },
    { title: '时间', dataIndex: 'time', key: 'time', render: (value: string) => <span className="mono">{value}</span> },
    { title: '学号', dataIndex: 'user_id', key: 'user_id', render: (value: string) => <span className="mono">{value}</span> },
    {
      title: '姓名',
      dataIndex: 'name',
      key: 'name',
      render: (value: string) => <Typography.Text strong>{value}</Typography.Text>,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (value: string) => statusTag(value),
    },
    {
      title: '置信度',
      dataIndex: 'confidence',
      key: 'confidence',
      render: (value: string) => <span className="mono">{value || '—'}</span>,
    },
  ];

  const eventColumns: TableColumnsType<RecognitionEvent> = [
    {
      title: '时间',
      dataIndex: 'timestamp',
      key: 'timestamp',
      sorter: (a, b) => a.timestamp.localeCompare(b.timestamp),
      defaultSortOrder: 'descend',
      render: (value: string) => <span className="mono">{value}</span>,
    },
    { title: '状态', dataIndex: 'event_type', key: 'event_type', render: (value: string) => statusTag(value) },
    { title: '学号', dataIndex: 'user_id', key: 'user_id', render: (value: string) => <span className="mono">{value}</span> },
    { title: '姓名', dataIndex: 'name', key: 'name' },
    { title: '置信度', dataIndex: 'confidence', key: 'confidence', render: (value: string) => <span className="mono">{value}</span> },
    { title: '说明', dataIndex: 'message', key: 'message', ellipsis: true },
  ];

  const searchBar = (
    <Flex gap={12} style={{ marginBottom: 16 }}>
      <Input
        allowClear
        placeholder="按姓名或学号筛选…"
        prefix={<Search size={14} style={{ opacity: 0.4 }} />}
        value={filterName}
        onChange={(e) => setFilterName(e.target.value)}
        style={{ maxWidth: 320 }}
      />
    </Flex>
  );

  return (
    <Space direction="vertical" size={24} style={{ width: '100%' }}>
      <PageHeader
        title="数据中心"
        kicker="Data Center"
        subtitle="管理并导出历史签到与识别事件日志"
        actions={
          <>
            <Button icon={<RefreshCw size={14} />} onClick={loadRecords} loading={loading}>
              刷新记录
            </Button>
            <Button
              type="primary"
              icon={<Download size={14} />}
              onClick={() => void handleExport('attendance')}
              loading={exporting}
            >
              导出 CSV
            </Button>
          </>
        }
      />

      {errorMessage && <Alert type="error" showIcon message={errorMessage} />}

      <Card styles={{ body: { padding: '8px 24px 24px' } }}>
        <Tabs
          items={[
            {
              key: 'attendance',
              label: `签到成功 (${filteredRecords.length})`,
              children: (
                <div style={{ marginTop: 16 }}>
                  {searchBar}
                  <Table<AttendanceRecord>
                    rowKey={(record, index) => `${record.user_id}-${index}`}
                    columns={columns}
                    dataSource={filteredRecords}
                    loading={loading}
                    size="middle"
                    pagination={{ pageSize: 8, showSizeChanger: false }}
                    rowClassName={() => 'macos-table-row'}
                  />
                </div>
              ),
            },
            {
              key: 'events',
              label: `识别日志 (${filteredEvents.length})`,
              children: (
                <div style={{ marginTop: 16 }}>
                  {eventApiUnavailable ? (
                    <Alert
                      type="warning"
                      showIcon
                      message="识别事件接口未启用"
                      description="后端未提供 /api/events 接口，暂无法展示识别事件日志。"
                    />
                  ) : (
                    <>
                      {searchBar}
                      <Table<RecognitionEvent>
                        rowKey={(event) => event.event_id}
                        columns={eventColumns}
                        dataSource={filteredEvents}
                        loading={loading}
                        size="middle"
                        pagination={{ pageSize: 8, showSizeChanger: false }}
                        rowClassName={() => 'macos-table-row'}
                      />
                    </>
                  )}
                </div>
              ),
            },
          ]}
        />
      </Card>
    </Space>
  );
};

export default Records;
