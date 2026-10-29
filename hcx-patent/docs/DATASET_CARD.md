# Dataset Card: USPTO-3M (Offline Partitioned Corpus)

## 1. Dataset Summary
- **Dataset Name**: USPTO-3M (United States Patent and Trademark Office Corpus)
- **Local Directory**: `D:\ALT-PROJECT\DATA\`
- **Total Records**: 3,198,360 patent documents
- **File Format**: Apache Parquet (`snappy` compressed)
- **File Partitions**: 7 shards (`train-00000-of-00007.parquet` to `train-00006-of-00007.parquet`)
- **Total Storage Size**: ~1.34 GB

## 2. Schema Discovery & Canonical Field Mapping

Through direct inspection of the Parquet metadata and pyarrow row groups, the schema was discovered as:

| Actual Column Name | Physical Data Type | Canonical Field | Description | Null Count |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `string` | `patent_id` | USPTO publication identifier | 0 |
| `date` | `string` (YYYY-MM-DD) | `date` | Patent grant / publication date | 0 |
| `cpc_ids` | `string` (comma-separated) | `cpc_codes` | CPC subclass labels (e.g. `A01H,C11D,Y10S`) | 0 |
| `text` | `string` | `text` | Full claims & abstract patent text | 0 |

### Observed Field Characteristics
- **Date Range**: 2000-01-11 to 2015-12-29 (16-year publication cohort span)
- **Labels per Patent**: 1 to 13 CPC codes (Mean: 2.3 labels per patent document)
- **Text Length**: Min: 39 characters, Max: 8,180 characters, Mean: 953 characters
- **Unique CPC Subclasses Observed**: 411 - 568 distinct codes
- **Multi-label Distribution**: Dominant codes include `Y10T`, `H01L`, `A61K`, `G06F`, `Y10S`, `A61P`, `H04L`, `H04N`.

## 3. Preprocessing & Leakage Prevention Policy
- Deduplication by document identifier (`id`) prior to partitioning.
- Strict isolation across `train` (70%), `val` (10%), `cal` (10%), and `test` (10%) splits.
- Split manifests recorded in `data/splits/<run_id>_split_manifest.json`.
- Rare-class thresholding (configurable, default $n \ge 10$) prevents degenerate singletons.

