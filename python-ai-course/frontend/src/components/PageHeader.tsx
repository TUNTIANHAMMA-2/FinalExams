import React from 'react';
import { Typography } from 'antd';

type PageHeaderProps = {
  title: string;
  subtitle?: string;
  /** 大写字间距的 Latin eyebrow（Swiss 栏目标签）；省略时仅显示钴蓝短杠 */
  kicker?: string;
  /** 右侧操作区（按钮等） */
  actions?: React.ReactNode;
};

/**
 * 全站统一页头（Swiss Modernism 2.0）：
 * 钴蓝短强调杠 + 大写 Latin kicker → 大号粗体标题 → 描述，底部发丝分隔线。
 */
const PageHeader: React.FC<PageHeaderProps> = ({ title, subtitle, kicker, actions }) => (
  <header className="page-header">
    <div style={{ minWidth: 0 }}>
      <div className="ph-kicker">
        <span className="accent-rule" />
        {kicker && <span className="swiss-eyebrow">{kicker}</span>}
      </div>
      <h1 className="ph-title">{title}</h1>
      {subtitle && (
        <Typography.Text type="secondary" style={{ fontSize: 14 }}>
          {subtitle}
        </Typography.Text>
      )}
    </div>
    {actions && <div className="ph-actions">{actions}</div>}
  </header>
);

export default PageHeader;
