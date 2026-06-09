import React, { useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Button,
  Card,
  Col,
  Descriptions,
  Empty,
  Flex,
  Progress,
  Row,
  Space,
  Statistic,
  Table,
  Tag,
  Typography,
  theme,
  type TableColumnsType,
} from 'antd';
import { Brain, DatabaseZap, RefreshCw, Sparkles } from 'lucide-react';
import type { StudentAnalysisResponse, StudentRiskReport } from '../api';
import { fetchStudentAnalysis, generateStudentDemoData, trainStudentRiskModel } from '../api';
import PageHeader from '../components/PageHeader';

const emptyAnalysis: StudentAnalysisResponse = {
  model_ready: false,
  student_count: 0,
  training_samples: 0,
  features: [],
  risk_counts: {},
  students: [],
};

function riskTag(level: string) {
  const styles: Record<string, { color: string; label: string }> = {
    高风险: { color: 'red', label: '高风险' },
    中风险: { color: 'orange', label: '中风险' },
    低风险: { color: 'green', label: '低风险' },
  };
  const config = styles[level] || { color: 'default', label: level || '未知' };
  return (
    <Tag color={config.color} bordered={false} style={{ borderRadius: 0 }}>
      {config.label}
    </Tag>
  );
}

const StudentAnalysis: React.FC = () => {
  const { token } = theme.useToken();
  const [analysis, setAnalysis] = useState<StudentAnalysisResponse>(emptyAnalysis);
  const [selectedUserId, setSelectedUserId] = useState('');
  const [loading, setLoading] = useState(false);
  const [action, setAction] = useState<'demo' | 'train' | null>(null);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const loadAnalysis = async () => {
    try {
      setLoading(true);
      const response = await fetchStudentAnalysis();
      setAnalysis(response);
      setSelectedUserId((current) => (
        response.students.some((student) => student.user_id === current)
          ? current
          : response.students[0]?.user_id ?? ''
      ));
      setErrorMessage('');
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '智能分析加载失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadAnalysis();
    }, 0);
    return () => window.clearTimeout(timer);
  }, []);

  const selectedReport = useMemo(
    () => analysis.students.find((student) => student.user_id === selectedUserId) ?? analysis.students[0] ?? null,
    [analysis.students, selectedUserId],
  );

  const highRiskCount = analysis.risk_counts['高风险'] ?? 0;
  const mediumRiskCount = analysis.risk_counts['中风险'] ?? 0;
  const lowRiskCount = analysis.risk_counts['低风险'] ?? 0;

  const handleGenerateDemo = async () => {
    try {
      setAction('demo');
      const response = await generateStudentDemoData();
      setSuccessMessage(
        `${response.message}：${response.generated.students} 名学生，${response.generated.training_samples} 条训练样本。`,
      );
      await loadAnalysis();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '演示数据生成失败');
    } finally {
      setAction(null);
    }
  };

  const handleTrain = async () => {
    try {
      setAction('train');
      const response = await trainStudentRiskModel();
      setSuccessMessage(`${response.message}：训练样本 ${response.model.training_samples} 条。`);
      await loadAnalysis();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '模型训练失败');
    } finally {
      setAction(null);
    }
  };

  const columns: TableColumnsType<StudentRiskReport> = [
    {
      title: '风险等级',
      dataIndex: 'risk_level',
      key: 'risk_level',
      render: (value: string) => riskTag(value),
      sorter: (a, b) => b.risk_score - a.risk_score,
    },
    {
      title: '学生',
      dataIndex: 'name',
      key: 'name',
      render: (value: string, record) => (
        <Space direction="vertical" size={0}>
          <Typography.Text strong>{value}</Typography.Text>
          <Typography.Text type="secondary" className="mono" style={{ fontSize: 12 }}>
            {record.user_id}
          </Typography.Text>
        </Space>
      ),
    },
    {
      title: '出勤率',
      dataIndex: ['features', 'attendance_rate_30d'],
      key: 'attendance_rate_30d',
      render: (value: number) => `${(value * 100).toFixed(1)}%`,
      sorter: (a, b) => a.features.attendance_rate_30d - b.features.attendance_rate_30d,
    },
    {
      title: '近7天迟到',
      dataIndex: ['features', 'late_count_7d'],
      key: 'late_count_7d',
      render: (value: number) => <span className="mono">{value}</span>,
      sorter: (a, b) => a.features.late_count_7d - b.features.late_count_7d,
    },
    {
      title: '平均成绩',
      dataIndex: ['features', 'avg_score'],
      key: 'avg_score',
      render: (value: number) => <span className="mono">{value.toFixed(1)}</span>,
      sorter: (a, b) => a.features.avg_score - b.features.avg_score,
    },
    {
      title: '成绩变化',
      dataIndex: ['features', 'score_delta'],
      key: 'score_delta',
      render: (value: number) => (
        <Typography.Text className="mono" type={value < 0 ? 'danger' : 'success'}>
          {value >= 0 ? '+' : ''}{value.toFixed(1)}
        </Typography.Text>
      ),
      sorter: (a, b) => a.features.score_delta - b.features.score_delta,
    },
    {
      title: '模型置信度',
      dataIndex: 'confidence',
      key: 'confidence',
      render: (value: number) => `${(value * 100).toFixed(1)}%`,
    },
  ];

  return (
    <Space direction="vertical" size={24} style={{ width: '100%' }}>
      <PageHeader
        title="智能分析"
        kicker="Intelligence"
        subtitle="融合考勤、迟到、重复签到与成绩变化，使用决策树模型生成学生状态评估报告"
        actions={
          <>
            <Button icon={<DatabaseZap size={14} />} onClick={handleGenerateDemo} loading={action === 'demo'}>
              生成演示数据
            </Button>
            <Button icon={<Brain size={14} />} onClick={handleTrain} loading={action === 'train'}>
              训练模型
            </Button>
            <Button type="primary" icon={<RefreshCw size={14} />} onClick={loadAnalysis} loading={loading}>
              刷新分析
            </Button>
          </>
        }
      />

      {errorMessage && <Alert type="error" showIcon message={errorMessage} />}
      {successMessage && <Alert type="success" showIcon message={successMessage} />}

      <Row gutter={[24, 24]}>
        <Col xs={24} sm={12} xl={6}>
          <Card className="stat-card is-interactive">
            <Statistic
              title={<span className="metric-label">模型状态</span>}
              value={analysis.model_ready ? '就绪' : '待训练'}
              valueStyle={{ fontSize: 24, fontWeight: 700, color: analysis.model_ready ? token.colorSuccess : token.colorWarning }}
            />
            <Typography.Text type="secondary">决策树模型文件状态</Typography.Text>
          </Card>
        </Col>
        <Col xs={24} sm={12} xl={6}>
          <Card className="stat-card is-interactive">
            <Statistic title={<span className="metric-label">学生数</span>} value={analysis.student_count} valueStyle={{ fontSize: 30, fontWeight: 700 }} />
            <Typography.Text type="secondary">当前参与分析的学生数</Typography.Text>
          </Card>
        </Col>
        <Col xs={24} sm={12} xl={6}>
          <Card className="stat-card is-interactive">
            <Statistic title={<span className="metric-label">高风险</span>} value={highRiskCount} valueStyle={{ fontSize: 30, fontWeight: 700, color: token.colorError }} />
            <Typography.Text type="secondary">需要优先关注</Typography.Text>
          </Card>
        </Col>
        <Col xs={24} sm={12} xl={6}>
          <Card className="stat-card is-interactive">
            <Statistic title={<span className="metric-label">训练样本</span>} value={analysis.training_samples} valueStyle={{ fontSize: 30, fontWeight: 700, color: token.colorPrimary }} />
            <Typography.Text type="secondary">用于训练分类器的样本</Typography.Text>
          </Card>
        </Col>
      </Row>

      <Row gutter={[24, 24]}>
        <Col xs={24} lg={15}>
          <Card title={<span style={{ fontWeight: 600 }}>学生风险预测结果</span>} style={{ height: '100%' }}>
            {analysis.students.length === 0 ? (
              <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无学生分析数据，请先生成演示数据" />
            ) : (
              <Table<StudentRiskReport>
                rowKey="user_id"
                columns={columns}
                dataSource={analysis.students}
                loading={loading}
                size="middle"
                pagination={{ pageSize: 6, showSizeChanger: false }}
                rowClassName={(record) => (record.user_id === selectedReport?.user_id ? 'macos-table-row selected-row' : 'macos-table-row')}
                onRow={(record) => ({ onClick: () => setSelectedUserId(record.user_id) })}
              />
            )}
          </Card>
        </Col>

        <Col xs={24} lg={9}>
          <Space direction="vertical" size={24} style={{ width: '100%' }}>
            <Card title={<span style={{ fontWeight: 600 }}>风险分布</span>}>
              <Space direction="vertical" size={16} style={{ width: '100%' }}>
                {[
                  { label: '高风险', count: highRiskCount, color: token.colorError },
                  { label: '中风险', count: mediumRiskCount, color: token.colorWarning },
                  { label: '低风险', count: lowRiskCount, color: token.colorSuccess },
                ].map((item) => (
                  <div key={item.label} className="meter-row">
                    <div className="meter-head">
                      <Typography.Text>{item.label}</Typography.Text>
                      <Typography.Text strong className="mono">
                        {item.count}
                      </Typography.Text>
                    </div>
                    <Progress
                      percent={Math.round((item.count / Math.max(1, analysis.student_count)) * 100)}
                      strokeColor={item.color}
                    />
                  </div>
                ))}
              </Space>
            </Card>

            <Card title={<span style={{ fontWeight: 600 }}>学生状态评估报告</span>}>
              {selectedReport ? (
                <Space direction="vertical" size={16} style={{ width: '100%' }}>
                  <Flex align="center" justify="space-between" gap={12}>
                    <div>
                      <Typography.Title level={4} style={{ margin: 0 }}>
                        {selectedReport.name}
                      </Typography.Title>
                      <Typography.Text type="secondary" className="mono">
                        {selectedReport.class_name} / {selectedReport.user_id}
                      </Typography.Text>
                    </div>
                    {riskTag(selectedReport.risk_level)}
                  </Flex>

                  <Progress
                    type="dashboard"
                    percent={selectedReport.risk_score}
                    strokeColor={selectedReport.risk_score >= 60 ? token.colorError : selectedReport.risk_score >= 30 ? token.colorWarning : token.colorSuccess}
                    format={(percent) => `${percent ?? 0}`}
                  />

                  <Descriptions column={1} size="small" colon={false}>
                    <Descriptions.Item label={<span className="metric-label">近30天出勤</span>}>
                      {(selectedReport.features.attendance_rate_30d * 100).toFixed(1)}%
                    </Descriptions.Item>
                    <Descriptions.Item label={<span className="metric-label">近30天缺勤</span>}>
                      {selectedReport.features.absent_count_30d} 天
                    </Descriptions.Item>
                    <Descriptions.Item label={<span className="metric-label">近30天重复</span>}>
                      {selectedReport.features.duplicate_count_30d} 次
                    </Descriptions.Item>
                    <Descriptions.Item label={<span className="metric-label">置信度</span>}>
                      {(selectedReport.confidence * 100).toFixed(1)}%
                    </Descriptions.Item>
                  </Descriptions>

                  <Alert type="info" showIcon icon={<Sparkles size={15} />} message={selectedReport.summary} description={selectedReport.suggestion} />
                </Space>
              ) : (
                <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="请选择学生" />
              )}
            </Card>
          </Space>
        </Col>
      </Row>
    </Space>
  );
};

export default StudentAnalysis;
