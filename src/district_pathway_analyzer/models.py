"""
Data models for the District Pathway Analyzer.

This module contains all the core data structures used throughout the analysis
pipeline, including enums, dataclasses, and Pydantic models.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# =============================================================================
# ENUMS
# =============================================================================


class ConfidenceLevel(str, Enum):
    """Confidence level for extracted data."""

    VERIFIED = "Verified"
    INFERRED = "Inferred"
    UNCERTAIN = "Uncertain"


class DigitalDomain(str, Enum):
    """Authoritative domain tags for Digital Technology courses.

    Aligned with Advance CTE Career Clusters and Sub-Clusters.
    """

    # Digital Technology Cluster (Core Sub-Clusters)
    DATA_AI = "Data Science & Artificial Intelligence"
    IT_SUPPORT = "Information Technology (IT) Support & Services"
    NETWORK_CYBER = "Network Systems & Cybersecurity"
    SOFTWARE_SOLUTIONS = "Software Solutions"
    WEB_CLOUD = "Web & Cloud"
    UNMANNED_VEHICLES = "Unmanned Vehicle Technology"

    # Adjacent/Embedded Clusters (Select Sub-Clusters)
    DESIGN_DIGITAL_ARTS = "Design & Digital Arts"
    ROBOTICS = "Robotics"
    ENGINEERING = "Engineering"

    # Legacy/Catch-all (for courses that don't fit cleanly)
    EMERGING_TECH = "Emerging / Applied Digital Technology"


class CourseRole(str, Enum):
    """Role classification for courses within a pathway."""

    EXPLORATORY = "exploratory"  # Broad intro, low/no prereqs
    GATEKEEPER = "gatekeeper"  # Early specialization point
    CONCENTRATOR = "concentrator"  # Advanced, specific domain
    CAPSTONE = "capstone"  # Final culminating course


class PathwayShape(str, Enum):
    """Shape pattern of pathway structure."""

    FUNNEL = "funnel"  # Wide intro → narrow specialization
    PARALLEL_SILOS = "parallel"  # Multiple disconnected entry points
    LATE_ENTRY = "late"  # Specialization without exploration
    MISSING_ENTRY = "missing"  # No clear entry point


class AIFoundationsRole(str, Enum):
    """Role for AI Foundations within the district structure."""

    PRIMARY_ENTRY = "primary_entry"  # THE entry point
    SHARED_FOUNDATION = "shared_foundation"  # Common across pathways
    BRIDGE_CONNECTOR = "bridge_connector"  # Adds AI focus to strong existing intro


class AIFStrategy(str, Enum):
    """Strategy for positioning AI Foundations."""

    POSITION_NEW = "position_new"  # Position as new entry course
    ALIGN_EXISTING = "align_existing"  # Align existing course with AIF content
    HYBRID = "hybrid"  # Both - align existing + clarify with AIF branding


class SourceType(str, Enum):
    """Type of source document."""

    PDF = "pdf"
    HTML = "html"
    DOCUMENT = "document"


class PipelineStatus(str, Enum):
    """Status of the analysis pipeline."""

    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class TagConfidence(str, Enum):
    """Confidence level for domain tagging."""

    HIGH = "High"  # Explicit in title
    MEDIUM = "Medium"  # Strongly implied by description
    LOW = "Low"  # Weak signal, unclear domain


class CoveragePattern(str, Enum):
    """Pattern of domain coverage."""

    BALANCED = "balanced"  # 5+ domains with reasonable distribution
    SKEWED = "skewed"  # 3-4 domains, one dominates
    NARROW = "narrow"  # 1-2 domains only


class EntryTiming(str, Enum):
    """Timing pattern for entry courses."""

    EARLY_BROAD = "early_broad"  # Grade 9-10, exploratory across domains
    EARLY_NARROW = "early_narrow"  # Grade 9-10, but immediately specialized
    LATE_BROAD = "late_broad"  # Grade 11-12, exploratory
    LATE_NARROW = "late_narrow"  # Grade 11-12, specialized


class SpecializationPattern(str, Enum):
    """Pattern of course specialization."""

    PREMATURE = "premature"  # Students specialize before understanding breadth
    BALANCED = "balanced"  # Exploration → informed choice → specialization
    DELAYED = "delayed"  # Extended exploration without clear progression
    EXTENDED_EXPLORATION = "extended_exploration"  # Broad but weak progression


class PathwayCoherence(str, Enum):
    """Coherence of pathway structure."""

    COHERENT_SYSTEM = "coherent_system"  # Clear progression, logical dependencies
    LOOSELY_CONNECTED = "loosely_connected"  # Courses exist but connections unclear
    PARALLEL_SILOS = "parallel_silos"  # Separate tracks with no crossover
    PATCHWORK = "patchwork"  # Courses added over time without design


class ChoiceArchitecture(str, Enum):
    """Pattern of student choice architecture."""

    CLEAR_INFORMED = "clear_informed"  # Students understand options before choosing
    HIGH_COGNITIVE_LOAD = "high_cognitive_load"  # Too many options, unclear differences
    EARLY_LOCK_IN = "early_lock_in"  # Choice at entry, hard to change
    DEFERRED_CHOICE = "deferred_choice"  # Choice delayed until after exploration


class AIIntegration(str, Enum):
    """Level of AI integration in curriculum."""

    AI_AS_TOPIC = "ai_as_topic"  # AI mentioned in units but not central
    AI_AS_LENS = "ai_as_lens"  # AI used to frame digital literacy
    AI_ABSENT = "ai_absent"  # No AI content in entry experience
    AI_ADVANCED_ONLY = "ai_advanced_only"  # AI only in specialized courses


class DownstreamRelationship(str, Enum):
    """Relationship to downstream pathways."""

    RECOMMENDED_PRECURSOR = "recommended_precursor"  # Explicitly feeds this pathway
    CONTEXTUAL_FOUNDATION = "contextual_foundation"  # Provides useful background
    NOT_CONNECTED = "not_connected"  # No clear relationship


# =============================================================================
# INPUT MODELS
# =============================================================================


class DistrictInput(BaseModel):
    """Input specification for district analysis."""

    district_name: str = Field(..., description="Name of the school district")
    state: str = Field(..., description="State name or abbreviation")
    user_provided_urls: List[str] = Field(
        default_factory=list, description="Optional manual URLs to analyze"
    )


# =============================================================================
# SOURCE AND DISCOVERY MODELS
# =============================================================================


class Source(BaseModel):
    """A discovered source document."""

    url: str
    source_type: SourceType
    confidence: float = Field(ge=0.0, le=1.0)
    date_accessed: str
    is_valid: bool = True
    validation_reason: Optional[str] = None


class SourceValidation(BaseModel):
    """Validation result for a source."""

    valid: bool
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str


class RawCourseData(BaseModel):
    """Raw extracted course data from a source."""

    titles: List[str] = Field(default_factory=list)
    descriptions: Dict[str, str] = Field(default_factory=dict)  # title -> description
    course_codes: Dict[str, str] = Field(default_factory=dict)  # title -> code
    grade_levels: Dict[str, str] = Field(default_factory=dict)  # title -> grade
    credit_types: Dict[str, str] = Field(default_factory=dict)  # title -> credit
    source_url: str
    extraction_confidence: float = Field(ge=0.0, le=1.0)


# =============================================================================
# COURSE INVENTORY MODELS
# =============================================================================


class DomainTags(BaseModel):
    """Domain tagging for a course."""

    primary: str
    secondary: List[str] = Field(default_factory=list)
    confidence: TagConfidence = TagConfidence.MEDIUM
    reasoning: str = ""


class CourseInventoryItem(BaseModel):
    """A course in the district inventory."""

    # Required fields (hard gate)
    title: str
    source_url: str
    offering_schools: List[str] = Field(default_factory=list)
    domain_tags: Optional[DomainTags] = None
    confidence: ConfidenceLevel = ConfidenceLevel.INFERRED

    # Optional fields (soft requirements)
    course_code: Optional[str] = None
    description: Optional[str] = None
    credit_type: Optional[str] = None
    grade_band: Optional[str] = None
    program_of_study: Optional[str] = None

    # Analysis fields (added during processing)
    role: Optional[CourseRole] = None
    role_confidence: Optional[TagConfidence] = None
    role_reasoning: Optional[str] = None

    # Flags
    is_alignment_candidate: bool = False
    alignment_candidate_reason: Optional[str] = None


class CourseInventory(BaseModel):
    """Complete course inventory for a district."""

    courses: List[CourseInventoryItem] = Field(default_factory=list)
    sources: List[Source] = Field(default_factory=list)
    discovery_date: str = Field(default_factory=lambda: datetime.now().isoformat())

    @property
    def course_count(self) -> int:
        return len(self.courses)

    @property
    def verified_count(self) -> int:
        return len([c for c in self.courses if c.confidence == ConfidenceLevel.VERIFIED])

    @property
    def verified_percentage(self) -> float:
        if not self.courses:
            return 0.0
        return self.verified_count / self.course_count


# =============================================================================
# DOMAIN COVERAGE MODELS
# =============================================================================


class DomainCoverage(BaseModel):
    """Analysis of domain coverage."""

    domains_present: Dict[str, int] = Field(default_factory=dict)  # domain -> count
    coverage_pattern: CoveragePattern = CoveragePattern.NARROW
    gaps: List[str] = Field(default_factory=list)
    dominant_domain: Optional[str] = None
    total_courses: int = 0


# =============================================================================
# LANDSCAPE MODELS (LAYER 1)
# =============================================================================


class EntryPointAnalysis(BaseModel):
    """Analysis of the district's entry point structure."""

    current_entry_course: Optional[str] = None
    entry_timing: str = "unclear"  # "early" | "late" | "unclear"
    entry_breadth: str = "fragmented"  # "broad" | "narrow" | "fragmented"
    grade_band: str = "unknown"  # "8" | "9-10" | "11-12"
    is_intentional: bool = False
    reasoning: str = ""


