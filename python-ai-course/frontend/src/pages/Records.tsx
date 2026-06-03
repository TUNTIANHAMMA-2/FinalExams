import React, { useEffect, useMemo, useState } from 'react';
import { Button, Card, Empty, Flex, Input, Space, Table, Tag, Typography, type TableColumnsType } from 'antd';
import { Download, RefreshCw, Search } from 'lucide-react';
import type { AttendanceRecord } from '../api';
import { fetchRecords } from '../api';

function statusTag(status: string) {
  if (status === 'success') return <Tag color="success">签到成功</Tag>;
  if (status === 'duplicate') return <Tag color="warning">重复签到</Tag>;
  return <Tag color="error">{status}</Tag>;
}

const Records: React.FC = () => {
  const [records, setRecords] = useState<AttendanceRecord[]>([]);
  const [filterName, setFilterName] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const loadRecords = async () => {
    try {
      setLoading(true);
      const response = await fetchRecords();
      setRecords(response.records);
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

  const exportCsv = () => {
    const header = 'date,time,user_id,name,status';
    const rows = filteredRecords.map((record) =>
      [record.date, record.time, record.user_id, record.name, record.status].join(','),
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

      <Card styles={{ body: { padding: 0 } }}>
        <Table<AttendanceRecord>
          rowKey={(record, index) => `${record.date}-${record.time}-${record.user_id}-${index}`}
          columns={columns}
          dataSource={filteredRecords}
          loading={loading}
          scroll={{ x: 'max-content' }}
          pagination={{ pageSize: 10, showSizeChanger: true, responsive: true, hideOnSinglePage: false }}
          locale={{ emptyText: <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="没有找到匹配的记录" /> }}
        />
      </Card>
    </Space>
  );
};

export default Records;
