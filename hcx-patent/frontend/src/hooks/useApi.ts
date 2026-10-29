import { useState, useEffect, useCallback } from 'react';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

interface UseApiReturn<T> extends UseApiState<T> {
  refetch: () => void;
}

export function useApi<T>(
  fetcher: () => Promise<T>,
  deps: any[] = [],
  immediate = true
): UseApiReturn<T> {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: immediate,
    error: null,
  });

  const fetch = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const data = await fetcher();
      setState({ data, loading: false, error: null });
    } catch (err: any) {
      const message =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        err.message ||
        'An unexpected error occurred';
      setState({ data: null, loading: false, error: message });
    }
  }, deps);

  useEffect(() => {
    if (immediate) {
      fetch();
    }
  }, [fetch, immediate]);

  return { ...state, refetch: fetch };
}

export function useLazyApi<T, A extends any[]>(
  fetcher: (...args: A) => Promise<T>
): {
  data: T | null;
  loading: boolean;
  error: string | null;
  execute: (...args: A) => Promise<T | null>;
  reset: () => void;
} {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const execute = useCallback(
    async (...args: A) => {
      setState({ data: null, loading: true, error: null });
      try {
        const data = await fetcher(...args);
        setState({ data, loading: false, error: null });
        return data;
      } catch (err: any) {
        const message =
          err.response?.data?.detail ||
          err.response?.data?.message ||
          err.message ||
          'An unexpected error occurred';
        setState({ data: null, loading: false, error: message });
        return null;
      }
    },
    [fetcher]
  );

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  return { ...state, execute, reset };
}