class DistrictLandscape(BaseModel):
    """Complete landscape model for a district (Layer 1 output)."""

    district_name: str
    state: str
    course_inventory: List[CourseInventoryItem] = Field(default_factory=list)
    domain_coverage: DomainCoverage = Field(default_factory=DomainCoverage)
    pathway_shape: PathwayShape = PathwayShape.MISSING_ENTRY
    entry_point_analysis: EntryPointAnalysis = Field(default_factory=EntryPointAnalysis)
    landscape_summary: str = ""

    # Additional structural details
    pathway_count: int = 0
    identified_pathways: List[str] = Field(default_factory=list)


# =============================================================================
# ALIGNMENT MODELS (LAYER 2)
# =============================================================================


class AlignmentProfile(BaseModel):
    """Alignment analysis dimensions."""

    entry_timing: EntryTiming = EntryTiming.LATE_NARROW
    specialization_pattern: SpecializationPattern = SpecializationPattern.PREMATURE
    domain_balance: CoveragePattern = CoveragePattern.NARROW
    pathway_coherence: PathwayCoherence = PathwayCoherence.PATCHWORK
    choice_architecture: ChoiceArchitecture = ChoiceArchitecture.HIGH_COGNITIVE_LOAD
    ai_integration: AIIntegration = AIIntegration.AI_ABSENT


