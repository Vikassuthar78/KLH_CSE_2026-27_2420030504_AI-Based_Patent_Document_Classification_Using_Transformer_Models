"""CPC/IPC hierarchy navigation and taxonomy validation endpoints."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.config import get_settings
from app.datasets.discovery import discover_datasets
from app.taxonomy.cpc_tree import CPCTaxonomy

router = APIRouter(prefix="/taxonomy", tags=["Taxonomy"])

# Global cached taxonomy instance
_taxonomy_cache: Optional[CPCTaxonomy] = None


def get_cached_taxonomy() -> CPCTaxonomy:
    """Load or return cached taxonomy built from dataset codes."""
    global _taxonomy_cache
    if _taxonomy_cache is None:
        settings = get_settings()
        files = discover_datasets(settings.DATASET_ROOT)
        parquets = [f.path for f in files if f.format == "parquet"]

        tax = CPCTaxonomy()
        if parquets:
            import pyarrow.parquet as pq

            pf = pq.ParquetFile(parquets[0])
            df = pf.read_row_group(0).to_pandas()
            all_codes = []
            for val in df["cpc_ids"].dropna():
                all_codes.extend([c.strip() for c in str(val).split(",") if c.strip()])

            from collections import Counter

            counts = Counter(all_codes)
            tax.build_from_codes(list(counts.keys()), counts=dict(counts))
        else:
            # Fallback seed codes
            seed = ["A01H", "A61K", "B01D", "C07K", "G06F", "G06Q", "H01L", "H04L", "H04N", "Y10T"]
            tax.build_from_codes(seed)

        _taxonomy_cache = tax

    return _taxonomy_cache


@router.get("/tree")
def get_tree() -> List[Dict[str, Any]]:
    """Return complete hierarchical taxonomy tree."""
    tax = get_cached_taxonomy()
    return tax.get_tree()


@router.get("/search")
def search_taxonomy(query: str = Query(..., min_length=1)) -> List[Dict[str, Any]]:
    """Search taxonomy codes by symbol or keyword."""
    tax = get_cached_taxonomy()
    return tax.search(query)


@router.get("/node/{code}")
def get_node(code: str) -> Dict[str, Any]:
    """Get metadata and ancestry path for a specific code."""
    tax = get_cached_taxonomy()
    code_clean = code.strip().upper()
    ancestors = tax.get_ancestors(code_clean)
    parent = tax.get_parent(code_clean)

    return {
        "code": code_clean,
        "ancestors": ancestors,
        "parent": parent,
        "level": "section" if len(code_clean) == 1 else ("class" if len(code_clean) == 3 else "subclass"),
    }

