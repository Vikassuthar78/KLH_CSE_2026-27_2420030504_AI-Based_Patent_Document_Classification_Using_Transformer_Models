import { api } from './client';
import type { DatasetFile, DatasetProfile, ColumnMapping, ValidationIssue } from '../types';

export const datasetsApi = {
  discover: () =>
    api.get<{ files: DatasetFile[] }>('/datasets/discover').then((r) => r.data),

  getStats: () =>
    api.get('/datasets/stats').then((r) => r.data),

  profile: (filePath?: string) =>
    api.post<DatasetProfile>('/datasets/profile', filePath ? { file_path: filePath } : {}).then((r) => r.data),

  getProfile: () =>
    api.get<DatasetProfile>('/datasets/profile').then((r) => r.data),

  preview: (page = 1, pageSize = 20) =>
    api.get('/datasets/preview', { params: { page, page_size: pageSize } }).then((r) => r.data),

  validate: () =>
    api.post<{ issues: ValidationIssue[] }>('/datasets/validate').then((r) => r.data),

  setColumnMapping: (mapping: ColumnMapping) =>
    api.post('/datasets/column-mapping', mapping).then((r) => r.data),

  getColumnMapping: () =>
    api.get<ColumnMapping>('/datasets/column-mapping').then((r) => r.data),
};
