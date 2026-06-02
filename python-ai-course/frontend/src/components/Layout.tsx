import React, { useState, useEffect } from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { Users, Camera, Activity, Database, ShieldCheck } from 'lucide-react';

const Layout: React.FC = () => {
  const [time, setTime] = useState(new Date());
  const location = useLocation();

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const navItems = [
    { path: '/live', label: 'LIVE_STREAM', icon: <Camera size={18} /> },
    { path: '/register', label: 'REGISTER_FACE', icon: <Users size={18} /> },
    { path: '/records', label: 'DATA_RECORDS', icon: <Database size={18} /> },
    { path: '/stats', label: 'SYS_ANALYTICS', icon: <Activity size={18} /> },
  ];

  return (
    <div style={{ display: 'flex', minHeight: '100vh', flexDirection: 'column' }}>
      {/* Header */}
      <header style={{ 
        borderBottom: '1px solid var(--accent-color)', 
        padding: '16px 24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        backgroundColor: 'rgba(0, 15, 0, 0.8)',
        backdropFilter: 'blur(8px)',
        zIndex: 100
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '40px', height: '40px', background: 'var(--accent-color)', color: 'var(--bg-color)' }}>
            <ShieldCheck size={24} />
          </div>
          <div>
            <h1 style={{ fontSize: '1.2rem', margin: 0, letterSpacing: '2px' }} className="glow-text">
              ASCII.FACE_REC_SYS <span className="blinker">_</span>
            </h1>
            <div style={{ fontSize: '0.7rem', color: 'var(--cyan-color)' }}>KERNEL_VERSION // 1.0.4.stable</div>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)', textAlign: 'right' }}>
            <div>SYSTEM_TIME</div>
            <div className="glow-text" style={{ fontSize: '1.1rem', color: 'var(--text-color)' }}>
              {time.toLocaleTimeString()}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Sidebar */}
        <aside style={{ 
          width: '260px', 
          borderRight: '1px solid var(--border-color)',
          backgroundColor: 'rgba(2, 5, 2, 0.8)',
          padding: '32px 0',
          display: 'flex',
          flexDirection: 'column',
          zIndex: 90
        }}>
          <div style={{ padding: '0 24px', marginBottom: '24px', fontSize: '0.75rem', color: 'var(--text-dim)', letterSpacing: '1px' }}>
            [ DIRECTORY_ACCESS ]
          </div>
          <nav style={{ display: 'flex', flexDirection: 'column', gap: '8px', padding: '0 12px' }}>
            {navItems.map((item) => {
              const isActive = location.pathname.startsWith(item.path);
              return (
                <NavLink 
                  key={item.path} 
                  to={item.path}
                  style={{
                    padding: '12px 16px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    color: isActive ? 'var(--bg-color)' : 'var(--text-color)',
                    backgroundColor: isActive ? 'var(--accent-color)' : 'transparent',
                    border: isActive ? '1px solid var(--accent-color)' : '1px solid transparent',
                    textDecoration: 'none',
                    transition: 'all 0.2s',
                    boxShadow: isActive ? '0 0 10px rgba(0,255,65,0.3)' : 'none',
                    fontWeight: isActive ? 'bold' : 'normal'
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) e.currentTarget.style.borderColor = 'var(--border-light)';
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) e.currentTarget.style.borderColor = 'transparent';
                  }}
                >
                  {item.icon}
                  <span>
                    {isActive ? '» ' : '  '}{item.label}
                  </span>
                </NavLink>
              );
            })}
          </nav>
          
          <div style={{ marginTop: 'auto', padding: '24px', fontSize: '0.7rem', color: 'var(--text-dark)' }}>
            SECURE_CONN_ESTABLISHED<br/>
            ENCRYPTION: AES-256
          </div>
        </aside>

        {/* Page View */}
        <main style={{ flex: 1, padding: '40px', overflowY: 'auto', position: 'relative', zIndex: 10 }}>
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
