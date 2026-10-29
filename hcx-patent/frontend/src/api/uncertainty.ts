import { api } from './client';
import type { ConformalResult, DriftResult } from '../types';

export const uncertaintyApi = {
  runConformal: (data: {
    target_coverage: number;
    method?: string;
  }) =>
    api.post<ConformalResult>('/uncertainty/conformal', data).then((r) => r.data),

  getCalibration: () =>
    api.get('/uncertainty/calibration').then((r) => r.data),

  runDrift: (data: {
    year_cutoff: number;
  }) =>
    api.post<DriftResult>('/uncertainty/drift', data).then((r) => r.data),

  getDriftResults: () =>
    api.get<DriftResult>('/uncertainty/drift').then((r) => r.data),
};