class OpportunitySignals(BaseModel):
    """Identified opportunities and risks."""

    opportunities: List[str] = Field(default_factory=list)
    risk_flags: List[str] = Field(default_factory=list)


class AlignmentReport(BaseModel):
    """Complete alignment analysis (Layer 2 output)."""

    alignment_profile: AlignmentProfile = Field(default_factory=AlignmentProfile)
    alignment_narrative: str = ""
    opportunity_signals: OpportunitySignals = Field(default_factory=OpportunitySignals)


# =============================================================================
# PATHWAY DESIGN MODELS (LAYER 3)
# =============================================================================


class DesignVariables(BaseModel):
    """District-sensitive design variables."""

    grade_band: str = "9-10"  # "8" | "9-10" | "10"
    credit_framing: str = "CTE"  # "CTE" | "hybrid" | "elective"
    entry_strength: str = "default"  # "required" | "default" | "recommended"
    narrative_emphasis: str = "access"  # "access" | "coherence" | "connection"
    downstream_branching: str = "explicit"  # "explicit" | "implied"


class DownstreamPath(BaseModel):
    """Mapping to a downstream pathway."""

    name: str
    courses: List[str] = Field(default_factory=list)
    relationship: DownstreamRelationship = DownstreamRelationship.CONTEXTUAL_FOUNDATION
    reasoning: str = ""


