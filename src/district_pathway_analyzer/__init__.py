"""
District Pathway Analyzer
=========================

AI-Powered District CTE Pathway Analysis Tool for analyzing school district
CTE programs to identify strategic opportunities for integrating Code.org's
AI Foundations curriculum.

"""

__version__ = "1.0.0"
__author__ = "Code.org"

from district_pathway_analyzer.models import (
    DistrictInput,
    CourseInventoryItem,
    DistrictLandscape,
    AlignmentReport,
    PathwayDesign,
    DistrictAnalysisReport,
)
from district_pathway_analyzer.analyzer import DistrictPathwayAnalyzer

__all__ = [
    "DistrictPathwayAnalyzer",
    "DistrictInput",
    "CourseInventoryItem",
    "DistrictLandscape",
    "AlignmentReport",
    "PathwayDesign",
    "DistrictAnalysisReport",
]
