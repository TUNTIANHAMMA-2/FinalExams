import React, { useEffect, useState } from 'react';
import { Button, Card, Col, Empty, Flex, Progress, Row, Space, Statistic, Tooltip, Typography, theme } from 'antd';
import { AlertTriangle, Info, RefreshCw, UserX, Users } from 'lucide-react';
import type { StatsResponse } from '../api';
import { fetchStats } from '../api';
import PageHeader from '../components/PageHeader';

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
      label: '成功签到',
      value: successCount,
      icon: <Users size={22} />,
      note: `出勤率 ${(stats.attendance_rate * 100).toFixed(1)}%`,
    },
    {
      label: '重复拦截',
      value: duplicateCount,
      icon: <UserX size={22} />,
      note: '忽略重复打卡',
    },
    {
      label: '未知人脸',
      value: unknownCount,
      icon: <AlertTriangle size={22} />,
      note: `异常事件 ${noModelCount} 次`,
    },
  ];

  return (
    <Space direction="vertical" size={24} style={{ width: '100%' }}>
      <PageHeader
        title="系统分析"
        kicker="Analytics"
        subtitle="出勤表现与识别质量的实时洞察"
        actions={
          <Button type="primary" icon={<RefreshCw size={14} />} onClick={loadStats} loading={loading}>
            同步数据
          </Button>
        }
      />

      {errorMessage && (
        <Typography.Text type="danger">
          {errorMessage}
        </Typography.Text>
      )}

      <Row gutter={[24, 24]}>
        {cards.map((card) => (
          <Col key={card.label} xs={24} sm={12} xl={8}>
            <Card className="stat-card is-interactive" styles={{ body: { padding: '22px 24px' } }}>
              <Flex align="center" gap={16}>
                <span className="stat-icon">{card.icon}</span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div className="metric-label" style={{ marginBottom: 2 }}>
                    {card.label}
                  </div>
                  <Statistic value={card.value} valueStyle={{ fontSize: 30, fontWeight: 700, letterSpacing: '-0.5px' }} />
                </div>
              </Flex>
              <div
                style={{
                  marginTop: 16,
                  paddingTop: 12,
                  borderTop: `1px solid ${token.colorBorderSecondary}`,
                }}
              >
                <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                  {card.note}
                </Typography.Text>
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      <Row gutter={[24, 24]}>
        <Col xs={24} md={8}>
          <Card className="is-interactive">
            <Statistic
              title={<span className="metric-label">识别事件总数</span>}
              value={stats.event_total}
              valueStyle={{ fontSize: 28, fontWeight: 700 }}
            />
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card className="is-interactive">
            <Statistic
              title={<span className="metric-label">出勤率</span>}
              value={stats.attendance_rate * 100}
              precision={1}
              suffix="%"
              valueStyle={{ fontSize: 28, fontWeight: 700, color: token.colorSuccess }}
            />
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card className="is-interactive">
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span className="metric-label">识别成功率</span>
              <Tooltip title="计算公式：(签到成功 + 重复签到 + 已识别) / (签到成功 + 重复签到 + 已识别 + 未知人脸)，排除未检测到人脸的空帧。">
                <Info size={13} style={{ color: token.colorTextSecondary, cursor: 'pointer' }} />
              </Tooltip>
            </div>
            <Statistic
              value={stats.recognition_success_rate * 100}
              precision={1}
              suffix="%"
              valueStyle={{ fontSize: 28, fontWeight: 700, color: token.colorPrimary }}
            />
          </Card>
        </Col>
      </Row>

      {recognizedCount > 0 && (
        <Typography.Text type="secondary" style={{ fontSize: 13 }}>
          识别预览事件 {recognizedCount} 次：系统识别到了注册用户，但本次请求没有写入签到表。
        </Typography.Text>
      )}

      <Row gutter={[24, 24]}>
        <Col xs={24} lg={12}>
          <Card title={<span style={{ fontWeight: 600 }}>识别事件类型分布</span>} style={{ height: '100%' }}>
            {Object.keys(stats.event_counts).length === 0 ? (
              <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无识别事件" />
            ) : (
              <Space direction="vertical" size={16} style={{ width: '100%' }}>
                {Object.entries(stats.event_counts).map(([eventType, count]) => {
                  const labelMap: Record<string, string> = {
                    recognized: '用户识别',
                    duplicate: '重复签到',
                    unknown: '陌生人',
                    no_model: '未注册',
                    no_face: '未检测到人脸',
                  };
                  return (
                    <div key={eventType} className="meter-row">
                      <div className="meter-head">
                        <Typography.Text>{labelMap[eventType] || eventType}</Typography.Text>
                        <Typography.Text strong className="mono">
                          {count}
                        </Typography.Text>
                      </div>
                      <Progress
                        percent={Math.round((count / Math.max(1, stats.event_total)) * 100)}
                        strokeColor={token.colorPrimary}
                      />
                    </div>
                  );
                })}
              </Space>
            )}
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title={<span style={{ fontWeight: 600 }}>用户签到次数</span>} style={{ height: '100%' }}>
            {userEntries.length === 0 ? (
              <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无成功签到记录" />
            ) : (
              <Space direction="vertical" size={16} style={{ width: '100%' }}>
                {userEntries.map(([name, count]) => (
                  <div key={name} className="meter-row">
                    <div className="meter-head">
                      <Typography.Text>{name}</Typography.Text>
                      <Typography.Text strong className="mono">
                        {count}
                      </Typography.Text>
                    </div>
                    <Progress percent={Math.round((count / maxUserCount) * 100)} showInfo={false} strokeColor={token.colorPrimary} />
                  </div>
                ))}
              </Space>
            )}
            <Typography.Text type="secondary" style={{ fontSize: 12, display: 'block', marginTop: 18 }}>
              记录总数 {stats.total_records}
            </Typography.Text>
          </Card>
        </Col>
      </Row>
    </Space>
  );
};

export default Stats;
