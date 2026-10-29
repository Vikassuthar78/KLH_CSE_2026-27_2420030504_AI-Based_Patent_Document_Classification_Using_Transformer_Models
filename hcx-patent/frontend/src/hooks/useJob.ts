import { useState, useEffect, useCallback, useRef } from 'react';
import { experimentsApi } from '../api/experiments';
import type { JobStatus } from '../types';

export function useJob(initialJobId?: string, pollIntervalMs = 3000) {
  const [jobId, setJobId] = useState<string | null>(initialJobId || null);
  const [status, setStatus] = useState<JobStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const poll = useCallback(
    async (jid: string) => {
      try {
        const jobStatus = await experimentsApi.getJobStatus(jid);
        setStatus(jobStatus);
        if (jobStatus.status === 'completed' || jobStatus.status === 'failed') {
          stopPolling();
          if (jobStatus.status === 'failed') {
            setError(jobStatus.error || 'Job failed');
          }
        }
      } catch (err: any) {
        setError(err.message || 'Failed to poll job status');
        stopPolling();
      }
    },
    [stopPolling]
  );

  const startJob = useCallback(
    (newJobId: string) => {
      stopPolling();
      setJobId(newJobId);
      setStatus(null);
      setError(null);
      poll(newJobId);
      intervalRef.current = setInterval(() => poll(newJobId), pollIntervalMs);
    },
    [poll, pollIntervalMs, stopPolling]
  );

  useEffect(() => {
    return () => stopPolling();
  }, [stopPolling]);

  return {
    jobId,
    status,
    error,
    isPolling: intervalRef.current !== null,
    isRunning: status?.status === 'running' || status?.status === 'pending',
    isCompleted: status?.status === 'completed',
    isFailed: status?.status === 'failed',
    progress: status?.progress,
    startJob,
    stopPolling,
  };
}
