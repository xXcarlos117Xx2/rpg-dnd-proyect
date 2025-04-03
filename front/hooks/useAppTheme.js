import { useMemo } from 'react';
import { themes } from '../theme';
import useGlobalReducer from './useGlobalReducer';
export default function useAppTheme() {
  const { store, dispatch } = useGlobalReducer();

  const theme = useMemo(() => themes[store.theme] || themes.light, [store.theme]);

  return {
    theme,
    themeName: store.theme,
    setThemeName: (t) => dispatch({ type: 'SET_THEME', payload: t }),
  };
}
