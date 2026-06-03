import { createContext, useContext } from 'react';

export type ThemeMode = 'light' | 'dark';

export type ThemeContextValue = {
  mode: ThemeMode;
  toggle: () => void;
};

export const ThemeContext = createContext<ThemeContextValue>({
  mode: 'light',
  toggle: () => undefined,
});

export function useThemeMode(): ThemeContextValue {
  return useContext(ThemeContext);
}
