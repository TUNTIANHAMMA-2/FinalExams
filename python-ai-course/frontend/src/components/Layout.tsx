import React, { useEffect, useState } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { Button, Drawer, Grid, Tooltip } from 'antd';
import {
  Activity,
  Brain,
  Database,
  Fingerprint,
  Menu as MenuIcon,
  Moon,
  ScanFace,
  Sun,
  UserPlus,
} from 'lucide-react';
import { useThemeMode } from '../theme/themeContext';

const { useBreakpoint } = Grid;

type NavItem = { key: string; label: string; icon: React.ReactNode };

const NAV: NavItem[] = [
  { key: '/live', label: '实时监控', icon: <ScanFace size={18} /> },
  { key: '/register', label: '用户注册', icon: <UserPlus size={18} /> },
  { key: '/records', label: '数据中心', icon: <Database size={18} /> },
  { key: '/stats', label: '系统分析', icon: <Activity size={18} /> },
  { key: '/analysis', label: '智能分析', icon: <Brain size={18} /> },
];

const Layout: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { mode, toggle } = useThemeMode();
  const screens = useBreakpoint();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [now, setNow] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const isDesktop = !!screens.lg;
  const current = NAV.find((item) => location.pathname.startsWith(item.key));
  const selectedKey = current ? current.key : '/live';
  const isWide = location.pathname.startsWith('/live'); // 实时监控页放开内容区宽度

  const go = (key: string) => {
    navigate(key);
    setDrawerOpen(false);
  };

  const timeString = now.toLocaleTimeString('zh-CN', { hour12: false });
  const dateString = now.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', weekday: 'short' });

  const brand = (
    <div className="sidebar-brand">
      <div className="brand-mark">
        <Fingerprint size={21} />
      </div>
      <div className="brand-text">
        <span className="brand-title">智能签到</span>
        <span className="brand-sub">Vision Console</span>
      </div>
    </div>
  );

  const navList = (
    <nav className="sidebar-nav">
      <div className="nav-section">导航 · Navigation</div>
      {NAV.map((item) => {
        const isActive = selectedKey === item.key;
        return (
          <div
            key={item.key}
            className={`nav-item ${isActive ? 'active' : ''}`}
            role="button"
            tabIndex={0}
            aria-current={isActive ? 'page' : undefined}
            onClick={() => go(item.key)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                go(item.key);
              }
            }}
          >
            <span className="nav-icon">{item.icon}</span>
            <span>{item.label}</span>
          </div>
        );
      })}
    </nav>
  );

  const footer = (
    <div className="sidebar-footer">
      <div className="sidebar-clock">
        <span className="clock-time">{timeString}</span>
        <span className="clock-date">{dateString}</span>
      </div>
      <Button block icon={mode === 'dark' ? <Sun size={15} /> : <Moon size={15} />} onClick={toggle}>
        {mode === 'dark' ? '浅色模式' : '深色模式'}
      </Button>
    </div>
  );

  if (isDesktop) {
    return (
      <div className="console-shell">
        <aside className="sidebar">
          {brand}
          {navList}
          {footer}
        </aside>
        <main className="content-area">
          <div className={`content-inner${isWide ? ' content-inner--wide' : ''}`}>
            <Outlet />
          </div>
        </main>
      </div>
    );
  }

  return (
    <div>
      <div className="mobile-appbar">
        <Button type="text" aria-label="打开菜单" icon={<MenuIcon size={20} />} onClick={() => setDrawerOpen(true)} />
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div className="brand-mark" style={{ width: 30, height: 30, borderRadius: 0 }}>
            <Fingerprint size={16} />
          </div>
          <span className="brand-title" style={{ fontSize: 14 }}>智能签到</span>
        </div>
        <Tooltip title="切换主题">
          <Button
            type="text"
            aria-label="切换明暗主题"
            icon={mode === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
            onClick={toggle}
          />
        </Tooltip>
      </div>

      <main className="content-area" style={{ height: 'auto', overflowY: 'visible' }}>
        <div className={`content-inner${isWide ? ' content-inner--wide' : ''}`} style={{ paddingTop: 22 }}>
          <Outlet />
        </div>
      </main>

      <Drawer
        placement="left"
        width={272}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        closable={false}
        styles={{ body: { padding: '20px 16px', display: 'flex', flexDirection: 'column' } }}
      >
        {brand}
        {navList}
        {footer}
      </Drawer>
    </div>
  );
};

export default Layout;
