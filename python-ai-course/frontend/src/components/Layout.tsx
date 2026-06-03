import React, { useState } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import {
  Avatar,
  Button,
  Drawer,
  Grid,
  Layout as AntLayout,
  Menu,
  Typography,
  theme,
  type MenuProps,
} from 'antd';
import {
  Activity,
  Camera,
  Database,
  Fingerprint,
  Menu as MenuIcon,
  Moon,
  Sun,
  Users,
} from 'lucide-react';
import { useThemeMode } from '../theme/themeContext';

const { Header, Sider, Content } = AntLayout;
const { useBreakpoint } = Grid;

type NavItem = { key: string; label: string; icon: React.ReactNode };

const NAV: NavItem[] = [
  { key: '/live', label: '实时签到 (Live)', icon: <Camera size={18} /> },
  { key: '/register', label: '人脸注册 (Register)', icon: <Users size={18} /> },
  { key: '/records', label: '签到记录 (Records)', icon: <Database size={18} /> },
  { key: '/stats', label: '数据分析 (Analytics)', icon: <Activity size={18} /> },
];

const Layout: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { mode, toggle } = useThemeMode();
  const { token } = theme.useToken();
  const screens = useBreakpoint();
  const [drawerOpen, setDrawerOpen] = useState(false);

  const isDesktop = !!screens.lg;
  const current = NAV.find((item) => location.pathname.startsWith(item.key));
  const selectedKey = current ? current.key : '/live';

  const handleSelect: MenuProps['onClick'] = ({ key }) => {
    navigate(key);
    setDrawerOpen(false);
  };

  const menu = (
    <Menu
      mode="inline"
      selectedKeys={[selectedKey]}
      onClick={handleSelect}
      items={NAV as MenuProps['items']}
      style={{ background: 'transparent', borderInlineEnd: 'none' }}
    />
  );

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Header
        style={{
          position: 'sticky',
          top: 0,
          zIndex: 100,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          paddingInline: 'clamp(16px, 3vw, 32px)',
          height: 64,
          background: token.colorBgContainer,
          borderBottom: `1px solid ${token.colorBorderSecondary}`,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, minWidth: 0 }}>
          {!isDesktop && (
            <Button
              type="text"
              aria-label="打开菜单"
              icon={<MenuIcon size={20} />}
              onClick={() => setDrawerOpen(true)}
            />
          )}
          <div
            style={{
              background: token.colorPrimary,
              color: '#fff',
              width: 36,
              height: 36,
              borderRadius: 8,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}
          >
            <Fingerprint size={20} />
          </div>
          <div style={{ lineHeight: 1.2, minWidth: 0 }}>
            <Typography.Title level={5} style={{ margin: 0, whiteSpace: 'nowrap' }}>
              智能人脸签到系统
            </Typography.Title>
            {screens.sm && (
              <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                Face Recognition Attendance System
              </Typography.Text>
            )}
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexShrink: 0 }}>
          <Button
            type="text"
            shape="circle"
            aria-label="切换明暗主题"
            icon={mode === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
            onClick={toggle}
          />
          {screens.md && (
            <div style={{ textAlign: 'right', lineHeight: 1.2 }}>
              <div style={{ fontSize: 14, fontWeight: 500 }}>Admin User</div>
              <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                System Administrator
              </Typography.Text>
            </div>
          )}
          <Avatar style={{ backgroundColor: token.colorPrimary }}>A</Avatar>
        </div>
      </Header>

      <AntLayout style={{ width: '100%', maxWidth: 1920, margin: '0 auto' }}>
        {isDesktop && (
          <Sider
            width={248}
            style={{
              background: token.colorBgContainer,
              borderInlineEnd: `1px solid ${token.colorBorderSecondary}`,
            }}
          >
            <div style={{ padding: '20px 12px' }}>
              <Typography.Text
                type="secondary"
                style={{ fontSize: 12, letterSpacing: '0.08em', paddingInlineStart: 12 }}
              >
                MENU
              </Typography.Text>
              <div style={{ marginTop: 12 }}>{menu}</div>
            </div>
          </Sider>
        )}

        <Content style={{ padding: 'clamp(16px, 2.5vw, 32px)', minWidth: 0 }}>
          <Outlet />
        </Content>
      </AntLayout>

      <Drawer
        title="菜单"
        placement="left"
        width={260}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        styles={{ body: { padding: 12 } }}
      >
        {menu}
      </Drawer>
    </AntLayout>
  );
};

export default Layout;
