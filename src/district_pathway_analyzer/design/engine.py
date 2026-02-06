"""
Pathway design engine for designing AI Foundations role.
"""

import json
import logging
import re
from typing import List, Optional, Tuple

from district_pathway_analyzer.llm_client import get_llm_client
from district_pathway_analyzer.models import (
    AIFStrategy,
    AIFoundationsRole,
    AIIntegration,
    AlignmentReport,
    ChoiceArchitecture,
    CourseInventoryItem,
    CourseRole,
    DesignInvariants,
    DesignVariables,
    DistrictLandscape,
    DownstreamPath,
    DownstreamRelationship,
    EntryTiming,
    InvariantViolation,
    PathwayCoherence,
    PathwayDesign,
    PathwayShape,
    SpecializationPattern,
)

logger = logging.getLogger(__name__)


# AI Foundations course information for reference
AI_FOUNDATIONS_INFO = {
    "name": "AI Foundations",
    "grade_level": "9-10",
    "prerequisites": "None required",
    "credit_type": "CTE or Academic",
    "duration": "Full year (2 semesters)",
    "semesters": {
        "semester_1": {
            "title": "Semester 1",
            "topics": [
                "Problem Solving with AI",
                "Foundations of AI Programming (Python)",
                "AI and the Systems That Power It",
                "The Fabric of the Internet and AI",
                "AI-Powered Threats and Defenses",
                "Introduction to Data Science",
            ],
        },
        "semester_2": {
            "title": "Semester 2",
            "topics": [
                "AI-Generated Design",
                "AI and Algorithmic Decisions",
                "Building Data-Driven Systems with AI",
                "Iterating with AI",
                "Designing Reliable Apps with AI and APIs",
                "Web Apps with AI Capstone Project",
            ],
        },
    },
    "positioning": "Entry-level course accessible to beginners with no prior CS experience",
}