class DesignInvariants(BaseModel):
    """Non-negotiable design constraints."""

    aif_is_entry: bool = True  # AI Foundations is an entry experience, not specialization
    downstream_intact: bool = True  # Existing downstream pathways remain intact
    reduces_cognitive_load: bool = True  # Design reduces cognitive load for students
    aligns_cross_cutting: bool = True  # Aligns with Digital Tech as cross-cutting
    two_minute_explainable: bool = True  # Can be explained without jargon

    def all_satisfied(self) -> bool:
        """Check if all invariants are satisfied."""
        return all(
            [
                self.aif_is_entry,
                self.downstream_intact,
                self.reduces_cognitive_load,
                self.aligns_cross_cutting,
                self.two_minute_explainable,
            ]
        )

    def violations(self) -> List[str]:
        """Return list of violated invariants."""
        violations = []
        if not self.aif_is_entry:
            violations.append("AI Foundations must be an entry experience, not a specialization")
        if not self.downstream_intact:
            violations.append("Existing downstream pathways must remain intact")
        if not self.reduces_cognitive_load:
            violations.append("Design must reduce cognitive load for students")
        if not self.aligns_cross_cutting:
            violations.append("Design must align with Digital Technology as cross-cutting")
        if not self.two_minute_explainable:
            violations.append("Design must be explainable in 2 minutes without jargon")
        return violations


class PathwayDesign(BaseModel):
    """Complete pathway design (Layer 3 output)."""

    # Design decision
    strategy: AIFStrategy = AIFStrategy.POSITION_NEW

    # If align_existing
    existing_course_to_align: Optional[str] = None

    # AI Foundations placement
    aif_role: AIFoundationsRole = AIFoundationsRole.PRIMARY_ENTRY
    design_variables: DesignVariables = Field(default_factory=DesignVariables)

    # Downstream pathway mapping
    downstream_pathways: List[DownstreamPath] = Field(default_factory=list)

    # Design narrative (3-4 sentences)
    design_narrative: str = ""

    # Confidence & caveats
    design_confidence: str = "medium"  # "high" | "medium" | "low"
    assumptions: List[str] = Field(default_factory=list)
    validation_needed: List[str] = Field(default_factory=list)

    # Invariant checking
    invariants: DesignInvariants = Field(default_factory=DesignInvariants)


# =============================================================================
# DISCOVERY GATE MODELS
# =============================================================================


class DiscoveryGateResult(BaseModel):
    """Result of the discovery gate check."""

    passed: bool = False
    reason: str = ""
    courses_found: int = 0
    verified_percentage: float = 0.0
    domains_covered: List[str] = Field(default_factory=list)
    issues: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


# =============================================================================
# COMPLETE ANALYSIS REPORT
# =============================================================================


class DistrictAnalysisReport(BaseModel):
    """Complete analysis output."""

    district_name: str
    state: str
    generated_date: str = Field(default_factory=lambda: datetime.now().isoformat())

    # Pipeline inputs
    input_data: DistrictInput

    # Discovery results
    sources: List[Source] = Field(default_factory=list)
    discovery_gate: DiscoveryGateResult = Field(default_factory=DiscoveryGateResult)

    # Analysis layers
    landscape: Optional[DistrictLandscape] = None
    alignment: Optional[AlignmentReport] = None
    design: Optional[PathwayDesign] = None

    # Pipeline status
    pipeline_status: PipelineStatus = PipelineStatus.FAILED
    current_phase: str = "discovery"
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)

    def to_summary(self) -> Dict[str, Any]:
        """Generate a summary of the analysis."""
        return {
            "district": f"{self.district_name}, {self.state}",
            "status": self.pipeline_status.value,
            "courses_found": len(self.landscape.course_inventory) if self.landscape else 0,
            "strategy": self.design.strategy.value if self.design else None,
            "confidence": self.design.design_confidence if self.design else None,
            "warnings": len(self.warnings),
            "errors": len(self.errors),
        }


# =============================================================================
# ERROR CLASSES
# =============================================================================


class AnalysisError(Exception):
    """Base class for analysis errors."""

    pass


class DiscoveryFailure(AnalysisError):
    """Cannot find or extract course data."""

    pass


class InsufficientData(AnalysisError):
    """Data found but too incomplete to analyze."""

    pass


class ConflictingSignals(AnalysisError):
    """Analysis produced contradictory results."""

    pass


class InvariantViolation(AnalysisError):
    """Design would violate a design invariant."""

    pass
