import { api } from './client';
import type { Experiment, MetricComparison, JobStatus } from '../types';

export const experimentsApi = {
  list: () =>
    api.get<Experiment[]>('/experiments').then((r) => r.data),

  get: (id: string) =>
    api.get<Experiment>(`/experiments/${id}`).then((r) => r.data),

  create: (data: {
    name: string;
    type: string;
    description?: string;
    config?: Record<string, any>;
  }) =>
    api.post<Experiment>('/experiments', data).then((r) => r.data),

  run: (id: string) =>
    api.post<JobStatus>(`/experiments/${id}/run`).then((r) => r.data),

  delete: (id: string) =>
    api.delete(`/experiments/${id}`).then((r) => r.data),

  getResults: (id: string) =>
    api.get(`/experiments/${id}/results`).then((r) => r.data),

  compare: (ids: string[]) =>
    api.post<MetricComparison>('/experiments/compare', { experiment_ids: ids }).then((r) => r.data),

  getJobStatus: (jobId: string) =>
    api.get<JobStatus>(`/jobs/${jobId}`).then((r) => r.data),
};
