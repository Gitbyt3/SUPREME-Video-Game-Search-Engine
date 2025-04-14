// counterStore.tsx
import { createStore } from '../hooks/createStore';

// Define your state and action types for the counter
interface AppState {
  useLTR: boolean;
}

type AppAction =
  | { type: 'toggleLTR'}
  | { type: 'setLTR', data: boolean };

// Create a reducer function for the counter store
const appReducer = (state: AppState, action: AppAction): AppState => {
  switch (action.type) {
    case 'toggleLTR':
      return Object.assign({}, state, { useLTR: !state.useLTR });
    case 'setLTR':
      return Object.assign({}, state, { useLTR: action.data });
    default:
      return state;
  }
};

// Provide the initial state for the counter
const initialCounterState: AppState = { useLTR: false };

// Generate a store using createStore
export const { StoreProvider: AppProvider, useStore: useAppStore } = createStore<
  AppState,
  AppAction
>(appReducer, initialCounterState);
