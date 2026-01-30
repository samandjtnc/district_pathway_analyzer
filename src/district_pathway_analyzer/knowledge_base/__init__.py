"""
Knowledge base module containing reference documents and frameworks.

This module provides access to:
- AI Foundations curriculum information
- National Career Clusters Framework (Digital Technology)
"""

from district_pathway_analyzer.knowledge_base.ai_foundations import AI_FOUNDATIONS_CURRICULUM
from district_pathway_analyzer.knowledge_base.digital_tech_cluster import (
    DIGITAL_TECH_CLUSTER,
    DIGITAL_TECH_SUB_CLUSTERS,
)

__all__ = [
    "AI_FOUNDATIONS_CURRICULUM",
    "DIGITAL_TECH_CLUSTER",
    "DIGITAL_TECH_SUB_CLUSTERS",
]
