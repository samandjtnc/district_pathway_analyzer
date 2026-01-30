"""
Alignment analysis for comparing district structure to Digital Technology cluster.
"""

import json
import logging
import re
from typing import List, Optional

from district_pathway_analyzer.llm_client import get_llm_client
from district_pathway_analyzer.models import (
    AIIntegration,
    AlignmentProfile,
    AlignmentReport,
    ChoiceArchitecture,
    CourseInventoryItem,
    CourseRole,
    CoveragePattern,
    DistrictLandscape,
    EntryTiming,
    OpportunitySignals,
    PathwayCoherence,
    PathwayShape,
    SpecializationPattern,
)

logger = logging.getLogger(__name__)


class AlignmentAnalyzer:
    """Analyzes alignment of district structure to Digital Technology cluster."""

    def __init__(self):
        """Initialize the analyzer."""
        self.llm = get_llm_client()

    def analyze(self, landscape: DistrictLandscape) -> AlignmentReport:
        """Analyze alignment of the district landscape.

        Args:
            landscape: The district landscape model

        Returns:
            AlignmentReport with analysis
        """
        # Build alignment profile
        profile = self._build_alignment_profile(landscape)

        # Identify opportunity signals
        opportunities = self._identify_opportunities(landscape, profile)

        # Generate alignment narrative
        narrative = self._generate_narrative(landscape, profile)

        return AlignmentReport(
            alignment_profile=profile,
            alignment_narrative=narrative,
            opportunity_signals=opportunities,
        )

    def _build_alignment_profile(
        self, landscape: DistrictLandscape
    ) -> AlignmentProfile:
        """Build the alignment profile from landscape data.

        Args:
            landscape: The district landscape

        Returns:
            AlignmentProfile
        """
        entry = landscape.entry_point_analysis

        # 1. Entry Timing
        entry_timing = self._assess_entry_timing(entry)

        # 2. Specialization Pattern
        specialization = self._assess_specialization(landscape)

        # 3. Domain Balance (from domain coverage)
        domain_balance = landscape.domain_coverage.coverage_pattern

        # 4. Pathway Coherence
        coherence = self._assess_coherence(landscape)

        # 5. Choice Architecture
        choice_arch = self._assess_choice_architecture(landscape)

        # 6. AI Integration
        ai_integration = self._assess_ai_integration(landscape.course_inventory)

        return AlignmentProfile(
            entry_timing=entry_timing,
            specialization_pattern=specialization,
            domain_balance=domain_balance,
            pathway_coherence=coherence,
            choice_architecture=choice_arch,
            ai_integration=ai_integration,
        )

    def _assess_entry_timing(self, entry: "EntryPointAnalysis") -> EntryTiming:
        """Assess entry timing alignment.

        Args:
            entry: Entry point analysis from landscape

        Returns:
            EntryTiming enum value
        """
        timing = entry.entry_timing
        breadth = entry.entry_breadth

        if timing == "early":
            if breadth == "broad":
                return EntryTiming.EARLY_BROAD
            else:
                return EntryTiming.EARLY_NARROW
        elif timing == "late":
            if breadth == "broad":
                return EntryTiming.LATE_BROAD
            else:
                return EntryTiming.LATE_NARROW
        else:
            # Unclear timing - check other signals
            if breadth == "narrow":
                return EntryTiming.EARLY_NARROW
            return EntryTiming.LATE_NARROW

    def _assess_specialization(
        self, landscape: DistrictLandscape
    ) -> SpecializationPattern:
        """Assess specialization pattern.

        Args:
            landscape: The district landscape

        Returns:
            SpecializationPattern enum value
        """
        courses = landscape.course_inventory
        entry = landscape.entry_point_analysis

        # Count course roles
        exploratory_count = len([c for c in courses if c.role == CourseRole.EXPLORATORY])
        concentrator_count = len([c for c in courses if c.role == CourseRole.CONCENTRATOR])

        # Check entry breadth
        if entry.entry_breadth == "narrow":
            # Narrow entry suggests premature specialization
            if exploratory_count <= 1:
                return SpecializationPattern.PREMATURE
        elif entry.entry_breadth == "broad":
            # Broad entry with good progression is balanced
            if concentrator_count > exploratory_count:
                return SpecializationPattern.BALANCED
            else:
                return SpecializationPattern.EXTENDED_EXPLORATION

        # Check pathway shape
        if landscape.pathway_shape == PathwayShape.FUNNEL:
            return SpecializationPattern.BALANCED
        elif landscape.pathway_shape == PathwayShape.PARALLEL_SILOS:
            return SpecializationPattern.PREMATURE
        elif landscape.pathway_shape == PathwayShape.LATE_ENTRY:
            return SpecializationPattern.DELAYED
        else:
            return SpecializationPattern.PREMATURE

    def _assess_coherence(self, landscape: DistrictLandscape) -> PathwayCoherence:
        """Assess pathway coherence.

        Args:
            landscape: The district landscape

        Returns:
            PathwayCoherence enum value
        """
        shape = landscape.pathway_shape

        if shape == PathwayShape.FUNNEL:
            # Check if progression is clear
            courses = landscape.course_inventory
            has_clear_sequence = self._has_clear_sequence(courses)
            if has_clear_sequence:
                return PathwayCoherence.COHERENT_SYSTEM
            else:
                return PathwayCoherence.LOOSELY_CONNECTED

        elif shape == PathwayShape.PARALLEL_SILOS:
            return PathwayCoherence.PARALLEL_SILOS

        elif shape == PathwayShape.LATE_ENTRY:
            return PathwayCoherence.LOOSELY_CONNECTED

        else:  # MISSING_ENTRY
            return PathwayCoherence.PATCHWORK

    def _has_clear_sequence(self, courses: List[CourseInventoryItem]) -> bool:
        """Check if courses have clear sequencing.

        Args:
            courses: List of courses

        Returns:
            True if clear sequence exists
        """
        # Check for numbered courses or explicit prerequisites
        has_levels = False
        for course in courses:
            title_lower = course.title.lower()
            # Look for level indicators
            if any(
                pattern in title_lower
                for pattern in [" i ", " ii ", " iii ", " 1 ", " 2 ", " 3 "]
            ):
                has_levels = True
                break

        return has_levels

    def _assess_choice_architecture(
        self, landscape: DistrictLandscape
    ) -> ChoiceArchitecture:
        """Assess the choice architecture for students.

        Args:
            landscape: The district landscape

        Returns:
            ChoiceArchitecture enum value
        """
        entry = landscape.entry_point_analysis
        courses = landscape.course_inventory

        # Count entry-level courses
        exploratory_count = len([c for c in courses if c.role == CourseRole.EXPLORATORY])

        if entry.entry_breadth == "broad" and entry.is_intentional:
            # Broad intentional entry suggests informed choice
            return ChoiceArchitecture.DEFERRED_CHOICE

        if exploratory_count > 3:
            # Too many options at entry
            return ChoiceArchitecture.HIGH_COGNITIVE_LOAD

        if entry.entry_breadth == "narrow" or entry.entry_breadth == "fragmented":
            # Early specialization locks students in
            return ChoiceArchitecture.EARLY_LOCK_IN

        if landscape.pathway_shape == PathwayShape.FUNNEL:
            return ChoiceArchitecture.CLEAR_INFORMED

        return ChoiceArchitecture.HIGH_COGNITIVE_LOAD

    def _assess_ai_integration(
        self, courses: List[CourseInventoryItem]
    ) -> AIIntegration:
        """Assess AI integration in the curriculum.

        Args:
            courses: List of courses

        Returns:
            AIIntegration enum value
        """
        ai_keywords = [
            "artificial intelligence",
            "ai",
            "machine learning",
            "data science",
            "neural",
        ]

        entry_has_ai = False
        advanced_has_ai = False

        for course in courses:
            title_lower = course.title.lower()
            desc_lower = (course.description or "").lower()

            has_ai = any(
                kw in title_lower or kw in desc_lower for kw in ai_keywords
            )

            if has_ai:
                if course.role == CourseRole.EXPLORATORY:
                    entry_has_ai = True
                elif course.role in [CourseRole.CONCENTRATOR, CourseRole.CAPSTONE]:
                    advanced_has_ai = True

        if entry_has_ai:
            return AIIntegration.AI_AS_LENS
        elif advanced_has_ai:
            return AIIntegration.AI_ADVANCED_ONLY
        else:
            return AIIntegration.AI_ABSENT

    def _identify_opportunities(
        self, landscape: DistrictLandscape, profile: AlignmentProfile
    ) -> OpportunitySignals:
        """Identify opportunity signals and risk flags.

        Args:
            landscape: The district landscape
            profile: The alignment profile

        Returns:
            OpportunitySignals
        """
        opportunities = []
        risks = []

        # Check entry timing
        if profile.entry_timing in [EntryTiming.EARLY_NARROW, EntryTiming.LATE_NARROW]:
            opportunities.append("Opportunity to clarify the digital entry experience")

        if profile.entry_timing in [EntryTiming.LATE_BROAD, EntryTiming.LATE_NARROW]:
            opportunities.append("Opportunity to establish earlier digital exploration")

        # Check specialization
        if profile.specialization_pattern == SpecializationPattern.PREMATURE:
            opportunities.append("Opportunity to broaden early exposure across domains")
            risks.append("Risk of over-prescription if entry role redefined")

        if profile.specialization_pattern == SpecializationPattern.EXTENDED_EXPLORATION:
            opportunities.append("Opportunity to strengthen pathway progression")

        # Check coherence
        if profile.pathway_coherence in [
            PathwayCoherence.PARALLEL_SILOS,
            PathwayCoherence.PATCHWORK,
        ]:
            opportunities.append("Opportunity to reduce fragmentation between pathways")

        # Check AI integration
        if profile.ai_integration == AIIntegration.AI_ABSENT:
            opportunities.append("Opportunity to make AI/data literacy explicit at entry")

        if profile.ai_integration == AIIntegration.AI_ADVANCED_ONLY:
            opportunities.append("Opportunity to introduce AI concepts earlier")

        # Check choice architecture
        if profile.choice_architecture == ChoiceArchitecture.HIGH_COGNITIVE_LOAD:
            opportunities.append("Opportunity to simplify student pathway choices")

        if profile.choice_architecture == ChoiceArchitecture.EARLY_LOCK_IN:
            opportunities.append("Opportunity to provide more exploratory options")

        # Risk flags based on district type
        if landscape.pathway_count >= 4:
            risks.append("Risk of threatening existing capstone courses")

        if profile.pathway_coherence == PathwayCoherence.COHERENT_SYSTEM:
            risks.append("Risk of narrative resistance in innovation-forward districts")

        # Check for alignment candidates
        alignment_candidates = [c for c in landscape.course_inventory if c.is_alignment_candidate]
        if alignment_candidates:
            course_names = ", ".join(c.title for c in alignment_candidates[:2])
            opportunities.append(
                f"Existing course(s) may be candidates for alignment: {course_names}"
            )

        return OpportunitySignals(opportunities=opportunities, risk_flags=risks)

    def _generate_narrative(
        self, landscape: DistrictLandscape, profile: AlignmentProfile
    ) -> str:
        """Generate the alignment narrative.

        Args:
            landscape: The district landscape
            profile: The alignment profile

        Returns:
            Narrative text
        """
        prompt = f"""Generate a 2-3 sentence alignment narrative for this district.
The narrative should diagnose structural gaps WITHOUT prescribing solutions.

DISTRICT: {landscape.district_name}

ALIGNMENT PROFILE:
- Entry Timing: {profile.entry_timing.value}
- Specialization Pattern: {profile.specialization_pattern.value}
- Domain Balance: {profile.domain_balance.value}
- Pathway Coherence: {profile.pathway_coherence.value}
- Choice Architecture: {profile.choice_architecture.value}
- AI Integration: {profile.ai_integration.value}

LANDSCAPE SUMMARY:
{landscape.landscape_summary}

Write a diagnostic narrative that:
1. Identifies the main structural pattern
2. Notes implications for students
3. Uses neutral language (not "problems" but "patterns")

Do NOT recommend AI Foundations or any specific solution."""

        try:
            response = self.llm.complete(prompt, temperature=0.3)
            return response.strip()
        except Exception as e:
            logger.error(f"Failed to generate narrative: {e}")
            return self._template_narrative(profile)

    def _template_narrative(self, profile: AlignmentProfile) -> str:
        """Generate a template-based narrative as fallback.

        Args:
            profile: The alignment profile

        Returns:
            Narrative text
        """
        parts = []

        # Entry timing
        if profile.entry_timing == EntryTiming.EARLY_BROAD:
            parts.append("Students encounter digital technology early through broad exploratory experiences.")
        elif profile.entry_timing == EntryTiming.EARLY_NARROW:
            parts.append(
                "Students encounter digital technology early, but primarily through narrow, "
                "tool-specific courses."
            )
        elif profile.entry_timing == EntryTiming.LATE_BROAD:
            parts.append(
                "Digital pathways begin later in the high school experience, limiting time "
                "for exploration and depth."
            )
        else:
            parts.append(
                "Students encounter digital technology late and through specialized courses."
            )

        # Pathway coherence
        if profile.pathway_coherence == PathwayCoherence.PARALLEL_SILOS:
            parts.append(
                "Multiple digital pathways exist but lack a shared foundation, creating "
                "early specialization pressure."
            )
        elif profile.pathway_coherence == PathwayCoherence.PATCHWORK:
            parts.append(
                "The structure implies students should know their specialization before "
                "understanding the field."
            )

        # Choice architecture
        if profile.choice_architecture == ChoiceArchitecture.HIGH_COGNITIVE_LOAD:
            parts.append("Students face high cognitive load during pathway selection.")

        return " ".join(parts)
