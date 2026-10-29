import { api } from './client';
import type { TaxonomyNode } from '../types';

export const taxonomyApi = {
  getTree: () =>
    api.get<TaxonomyNode[]>('/taxonomy/tree').then((r) => r.data),

  search: (query: string) =>
    api.get<TaxonomyNode[]>('/taxonomy/search', { params: { q: query } }).then((r) => r.data),

  getNode: (code: string) =>
    api.get<TaxonomyNode>(`/taxonomy/${code}`).then((r) => r.data),

  validate: () =>
    api.post('/taxonomy/validate').then((r) => r.data),
};
