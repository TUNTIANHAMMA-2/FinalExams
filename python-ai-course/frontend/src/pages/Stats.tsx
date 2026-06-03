import React, { useEffect, useState } from 'react';
import { Button, Card, Col, Empty, Flex, Progress, Row, Space, Statistic, Typography, theme } from 'antd';
import { AlertTriangle, RefreshCw, UserX, Users } from 'lucide-react';
import type { StatsResponse } from '../api';
import { fetchStats } from '../api';

const emptyStats: StatsResponse = {
  total_records: 0,
  status_counts: {},
  valid_status_counts: {},
  event_total: 0,
  event_counts: {},
  user_counts: {},
  registered_user_count: 0,
  attendance_rate: 0,
  recognition_success_rate: 0,
};

const Stats: React.FC = () => {
  const { token } = theme.useToken();
  const [stats, setStats] = useState<StatsResponse>(emptyStats);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const loadStats = async () => {
    try {
      setLoading(true);
      const response = await fetchStats();
      setStats(response);
      setErrorMessage('');
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '统计加载失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadStats();
    }, 0);
    return () => window.clearTimeout(timer);
  }, []);

  const successCount = stats.valid_status_counts.success ?? stats.status_counts.success ?? 0;
  const duplicateCount = stats.event_counts.duplicate ?? 0;
  const recognizedCount = stats.event_counts.recognized ?? 0;
  const unknownCount = stats.event_counts.unknown ?? 0;
  const noModelCount = stats.event_counts.no_model ?? 0;
  const userEntries = Object.entries(stats.user_counts);
  const maxUserCount = Math.max(1, ...userEntries.map(([, value]) => value));

  const cards = [
    {
      label: '今日签到人数',
      value: successCount,
      icon: <Users size={20} />,
      color: token.colorSuccess,
      bg: token.colorSuccessBg,
      note: `有效签到记录 ${successCount} 条，出勤率 ${(stats.attendance_rate * 100).toFixed(1)}%`,
    },
    {
      label: '拦截重复签到',
      value: duplicateCount,
      icon: <UserX size={20} />,
      color: token.colorWarning,
      bg: token.colorWarningBg,
      note: '自动忽略重复打卡请求',
    },
    {
      label: '未知人脸事件',
      value: unknownCount,
      icon: <AlertTriangle size={20} />,
      color: token.colorError,
      bg: token.colorErrorBg,
      note: `无模型事件 ${noModelCount} 次`,
    },
  ];

  return (
    <Space direction="vertical" size={24} style={{ width: '100%' }}>
      <Flex justify="space-between" align="center" wrap gap={16}>
        <div>
          <Typography.Title level={3} style={{ margin: 0 }}>
            数据分析
          </Typography.Title>
          <Typography.Text type="secondary">系统使用情况与出勤率统计</Typography.Text>
        </div>
        <Button icon={<RefreshCw size={16} />} onClick={loadStats} loading={loading}>
          刷新
        </Button>
      </Flex>

      {errorMessage && <Typography.Text type="danger">ERROR: {errorMessage}</Typography.Text>}

      <Row gutter={[24, 24]}>
        {cards.map((card) => (
          <Col key={card.label} xs={24} sm={12} xl={8}>
            <Card>
              <Flex vertical gap={8}>
                <Flex justify="space-between" align="center">
                  <Typography.Text type="secondary" style={{ fontWeight: 500 }}>
                    {card.label}
                  </Typography.Text>
                  <span
                    style={{
                      display: 'inline-flex',
                      padding: 8,
                      borderRadius: 8,
                      background: card.bg,
                      color: card.color,
                    }}
                  >
                    {card.icon}
                  </span>
                </Flex>
                <Statistic value={card.value} valueStyle={{ fontSize: 34, fontWeight: 700, lineHeight: 1.2 }} />
                <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                  {card.note}
                </Typography.Text>
              </Flex>
            </Card>
          </Col>
        ))}
      </Row>

      <Row gutter={[24, 24]}>
        <Col xs={24} md={8}>
          <Card>
            <Statistic
              title="识别事件总数"
              value={stats.event_total}
              valueStyle={{ fontSize: 28, fontWeight: 700 }}
            />
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card>
            <Statistic
              title="出勤率"
              value={stats.attendance_rate * 100}
              precision={1}
              suffix="%"
              valueStyle={{ fontSize: 28, fontWeight: 700, color: token.colorSuccess }}
            />
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card>
            <Statistic
              title="识别成功率"
              value={stats.recognition_success_rate * 100}
              precision={1}
              suffix="%"
              valueStyle={{ fontSize: 28, fontWeight: 700, color: token.colorPrimary }}
            />
            <Typography.Text type="secondary" style={{ fontSize: 12 }}>
              success + duplicate + recognized / success + duplicate + recognized + unknown，不包含 no_face 空帧。
            </Typography.Text>
          </Card>
        </Col>
      </Row>

      {recognizedCount > 0 && (
        <Typography.Text type="secondary">
          识别预览事件 {recognizedCount} 次：表示系统识别到了注册用户，但本次请求没有写入签到表。
        </Typography.Text>
      )}

      <Card title="识别事件类型分布">
        {Object.keys(stats.event_counts).length === 0 ? (
          <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无识别事件" />
        ) : (
          <Space direction="vertical" size={14} style={{ width: '100%' }}>
            {Object.entries(stats.event_counts).map(([eventType, count]) => (
              <div key={eventType}>
                <Flex justify="space-between" style={{ marginBottom: 4 }}>
                  <Typography.Text>{eventType}</Typography.Text>
                  <Typography.Text strong>{count}</Typography.Text>
                </Flex>
                <Progress percent={Math.round((count / Math.max(1, stats.event_total)) * 100)} />
              </div>
            ))}
          </Space>
        )}
      </Card>

      <Card title="用户签到次数">
        {userEntries.length === 0 ? (
          <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无成功签到记录" />
        ) : (
          <Space direction="vertical" size={14} style={{ width: '100%' }}>
            {userEntries.map(([name, count]) => (
              <div key={name}>
                <Flex justify="space-between" style={{ marginBottom: 4 }}>
                  <Typography.Text>{name}</Typography.Text>
                  <Typography.Text strong>{count}</Typography.Text>
                </Flex>
                <Progress percent={Math.round((count / maxUserCount) * 100)} showInfo={false} />
              </div>
            ))}
          </Space>
        )}
        <Typography.Text type="secondary" style={{ fontSize: 12, display: 'block', marginTop: 20 }}>
          TOTAL_RECORDS: {stats.total_records}
        </Typography.Text>
      </Card>
    </Space>
  );
};

export default Stats;
