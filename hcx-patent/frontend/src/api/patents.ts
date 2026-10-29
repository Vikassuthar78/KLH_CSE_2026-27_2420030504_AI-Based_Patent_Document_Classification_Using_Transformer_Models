import { api } from './client';
import type { ClassificationResult } from '../types';

export const patentsApi = {
  classify: (text: string, modelName?: string) =>
    api.post<ClassificationResult>('/patents/classify', {
      text,
      model_name: modelName,
    }).then((r) => r.data),

  classifyFile: (file: File, modelName?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    if (modelName) formData.append('model_name', modelName);
    return api.post<ClassificationResult>('/patents/classify/file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then((r) => r.data);
  },

  getModels: () =>
    api.get<{ models: string[] }>('/patents/models').then((r) => r.data),

  getSample: () =>
    api.get<{ text: string; title?: string }>('/patents/sample').then((r) => r.data),
};
