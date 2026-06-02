import React from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { Users, Camera, Activity, Database, Fingerprint } from 'lucide-react';

const Layout: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { path: '/live', label: '实时签到 (Live)', icon: <Camera size={20} /> },
    { path: '/register', label: '人脸注册 (Register)', icon: <Users size={20} /> },
    { path: '/records', label: '签到记录 (Records)', icon: <Database size={20} /> },
    { path: '/stats', label: '数据分析 (Analytics)', icon: <Activity size={20} /> },
  ];

  return (
    <div style={{ display: 'flex', minHeight: '100vh', flexDirection: 'column', backgroundColor: 'var(--bg-color)' }}>
      {/* Header */}
      <header style={{ 
        backgroundColor: 'var(--surface)', 
        borderBottom: '1px solid var(--border)', 
        padding: '16px 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'sticky',
        top: 0,
        zIndex: 10
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ 
            backgroundColor: 'var(--primary)', 
            color: 'white', 
            padding: '8px', 
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center'
          }}>
            <Fingerprint size={24} />
          </div>
          <div>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 600, margin: 0, color: 'var(--text-main)' }}>
              智能人脸签到系统
            </h1>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: 0 }}>
              Face Recognition Attendance System
            </p>
          </div>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.875rem', fontWeight: 500 }}>Admin User</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>System Administrator</div>
          </div>
          <div style={{ width: '36px', height: '36px', borderRadius: '50%', backgroundColor: '#e2e8f0', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', color: 'var(--text-muted)' }}>
            A
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div style={{ display: 'flex', flex: 1, maxWidth: '1440px', margin: '0 auto', width: '100%' }}>
        {/* Sidebar */}
        <aside style={{ 
          width: '260px', 
          backgroundColor: 'var(--bg-color)',
          padding: '32px 24px',
          display: 'flex',
          flexDirection: 'column',
          gap: '8px'
        }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '8px', letterSpacing: '0.05em' }}>
            Menu
          </div>
          <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            {navItems.map((item) => {
              const isActive = location.pathname.startsWith(item.path);
              return (
                <NavLink 
                  key={item.path} 
                  to={item.path}
                  style={{
                    padding: '10px 16px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    borderRadius: '6px',
                    color: isActive ? 'var(--primary)' : 'var(--text-muted)',
                    backgroundColor: isActive ? '#eff6ff' : 'transparent',
                    textDecoration: 'none',
                    fontWeight: isActive ? 500 : 400,
                    transition: 'all 0.2s',
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.backgroundColor = '#e2e8f0';
                      e.currentTarget.style.color = 'var(--text-main)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.backgroundColor = 'transparent';
                      e.currentTarget.style.color = 'var(--text-muted)';
                    }
                  }}
                >
                  {item.icon}
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </nav>
        </aside>

        {/* Page Content */}
        <main style={{ flex: 1, padding: '32px' }}>
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
