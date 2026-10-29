"""Pydantic schemas for taxonomy APIs."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TaxonomyNode(BaseModel):
    """A single node in the CPC taxonomy tree."""
    code: str
    level: str  # section, class, subclass
    description: Optional[str] = None
    parent_code: Optional[str] = None
    children: List[str] = Field(default_factory=list)
    patent_count: int = 0


class TaxonomyTreeResponse(BaseModel):
    """Full or partial taxonomy tree."""
    root_nodes: List[TaxonomyNode]
    total_nodes: int
    levels: Dict[str, int]  # e.g. {"section": 9, "class": 130, "subclass": 411}


class TaxonomySearchResponse(BaseModel):
    """Taxonomy search results."""
    results: List[TaxonomyNode]
    total: int


class TaxonomyValidationResponse(BaseModel):
    """Taxonomy consistency validation result."""
    valid: bool
    issues: List[Dict[str, Any]]
    summary: str


class TaxonomyNodeDetail(BaseModel):
    """Detailed information for a single taxonomy node."""
    code: str
    level: str
    description: Optional[str] = None
    parent: Optional[TaxonomyNode] = None
    children: List[TaxonomyNode] = Field(default_factory=list)
    patent_count: int = 0
    sample_patents: List[Dict[str, Any]] = Field(default_factory=list)
