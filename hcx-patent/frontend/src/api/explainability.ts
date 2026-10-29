import { api } from './client';
import type { ExplainabilityResult, Attribution } from '../types';

export const explainabilityApi = {
  explain: (data: {
    text: string;
    model_name?: string;
    method?: string;
    target_class?: string;
  }) =>
    api.post<ExplainabilityResult>('/explainability/explain', data).then((r) => r.data),

  getMethods: () =>
    api.get<{ methods: string[] }>('/explainability/methods').then((r) => r.data),

  getFaithfulness: (data: {
    text: string;
    model_name?: string;
    method?: string;
  }) =>
    api.post('/explainability/faithfulness', data).then((r) => r.data),

  getStability: (data: {
    text: string;
    model_name?: string;
    method?: string;
  }) =>
    api.post('/explainability/stability', data).then((r) => r.data),

  exportReport: (data: {
    text: string;
    model_name?: string;
    method?: string;
  }) =>
    api.post('/explainability/report', data, { responseType: 'blob' }).then((r) => r.data),
};
