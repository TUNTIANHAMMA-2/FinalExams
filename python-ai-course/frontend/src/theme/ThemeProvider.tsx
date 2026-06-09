import React, { useEffect, useMemo, useState } from 'react';
import { App as AntApp, ConfigProvider, theme } from 'antd';
import { ThemeContext, type ThemeMode } from './themeContext';

const STORAGE_KEY = 'attendance-theme-mode';

function getInitialMode(): ThemeMode {
  if (typeof window === 'undefined') {
    return 'light';
  }
  const stored = window.localStorage.getItem(STORAGE_KEY);
  if (stored === 'light' || stored === 'dark') {
    return stored;
  }
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [mode, setMode] = useState<ThemeMode>(getInitialMode);

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, mode);
    document.documentElement.setAttribute('data-theme', mode);
  }, [mode]);

  const value = useMemo(
    () => ({
      mode,
      toggle: () => setMode((prev) => (prev === 'light' ? 'dark' : 'light')),
    }),
    [mode],
  );

  return (
    <ThemeContext.Provider value={value}>
      <ConfigProvider
        theme={{
          algorithm: mode === 'dark' ? theme.darkAlgorithm : theme.defaultAlgorithm,
          token: {
            // Swiss Modernism 2.0：单一钴蓝品牌强调色
            colorPrimary: mode === 'dark' ? '#3d5bff' : '#2440ff',
            colorInfo: mode === 'dark' ? '#3d5bff' : '#2440ff',
            colorSuccess: mode === 'dark' ? '#22c55e' : '#16a34a',
            colorWarning: mode === 'dark' ? '#f59e0b' : '#d97706',
            colorError: mode === 'dark' ? '#ef4444' : '#dc2626',
            colorLink: mode === 'dark' ? '#8aa0ff' : '#2440ff',
            colorTextLightSolid: '#ffffff', // 强调色两模式均为深色钴蓝 → 始终白字
            borderRadius: 0, // 直角
            fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'PingFang SC', 'Microsoft YaHei', sans-serif",
            colorBgContainer: mode === 'dark' ? '#18181b' : '#ffffff',
          },
          components: {
            Card: {
              borderRadiusLG: 0,
            },
            Button: {
              fontWeight: 600,
            },
            Menu: {
              itemBg: 'transparent',
              itemSelectedBg: mode === 'dark' ? 'rgba(61, 91, 255, 0.16)' : 'rgba(36, 64, 255, 0.08)',
              itemSelectedColor: mode === 'dark' ? '#8aa0ff' : '#2440ff',
            },
            Tabs: {
              inkBarColor: mode === 'dark' ? '#3d5bff' : '#2440ff',
              itemSelectedColor: mode === 'dark' ? '#8aa0ff' : '#2440ff',
              itemHoverColor: mode === 'dark' ? '#8aa0ff' : '#2440ff',
            },
            Table: {
              headerBg: 'transparent',
            },
          },
        }}
      >
        <AntApp style={{ minHeight: '100vh' }}>{children}</AntApp>
      </ConfigProvider>
    </ThemeContext.Provider>
  );
};

export default ThemeProvider;
