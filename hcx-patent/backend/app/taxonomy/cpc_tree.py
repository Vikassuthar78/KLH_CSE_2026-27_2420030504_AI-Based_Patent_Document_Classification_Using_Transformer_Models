"""CPC (Cooperative Patent Classification) taxonomy hierarchy tree and navigation."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

# Standard CPC Section Descriptions
CPC_SECTION_DESCRIPTIONS = {
    "A": "Human Necessities",
    "B": "Performing Operations; Transporting",
    "C": "Chemistry; Metallurgy",
    "D": "Textiles; Paper",
    "E": "Fixed Constructions",
    "F": "Mechanical Engineering; Lighting; Heating; Weapons; Blasting",
    "G": "Physics",
    "H": "Electricity",
    "Y": "General Tagging of New Technological Developments",
}


class CPCTaxonomy:
    """CPC hierarchy parser, tree builder, and validation engine."""

    def __init__(self) -> None:
        self.sections: Dict[str, Dict[str, Any]] = {}
        self.classes: Dict[str, Dict[str, Any]] = {}
        self.subclasses: Dict[str, Dict[str, Any]] = {}
        self.code_counts: Dict[str, int] = {}

    def get_ancestors(self, code: str) -> List[str]:
        """Return list of ancestor codes in order: [Section, Class].

        Example: 'A01H' -> ['A', 'A01']
        """
        code = code.strip().upper()
        if len(code) < 2:
            return []

        section = code[0]
        ancestors = [section]

        if len(code) >= 3:
            # Class: e.g. A01
            cls = code[:3]
            ancestors.append(cls)

        return ancestors

    def get_parent(self, code: str) -> Optional[str]:
        """Return direct parent code."""
        code = code.strip().upper()
        if len(code) == 1:
            return None  # Section has no parent
        elif len(code) == 3:
            return code[0]  # Class parent is Section
        elif len(code) >= 4:
            return code[:3]  # Subclass parent is Class
        return None

    def is_valid_parent_child(self, parent: str, child: str) -> bool:
        """Validate whether parent is a legitimate direct or ancestor parent of child."""
        parent = parent.strip().upper()
        child = child.strip().upper()

        if parent == child:
            return False

        # Direct parent checks
        if len(parent) == 1:  # Parent is Section
            return child.startswith(parent) and len(child) > 1
        elif len(parent) == 3:  # Parent is Class
            return child.startswith(parent) and len(child) > 3
        return False

    def build_from_codes(self, codes: List[str], counts: Optional[Dict[str, int]] = None) -> None:
        """Construct the hierarchy from an observed list of CPC codes."""
        self.sections.clear()
        self.classes.clear()
        self.subclasses.clear()
        self.code_counts = counts or {}

        for raw_code in codes:
            code = raw_code.strip().upper()
            if not code:
                continue

            section = code[0]
            if section not in self.sections:
                self.sections[section] = {
                    "code": section,
                    "description": CPC_SECTION_DESCRIPTIONS.get(section, f"Section {section}"),
                    "level": "section",
                    "classes": {},
                    "count": 0,
                }
            self.sections[section]["count"] += self.code_counts.get(code, 1)

            if len(code) >= 3:
                cls = code[:3]
                if cls not in self.classes:
                    self.classes[cls] = {
                        "code": cls,
                        "description": f"Class {cls}",
                        "level": "class",
                        "parent": section,
                        "subclasses": {},
                        "count": 0,
                    }
                    self.sections[section]["classes"][cls] = self.classes[cls]
                self.classes[cls]["count"] += self.code_counts.get(code, 1)

            if len(code) >= 4:
                subclass = code[:4]
                if subclass not in self.subclasses:
                    self.subclasses[subclass] = {
                        "code": subclass,
                        "description": f"Subclass {subclass}",
                        "level": "subclass",
                        "parent": code[:3],
                        "count": 0,
                    }
                    if code[:3] in self.classes:
                        self.classes[code[:3]]["subclasses"][subclass] = self.subclasses[subclass]
                self.subclasses[subclass]["count"] += self.code_counts.get(code, 1)

    def get_tree(self) -> List[Dict[str, Any]]:
        """Return full hierarchical tree formatted for frontend visualization."""
        tree = []
        for sec_code in sorted(self.sections.keys()):
            sec = self.sections[sec_code]
            sec_node = {
                "code": sec["code"],
                "description": sec["description"],
                "level": "section",
                "patent_count": sec["count"],
                "children": [],
            }
            for cls_code in sorted(sec["classes"].keys()):
                cls = sec["classes"][cls_code]
                cls_node = {
                    "code": cls["code"],
                    "description": cls["description"],
                    "level": "class",
                    "parent": sec_code,
                    "patent_count": cls["count"],
                    "children": [],
                }
                for sub_code in sorted(cls["subclasses"].keys()):
                    sub = cls["subclasses"][sub_code]
                    sub_node = {
                        "code": sub["code"],
                        "description": sub["description"],
                        "level": "subclass",
                        "parent": cls_code,
                        "patent_count": sub["count"],
                        "children": [],
                    }
                    cls_node["children"].append(sub_node)
                sec_node["children"].append(cls_node)
            tree.append(sec_node)
        return tree

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search taxonomy by code prefix or keyword."""
        q = query.strip().upper()
        results = []

        # Check sections
        for sec_code, sec in self.sections.items():
            if q in sec_code or q.lower() in sec["description"].lower():
                results.append({
                    "code": sec_code,
                    "description": sec["description"],
                    "level": "section",
                    "path": [sec_code],
                })

        # Check classes
        for cls_code, cls in self.classes.items():
            if q in cls_code or q.lower() in cls["description"].lower():
                results.append({
                    "code": cls_code,
                    "description": cls["description"],
                    "level": "class",
                    "path": [cls["parent"], cls_code],
                })

        # Check subclasses
        for sub_code, sub in self.subclasses.items():
            if q in sub_code or q.lower() in sub["description"].lower():
                results.append({
                    "code": sub_code,
                    "description": sub["description"],
                    "level": "subclass",
                    "path": [sub_code[0], sub["parent"], sub_code],
                })

        return results

