import React, { useState, useEffect } from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { Terminal, Users, Camera, Activity, Database } from 'lucide-react';

const Layout: React.FC = () => {
  const [time, setTime] = useState(new Date());
  const location = useLocation();

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const navItems = [
    { path: '/live', label: 'Live Stream', icon: <Camera size={18} /> },
    { path: '/register', label: 'Register', icon: <Users size={18} /> },
    { path: '/records', label: 'Records', icon: <Database size={18} /> },
    { path: '/stats', label: 'Analytics', icon: <Activity size={18} /> },
  ];

  return (
    <div style={{ display: 'flex', minHeight: '100vh', flexDirection: 'column' }}>
      <header style={{ 
        borderBottom: '1px solid var(--border-color)', 
        padding: '16px 24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        backgroundColor: 'rgba(0,0,0,0.8)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Terminal className="glow" />
          <h1 style={{ fontSize: '1.2rem', margin: 0 }} className="glow">ASCII.FACE_REC_SYS // v1.0.0</h1>
        </div>
        <div style={{ fontSize: '0.9rem', color: 'var(--text-dim)' }}>
          SYS.TIME: {time.toLocaleTimeString()}
        </div>
      </header>

      <div style={{ display: 'flex', flex: 1 }}>
        <aside style={{ 
          width: '240px', 
          borderRight: '1px solid var(--border-color)',
          padding: '24px 0',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <div style={{ padding: '0 24px', marginBottom: '16px', fontSize: '0.8rem', color: 'var(--text-dim)' }}>
            &gt; SELECT_MODULE:
          </div>
          <nav style={{ display: 'flex', flexDirection: 'column' }}>
            {navItems.map((item) => {
              const isActive = location.pathname.startsWith(item.path);
              return (
                <NavLink 
                  key={item.path} 
                  to={item.path}
                  style={{
                    padding: '12px 24px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    color: isActive ? 'var(--bg-color)' : 'var(--text-color)',
                    backgroundColor: isActive ? 'var(--text-color)' : 'transparent',
                    textDecoration: 'none',
                    borderLeft: isActive ? '4px solid var(--text-color)' : '4px solid transparent',
                    transition: 'none'
                  }}
                >
                  {item.icon}
                  <span style={{ fontWeight: isActive ? 'bold' : 'normal' }}>
                    {isActive ? '> ' : '  '}{item.label}
                  </span>
                </NavLink>
              );
            })}
          </nav>
        </aside>

        <main style={{ flex: 1, padding: '32px', position: 'relative' }}>
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
