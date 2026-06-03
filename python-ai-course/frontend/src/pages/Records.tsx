import React, { useEffect, useMemo, useState } from 'react';
import { Alert, Button, Card, Empty, Flex, Input, Space, Table, Tabs, Tag, Typography, type TableColumnsType } from 'antd';
import { Download, RefreshCw, Search } from 'lucide-react';
import type { AttendanceRecord, RecognitionEvent } from '../api';
import { fetchEvents, fetchRecords } from '../api';

function statusTag(status: string) {
  if (status === 'success') return <Tag color="success">签到成功</Tag>;
  if (status === 'duplicate') return <Tag color="warning">重复签到</Tag>;
  if (status === 'recognized') return <Tag color="processing">识别预览</Tag>;
  if (status === 'unknown') return <Tag color="error">未知人脸</Tag>;
  if (status === 'no_model') return <Tag color="default">模型未训练</Tag>;
  return <Tag color="default">{status}</Tag>;
}

function escapeCsv(value?: string) {
  const text = value ?? '';
  return /[",\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

const Records: React.FC = () => {
  const [records, setRecords] = useState<AttendanceRecord[]>([]);
  const [events, setEvents] = useState<RecognitionEvent[]>([]);
  const [filterName, setFilterName] = useState('');
  const [loading, setLoading] = useState(false);
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

  const exportCsv = () => {
    const header = 'date,time,user_id,name,status,confidence,event_id';
    const rows = filteredRecords.map((record) =>
      [record.date, record.time, record.user_id, record.name, record.status, record.confidence, record.event_id]
        .map(escapeCsv)
        .join(','),
    );
    const blob = new Blob([[header, ...rows].join('\n')], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'attendance_records.csv';
    anchor.click();
    URL.revokeObjectURL(url);
  };

  const columns: TableColumnsType<AttendanceRecord> = [
    {
      title: '日期',
      dataIndex: 'date',
      key: 'date',
      sorter: (a, b) => a.date.localeCompare(b.date),
      defaultSortOrder: 'descend',
    },
    { title: '时间', dataIndex: 'time', key: 'time', sorter: (a, b) => a.time.localeCompare(b.time) },
    { title: '学号', dataIndex: 'user_id', key: 'user_id' },
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
      filters: [
        { text: '签到成功', value: 'success' },
        { text: '重复签到', value: 'duplicate' },
        { text: '未识别', value: 'unknown' },
      ],
      onFilter: (value, record) => record.status === value,
    },
    { title: '置信度', dataIndex: 'confidence', key: 'confidence', render: (value: string) => value || '-' },
    { title: '事件ID', dataIndex: 'event_id', key: 'event_id', render: (value: string) => value || '-' },
  ];

  const eventColumns: TableColumnsType<RecognitionEvent> = [
    {
      title: '时间',
      dataIndex: 'timestamp',
      key: 'timestamp',
      sorter: (a, b) => a.timestamp.localeCompare(b.timestamp),
      defaultSortOrder: 'descend',
    },
    { title: '事件', dataIndex: 'event_type', key: 'event_type', render: (value: string) => statusTag(value) },
    { title: '学号', dataIndex: 'user_id', key: 'user_id', render: (value: string) => value || '-' },
    { title: '姓名', dataIndex: 'name', key: 'name', render: (value: string) => value || '-' },
    { title: '置信度', dataIndex: 'confidence', key: 'confidence', render: (value: string) => value || '-' },
    { title: '人脸数', dataIndex: 'face_count', key: 'face_count' },
    { title: '说明', dataIndex: 'message', key: 'message', render: (value: string) => value || '-' },
  ];

  return (
    <Space direction="vertical" size={24} style={{ width: '100%' }}>
      <div>
        <Typography.Title level={3} style={{ margin: 0 }}>
          签到记录
        </Typography.Title>
        <Typography.Text type="secondary">查询与导出历史签到日志数据</Typography.Text>
      </div>

      <Flex gap={16} wrap align="center" justify="space-between">
        <Input
          allowClear
          placeholder="搜索姓名或学号..."
          prefix={<Search size={16} />}
          value={filterName}
          onChange={(event) => setFilterName(event.target.value)}
          style={{ flex: '1 1 240px', maxWidth: 360 }}
        />
        <Space wrap>
          <Button icon={<RefreshCw size={16} />} onClick={loadRecords} loading={loading}>
            刷新
          </Button>
          <Button icon={<Download size={16} />} onClick={exportCsv}>
            导出为 CSV
          </Button>
        </Space>
      </Flex>

      {errorMessage && (
        <Typography.Text type="danger">ERROR: {errorMessage}</Typography.Text>
      )}

      <Card>
        <Tabs
          items={[
            {
              key: 'attendance',
              label: `签到记录 (${filteredRecords.length})`,
              children: (
                <Table<AttendanceRecord>
                  rowKey={(record, index) => `${record.date}-${record.time}-${record.user_id}-${index}`}
                  columns={columns}
                  dataSource={filteredRecords}
                  loading={loading}
                  scroll={{ x: 'max-content' }}
                  pagination={{ pageSize: 10, showSizeChanger: true, responsive: true, hideOnSinglePage: false }}
                  locale={{ emptyText: <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="没有找到匹配的记录" /> }}
                />
              ),
            },
            {
              key: 'events',
              label: `识别事件 (${filteredEvents.length})`,
              children: (
                <Space direction="vertical" size={16} style={{ width: '100%' }}>
                  {eventApiUnavailable && (
                    <Alert
                      type="warning"
                      showIcon
                      message="当前后端还没有 /api/events 接口"
                      description="签到记录已正常加载。请重启或更新 Python 后端后，识别事件日志会显示在这里。"
                    />
                  )}
                  <Table<RecognitionEvent>
                    rowKey={(event) => event.event_id}
                    columns={eventColumns}
                    dataSource={filteredEvents}
                    loading={loading}
                    scroll={{ x: 'max-content' }}
                    pagination={{ pageSize: 10, showSizeChanger: true, responsive: true, hideOnSinglePage: false }}
                    locale={{ emptyText: <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无识别事件" /> }}
                  />
                </Space>
              ),
            },
          ]}
        />
      </Card>
    </Space>
  );
};

export default Records;
