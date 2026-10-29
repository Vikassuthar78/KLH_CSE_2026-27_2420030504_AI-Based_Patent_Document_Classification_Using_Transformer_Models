export interface DatasetFile {
  path: string;
  name: string;
  size_bytes: number;
  format: string;
  num_rows?: number;
}

export interface DatasetProfile {
  id: string;
  name: string;
  num_rows: number;
  num_columns: number;
  columns: ColumnInfo[];
  stats: DatasetStats;
  created_at: string;
}

export interface ColumnInfo {
  name: string;
  dtype: string;
  null_count: number;
  unique_count: number;
  sample_values: string[];
}

export interface DatasetStats {
  cpc_distribution: Record<string, number>;
  date_distribution: Record<string, number>;
  text_length_stats: { min: number; max: number; mean: number; median: number };
  multi_label_stats: { min: number; max: number; mean: number };
  total_unique_cpc: number;
}

export interface Experiment {
  id: string;
  name: string;
  type: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  config: Record<string, any>;
  metrics?: Record<string, number>;
  started_at?: string;
  completed_at?: string;
  error?: string;
}

export interface ClassificationResult {
  predictions: Prediction[];
  inference_time_ms: number;
  model_name: string;
  model_type: string;
}

export interface Prediction {
  code: string;
  label: string;
  confidence: number;
  hierarchy_path: string[];
}

export interface TaxonomyNode {
  code: string;
  description: string;
  level: 'section' | 'class' | 'subclass';
  children: TaxonomyNode[];
  patent_count: number;
}

export interface Attribution {
  tokens: string[];
  scores: number[];
  method: string;
  target_class: string;
}

export interface ConformalResult {
  target_coverage: number;
  empirical_coverage: number;
  avg_set_size: number;
  coverage_by_class: Record<string, number>;
  coverage_by_year: Record<string, number>;
  prediction_sets: PredictionSet[];
}

export interface PredictionSet {
  patent_id: string;
  true_labels: string[];
  prediction_set: string[];
  set_size: number;
}

export interface JobStatus {
  id: string;
  type: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress?: number;
  result?: any;
  error?: string;
}

export interface MetricComparison {
  experiment_ids: string[];
  metrics: Record<string, Record<string, number>>;
}

export interface ValidationIssue {
  column: string;
  issue: string;
  severity: 'error' | 'warning' | 'info';
  count?: number;
}

export interface ColumnMapping {
  text_column: string;
  label_column: string;
  date_column?: string;
  id_column?: string;
}

export interface DriftResult {
  performance_by_year: Record<string, Record<string, number>>;
  random_vs_temporal: Record<string, Record<string, number>>;
  distribution_shift: Record<string, Record<string, number>>;
  calibration_drift: Record<string, number>;
  coverage_drift: Record<string, number>;
  rare_classes: RareClassInfo[];
}

export interface RareClassInfo {
  code: string;
  label: string;
  count: number;
  train_f1: number;
  test_f1: number;
}

export interface ExplainabilityResult {
  attribution: Attribution;
  faithfulness: {
    comprehensiveness: number;
    sufficiency: number;
  };
  stability: {
    score: number;
    method: string;
  };
}