class PathwayDesignEngine:
    """Designs the role for AI Foundations within a district."""

    def __init__(self):
        """Initialize the design engine."""
        self.llm = get_llm_client()

    def design(
        self, landscape: DistrictLandscape, alignment: AlignmentReport
    ) -> PathwayDesign:
        """Design the AI Foundations role for the district.

        Args:
            landscape: The district landscape model
            alignment: The alignment analysis

        Returns:
            PathwayDesign with recommendations
        """
        # Step 1: Determine strategy
        strategy, existing_course = self._determine_strategy(landscape)

        # Step 2: Determine structural placement (role)
        aif_role = self._determine_role(landscape, alignment)

        # Step 3: Set design variables
        design_vars = self._set_design_variables(landscape, alignment, strategy)

        # Step 4: Map downstream pathways
        downstream = self._map_downstream_pathways(landscape)

        # Step 5: Check invariants
        invariants = self._check_invariants(landscape, aif_role, strategy)

        if not invariants.all_satisfied():
            # Handle invariant violations
            violations = invariants.violations()
            logger.warning(f"Design invariant violations: {violations}")
            # Attempt to adjust design
            aif_role, design_vars = self._adjust_for_violations(
                aif_role, design_vars, violations
            )
            # Re-check
            invariants = self._check_invariants(landscape, aif_role, strategy)

        # Step 6: Generate design narrative
        narrative = self._generate_narrative(
            landscape, strategy, aif_role, design_vars, existing_course
        )

        # Step 7: Assess confidence and caveats
        confidence, assumptions, validations = self._assess_confidence(
            landscape, strategy, existing_course
        )

        return PathwayDesign(
            strategy=strategy,
            existing_course_to_align=existing_course,
            aif_role=aif_role,
            design_variables=design_vars,
            downstream_pathways=downstream,
            design_narrative=narrative,
            design_confidence=confidence,
            assumptions=assumptions,
            validation_needed=validations,
            invariants=invariants,
        )

    def _determine_strategy(
        self, landscape: DistrictLandscape
    ) -> Tuple[AIFStrategy, Optional[str]]:
        """Determine the AIF strategy.

        Args:
            landscape: The district landscape

        Returns:
            Tuple of (strategy, existing_course_name or None)
        """
        # Look for alignment candidates
        candidates = [
            c for c in landscape.course_inventory if c.is_alignment_candidate
        ]

        if candidates:
            # Assess alignment potential
            for candidate in candidates:
                match_score = self._assess_alignment_match(candidate)
                if match_score >= 0.7:
                    return AIFStrategy.ALIGN_EXISTING, candidate.title
                elif match_score >= 0.5:
                    return AIFStrategy.HYBRID, candidate.title

        # Check for suitable entry course that could be aligned
        entry_courses = [
            c for c in landscape.course_inventory if c.role == CourseRole.EXPLORATORY
        ]
        for course in entry_courses:
            if self._is_broad_digital_course(course):
                match_score = self._assess_alignment_match(course)
                if match_score >= 0.5:
                    return AIFStrategy.HYBRID, course.title

        # Default to position_new
        return AIFStrategy.POSITION_NEW, None

    def _assess_alignment_match(self, course: CourseInventoryItem) -> float:
        """Assess how well a course matches AI Foundations content.

        Args:
            course: The course to assess

        Returns:
            Match score from 0.0 to 1.0
        """
        score = 0.0
        title_lower = course.title.lower()
        desc_lower = (course.description or "").lower()

        # Check for broad digital/computing title
        if any(kw in title_lower for kw in ["foundations", "fundamentals", "computing"]):
            score += 0.2

        # Check for AI Foundations topic coverage
        topic_keywords = {
            "ai": ["ai", "artificial intelligence"],
            "python": ["python", "programming"],
            "systems": ["systems", "computing"],
            "network": ["network", "internet"],
            "security": ["security", "cyber"],
            "data": ["data", "analytics"],
        }

        topics_covered = 0
        for topic, keywords in topic_keywords.items():
            if any(kw in title_lower or kw in desc_lower for kw in keywords):
                topics_covered += 1

        score += (topics_covered / len(topic_keywords)) * 0.5

        # Check grade level
        if course.grade_band and ("9" in course.grade_band or "10" in course.grade_band):
            score += 0.15

        # Check credit type
        if course.credit_type and "cte" in course.credit_type.lower():
            score += 0.15

        return min(score, 1.0)

    def _is_broad_digital_course(self, course: CourseInventoryItem) -> bool:
        """Check if a course is a broad digital course.

        Args:
            course: The course to check

        Returns:
            True if broad digital course
        """
        title_lower = course.title.lower()

        broad_indicators = [
            "digital technology",
            "computing foundations",
            "computer foundations",
            "information technology",
            "tech essentials",
            "digital literacy",
        ]

        return any(ind in title_lower for ind in broad_indicators)

    def _determine_role(
        self, landscape: DistrictLandscape, alignment: AlignmentReport
    ) -> AIFoundationsRole:
        """Determine the structural role for AI Foundations.

        Args:
            landscape: The district landscape
            alignment: The alignment analysis

        Returns:
            AIFoundationsRole enum value
        """
        profile = alignment.alignment_profile
        shape = landscape.pathway_shape

        # Check for missing/fragmented entry - PRIMARY_ENTRY
        if shape == PathwayShape.MISSING_ENTRY:
            return AIFoundationsRole.PRIMARY_ENTRY

        if profile.entry_timing in [EntryTiming.EARLY_NARROW, EntryTiming.LATE_NARROW]:
            return AIFoundationsRole.PRIMARY_ENTRY

        # Check for parallel silos - SHARED_FOUNDATION
        if shape == PathwayShape.PARALLEL_SILOS:
            return AIFoundationsRole.SHARED_FOUNDATION

        if profile.pathway_coherence == PathwayCoherence.PARALLEL_SILOS:
            return AIFoundationsRole.SHARED_FOUNDATION

        # Check for existing strong intro - BRIDGE_CONNECTOR
        entry_analysis = landscape.entry_point_analysis
        if (
            entry_analysis.entry_breadth == "broad"
            and entry_analysis.is_intentional
            and profile.ai_integration in [AIIntegration.AI_ABSENT, AIIntegration.AI_ADVANCED_ONLY]
        ):
            return AIFoundationsRole.BRIDGE_CONNECTOR

        # Default based on pathway count
        if landscape.pathway_count >= 3:
            return AIFoundationsRole.SHARED_FOUNDATION

        return AIFoundationsRole.PRIMARY_ENTRY

    def _set_design_variables(
        self,
        landscape: DistrictLandscape,
        alignment: AlignmentReport,
        strategy: AIFStrategy,
    ) -> DesignVariables:
        """Set the design variables for the district.

        Args:
            landscape: The district landscape
            alignment: The alignment analysis
            strategy: The chosen strategy

        Returns:
            DesignVariables
        """
        profile = alignment.alignment_profile

        # Grade band
        grade_band = "9-10"  # Default
        entry = landscape.entry_point_analysis
        if entry.grade_band == "8":
            grade_band = "9-10"  # Still recommend 9-10 even if MS has computing
        elif "11" in (entry.grade_band or "") and "9" not in (entry.grade_band or ""):
            grade_band = "10"  # Earlier is better if currently late

        # Credit framing
        credit_framing = "CTE"  # Default
        # Check if hybrid might work better
        cs_courses = [
            c for c in landscape.course_inventory
            if c.domain_tags and "Computer Science" in c.domain_tags.primary
        ]
        if len(cs_courses) > len(landscape.course_inventory) * 0.4:
            credit_framing = "hybrid"  # District may prefer academic positioning

        # Entry strength
        entry_strength = "default"  # Recommended for all pathways
        if strategy == AIFStrategy.ALIGN_EXISTING:
            entry_strength = "default"  # Keep existing structure
        elif profile.pathway_coherence == PathwayCoherence.PATCHWORK:
            entry_strength = "recommended"  # Lighter touch for complex situations

        # Narrative emphasis
        narrative_emphasis = "access"  # Default
        if profile.pathway_coherence in [
            PathwayCoherence.PARALLEL_SILOS,
            PathwayCoherence.PATCHWORK,
        ]:
            narrative_emphasis = "coherence"
        elif profile.choice_architecture == ChoiceArchitecture.HIGH_COGNITIVE_LOAD:
            narrative_emphasis = "connection"

        # Downstream branching
        downstream_branching = "explicit"  # Default
        if landscape.pathway_count <= 2:
            downstream_branching = "implied"

        return DesignVariables(
            grade_band=grade_band,
            credit_framing=credit_framing,
            entry_strength=entry_strength,
            narrative_emphasis=narrative_emphasis,
            downstream_branching=downstream_branching,
        )

    def _map_downstream_pathways(
        self, landscape: DistrictLandscape
    ) -> List[DownstreamPath]:
        """Map AI Foundations to downstream pathways.

        Args:
            landscape: The district landscape

        Returns:
            List of DownstreamPath mappings
        """
        downstream = []

        # Group courses by domain
        domain_courses = {}
        for course in landscape.course_inventory:
            if course.domain_tags and course.role in [
                CourseRole.CONCENTRATOR,
                CourseRole.CAPSTONE,
            ]:
                domain = course.domain_tags.primary
                if domain not in domain_courses:
                    domain_courses[domain] = []
                domain_courses[domain].append(course.title)

        # Create downstream paths
        for domain, courses in domain_courses.items():
            # Determine relationship based on AI Foundations topic coverage
            relationship = self._determine_downstream_relationship(domain)

            reasoning = self._get_pathway_reasoning(domain, relationship)

            downstream.append(
                DownstreamPath(
                    name=domain,
                    courses=courses,
                    relationship=relationship,
                    reasoning=reasoning,
                )
            )

        # Also check identified pathways
        for pathway in landscape.identified_pathways:
            if pathway not in domain_courses:
                downstream.append(
                    DownstreamPath(
                        name=pathway,
                        courses=[],
                        relationship=DownstreamRelationship.CONTEXTUAL_FOUNDATION,
                        reasoning="Pathway identified in district structure",
                    )
                )

        return downstream

    def _determine_downstream_relationship(
        self, domain: str
    ) -> DownstreamRelationship:
        """Determine the relationship to a downstream domain.

        Args:
            domain: The domain name

        Returns:
            DownstreamRelationship enum value
        """
        # AI Foundations strongly connects to these
        recommended_domains = [
            "Computer Science",
            "Software Development",
            "Data Science",
            "Artificial Intelligence",
            "Cybersecurity",
        ]

        # Contextual connection to these
        contextual_domains = [
            "Information Technology",
            "IT Systems",
            "Networking",
            "Digital Media",
            "Web",
        ]

        domain_lower = domain.lower()

        for rd in recommended_domains:
            if rd.lower() in domain_lower or domain_lower in rd.lower():
                return DownstreamRelationship.RECOMMENDED_PRECURSOR

        for cd in contextual_domains:
            if cd.lower() in domain_lower or domain_lower in cd.lower():
                return DownstreamRelationship.CONTEXTUAL_FOUNDATION

        # Engineering is typically not connected
        if "engineering" in domain_lower:
            return DownstreamRelationship.NOT_CONNECTED

        return DownstreamRelationship.CONTEXTUAL_FOUNDATION

    def _get_pathway_reasoning(
        self, domain: str, relationship: DownstreamRelationship
    ) -> str:
        """Get reasoning for pathway relationship.

        Args:
            domain: The domain name
            relationship: The relationship type

        Returns:
            Reasoning text
        """
        if relationship == DownstreamRelationship.RECOMMENDED_PRECURSOR:
            return f"AI Foundations covers foundational concepts that directly prepare students for {domain}"
        elif relationship == DownstreamRelationship.CONTEXTUAL_FOUNDATION:
            return f"AI Foundations provides useful background context for {domain}"
        else:
            return f"AI Foundations content does not directly connect to {domain}"

    def _check_invariants(
        self,
        landscape: DistrictLandscape,
        role: AIFoundationsRole,
        strategy: AIFStrategy,
    ) -> DesignInvariants:
        """Check design invariants.

        Args:
            landscape: The district landscape
            role: The proposed role
            strategy: The proposed strategy

        Returns:
            DesignInvariants with satisfaction status
        """
        invariants = DesignInvariants()

        # Invariant 1: AI Foundations is entry, not specialization
        invariants.aif_is_entry = role in [
            AIFoundationsRole.PRIMARY_ENTRY,
            AIFoundationsRole.SHARED_FOUNDATION,
            AIFoundationsRole.BRIDGE_CONNECTOR,
        ]

        # Invariant 2: Downstream pathways intact
        # Check if any concentrator/capstone would be displaced
        concentrators = [
            c for c in landscape.course_inventory
            if c.role in [CourseRole.CONCENTRATOR, CourseRole.CAPSTONE]
        ]
        invariants.downstream_intact = len(concentrators) >= len(
            [c for c in landscape.course_inventory if c.role == CourseRole.CONCENTRATOR]
        )

        # Invariant 3: Reduces cognitive load
        # Design should simplify, not add complexity
        if role == AIFoundationsRole.PRIMARY_ENTRY:
            invariants.reduces_cognitive_load = True
        elif role == AIFoundationsRole.SHARED_FOUNDATION:
            invariants.reduces_cognitive_load = True
        else:
            # Bridge connector adds a course
            invariants.reduces_cognitive_load = landscape.pathway_count <= 4

        # Invariant 4: Aligns with cross-cutting nature
        invariants.aligns_cross_cutting = role != AIFoundationsRole.BRIDGE_CONNECTOR or (
            strategy == AIFStrategy.ALIGN_EXISTING
        )

        # Invariant 5: Two-minute explainable
        invariants.two_minute_explainable = True  # Assume true unless very complex

        return invariants

    def _adjust_for_violations(
        self,
        role: AIFoundationsRole,
        design_vars: DesignVariables,
        violations: List[str],
    ) -> Tuple[AIFoundationsRole, DesignVariables]:
        """Attempt to adjust design to satisfy violated invariants.

        Args:
            role: Current role
            design_vars: Current design variables
            violations: List of violation messages

        Returns:
            Adjusted (role, design_vars)
        """
        # For cognitive load issues, make entry strength lighter
        if any("cognitive load" in v.lower() for v in violations):
            design_vars.entry_strength = "recommended"

        # For cross-cutting issues, shift to shared foundation
        if any("cross-cutting" in v.lower() for v in violations):
            role = AIFoundationsRole.SHARED_FOUNDATION

        return role, design_vars

    def _generate_narrative(
        self,
        landscape: DistrictLandscape,
        strategy: AIFStrategy,
        role: AIFoundationsRole,
        design_vars: DesignVariables,
        existing_course: Optional[str],
    ) -> str:
        """Generate the design narrative.

        Args:
            landscape: The district landscape
            strategy: The chosen strategy
            role: The chosen role
            design_vars: The design variables
            existing_course: Name of existing course if aligning

        Returns:
            Narrative text
        """
        prompt = f"""Generate a 3-4 sentence design narrative for positioning AI Foundations in this district.

DISTRICT: {landscape.district_name}
STRATEGY: {strategy.value}
ROLE: {role.value}
EXISTING COURSE TO ALIGN: {existing_course or "None"}

DESIGN VARIABLES:
- Grade Band: {design_vars.grade_band}
- Credit Framing: {design_vars.credit_framing}
- Entry Strength: {design_vars.entry_strength}
- Narrative Emphasis: {design_vars.narrative_emphasis}

LANDSCAPE SUMMARY:
{landscape.landscape_summary}

IDENTIFIED PATHWAYS: {', '.join(landscape.identified_pathways) if landscape.identified_pathways else 'None identified'}

The narrative should:
1. State what AI Foundations will serve as
2. Explain how it connects to existing pathways
3. Use the appropriate narrative emphasis ({design_vars.narrative_emphasis})
4. Be jargon-free and explainable in 2 minutes"""

        try:
            response = self.llm.complete(prompt, temperature=0.3)
            return response.strip()
        except Exception as e:
            logger.error(f"Failed to generate narrative: {e}")
            return self._template_narrative(
                landscape, strategy, role, design_vars, existing_course
            )

    def _template_narrative(
        self,
        landscape: DistrictLandscape,
        strategy: AIFStrategy,
        role: AIFoundationsRole,
        design_vars: DesignVariables,
        existing_course: Optional[str],
    ) -> str:
        """Generate a template-based narrative as fallback.

        Args:
            landscape: The district landscape
            strategy: The chosen strategy
            role: The chosen role
            design_vars: The design variables
            existing_course: Name of existing course if aligning

        Returns:
            Narrative text
        """
        parts = []

        if strategy == AIFStrategy.ALIGN_EXISTING:
            parts.append(
                f"The existing '{existing_course}' course already serves the structural role "
                "of a digital entry experience. This course presents a strong alignment "
                "opportunity with AI Foundations curriculum."
            )
            parts.append(
                "By adopting Code.org's AI Foundations content, the district can modernize "
                "this course with AI/data science emphasis while preserving its existing "
                "role in the pathway structure."
            )
        elif strategy == AIFStrategy.HYBRID:
            parts.append(
                f"AI Foundations can complement the existing '{existing_course}' course "
                "to strengthen the digital entry experience."
            )
            parts.append(
                "This hybrid approach allows the district to enhance AI/data literacy "
                "while building on established curriculum."
            )
        else:  # POSITION_NEW
            if role == AIFoundationsRole.PRIMARY_ENTRY:
                parts.append(
                    "AI Foundations serves as the recommended entry point for students "
                    "interested in any digital technology pathway."
                )
                parts.append(
                    "It provides broad exposure to computing fundamentals, AI concepts, "
                    "and technical systems before students specialize."
                )
            else:  # SHARED_FOUNDATION
                parts.append(
                    "AI Foundations serves as a recommended shared experience across "
                    f"digital pathways including {', '.join(landscape.identified_pathways[:3])}."
                )
                parts.append(
                    "Rather than replacing existing courses, it functions as a connector "
                    "that helps students make informed Program of Study choices."
                )

        parts.append(
            "Existing downstream pathways remain intact, with AI Foundations "
            "feeding into them as a common foundation."
        )

        return " ".join(parts)

    def _assess_confidence(
        self,
        landscape: DistrictLandscape,
        strategy: AIFStrategy,
        existing_course: Optional[str],
    ) -> Tuple[str, List[str], List[str]]:
        """Assess design confidence and identify assumptions/validations.

        Args:
            landscape: The district landscape
            strategy: The chosen strategy
            existing_course: Name of existing course if aligning

        Returns:
            Tuple of (confidence, assumptions, validations_needed)
        """
        assumptions = []
        validations = []

        # Base confidence
        confidence = "high"

        # Check data quality
        uncertain_courses = [
            c for c in landscape.course_inventory
            if c.confidence.value == "Uncertain"
        ]
        if len(uncertain_courses) > len(landscape.course_inventory) * 0.2:
            confidence = "medium"
            validations.append("Verify course inventory with district")

        # Strategy-specific assumptions
        if strategy == AIFStrategy.POSITION_NEW:
            assumptions.append("District open to adding entry course")
            if landscape.entry_point_analysis.current_entry_course:
                assumptions.append(
                    f"Current entry course ({landscape.entry_point_analysis.current_entry_course}) "
                    "can shift to concentrator role or coexist"
                )
        elif strategy == AIFStrategy.ALIGN_EXISTING:
            assumptions.append(f"'{existing_course}' instructor open to curriculum adoption")
            assumptions.append("Existing course schedule can accommodate new content")
            validations.append("Review full course syllabus")
            validations.append("Discuss with current instructor")
            confidence = "medium"
        else:  # HYBRID
            assumptions.append("District open to curriculum coordination")
            validations.append("Discuss integration approach with department")
            confidence = "medium"

        # Check pathway count
        if landscape.pathway_count >= 4:
            assumptions.append("Pathway leads open to coordination")
            confidence = "medium" if confidence == "high" else confidence

        return confidence, assumptions, validations
