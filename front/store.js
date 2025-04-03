export const initialStore = () => ({
    theme: localStorage.getItem('theme') || 'light',
  });
  
  export default function storeReducer(state, action) {
    switch (action.type) {
      case 'SET_THEME':
        const newTheme = action.payload;
        localStorage.setItem('theme', newTheme);
        return {
          ...state,
          theme: newTheme,
        };
      default:
        return state;
    }
  }
  