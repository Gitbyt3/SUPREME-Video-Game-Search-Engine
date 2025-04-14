import React, {
  createContext,
  useContext,
  useReducer,
  ReactNode,
  Dispatch,
} from 'react';

type ProviderProps = { children: ReactNode };

export function createStore<S, A>(
  reducer: (state: S, action: A) => S,
  initialState: S
) {
  // Define the shape of our context value
  type StoreContextType = { state: S; dispatch: Dispatch<A> };

  // Create a context with an undefined default
  const StoreContext = createContext<StoreContextType | undefined>(undefined);

  // Define the Provider component
  const StoreProvider = ({ children }: ProviderProps) => {
    const [state, dispatch] = useReducer(reducer, initialState);
    return (
      <StoreContext.Provider value={{ state, dispatch }}>
        {children}
      </StoreContext.Provider>
    );
  };

  // Custom hook to consume the context
  const useStore = (): StoreContextType => {
    const context = useContext(StoreContext);
    if (context === undefined) {
      throw new Error('useStore must be used within a StoreProvider');
    }
    return context;
  };

  return { StoreProvider, useStore };
}

