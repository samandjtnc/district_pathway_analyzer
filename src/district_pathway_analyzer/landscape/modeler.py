"""
Landscape modeling for understanding district structure.
"""

import json
import logging
import re
from typing import Dict, List, Optional, Set, Tuple

from district_pathway_analyzer.llm_client import get_llm_client
from district_pathway_analyzer.models import (
    CourseInventoryItem,
    CourseRole,
    DigitalDomain,
    DistrictLandscape,
    DomainCoverage,
    EntryPointAnalysis,
    PathwayShape,
    TagConfidence,
)

logger = logging.getLogger(__name__)


# Keywords for role inference
EXPLORATORY_KEYWORDS = [
    "intro",
    "introduction",
    "foundations",
    "fundamentals",
    "essentials",
    "basics",
    "principles",
    "exploring",
    "discovery",
    "survey",
]

CAPSTONE_KEYWORDS = [
    "capstone",
    "practicum",
    "internship",
    "work-based",
    "senior",
    "advanced project",
    "portfolio",
]

CONCENTRATOR_KEYWORDS = [
    "advanced",
    "honors",
    "ap ",
    "ib ",
    "specialized",
    "certification",
]


class LandscapeModeler:
    """Models the landscape of a district's digital CTE structure."""

    def __init__(self):
        """Initialize the modeler."""
        self.llm = get_llm_client()

    def model_landscape(
        self,
        district_name: str,
        state: str,
        courses: List[CourseInventoryItem],
        domain_coverage: DomainCoverage,
    ) -> DistrictLandscape:
        """Build a landscape model for the district.

        Args:
            district_name: Name of the district
            state: State
            courses: List of tagged courses
            domain_coverage: Domain coverage analysis

        Returns:
            DistrictLandscape model
        """
        # Step 1: Infer course roles
        courses_with_roles = self._infer_roles(courses)

        # Step 2: Analyze pathway shape
        pathway_shape = self._analyze_pathway_shape(courses_with_roles)

        # Step 3: Analyze entry point
        entry_analysis = self._analyze_entry_point(courses_with_roles)

        # Step 4: Identify pathways
        pathways = self._identify_pathways(courses_with_roles)

        # Step 5: Generate landscape summary
        summary = self._generate_summary(
            district_name,
            courses_with_roles,
            domain_coverage,
            pathway_shape,
            entry_analysis,
        )

        return DistrictLandscape(
            district_name=district_name,
            state=state,
            course_inventory=courses_with_roles,
            domain_coverage=domain_coverage,
            pathway_shape=pathway_shape,
            entry_point_analysis=entry_analysis,
            landscape_summary=summary,
            pathway_count=len(pathways),
            identified_pathways=pathways,
        )

    def _infer_roles(
        self, courses: List[CourseInventoryItem]
    ) -> List[CourseInventoryItem]:
        """Infer the role of each course in the pathway.

        Args:
            courses: List of courses

        Returns:
            Courses with role assignments
        """
        for course in courses:
            role, confidence, reasoning = self._infer_single_role(course, courses)
            course.role = role
            course.role_confidence = confidence
            course.role_reasoning = reasoning

        return courses

    def _infer_single_role(
        self, course: CourseInventoryItem, all_courses: List[CourseInventoryItem]
    ) -> Tuple[CourseRole, TagConfidence, str]:
        """Infer the role for a single course.

        Args:
            course: The course to analyze
            all_courses: All courses for context

        Returns:
            Tuple of (role, confidence, reasoning)
        """
        title_lower = course.title.lower()
        desc_lower = (course.description or "").lower()

        # Check for capstone keywords
        if any(kw in title_lower for kw in CAPSTONE_KEYWORDS):
            return (
                CourseRole.CAPSTONE,
                TagConfidence.HIGH,
                "Title contains capstone/practicum keyword",
            )

        # Check for exploratory keywords
        if any(kw in title_lower for kw in EXPLORATORY_KEYWORDS):
            return (
                CourseRole.EXPLORATORY,
                TagConfidence.HIGH,
                "Title contains exploratory/foundations keyword",
            )

        # Check for concentrator keywords
        if any(kw in title_lower for kw in CONCENTRATOR_KEYWORDS):
            return (
                CourseRole.CONCENTRATOR,
                TagConfidence.HIGH,
                "Title contains advanced/specialized keyword",
            )

        # Check grade band if available
        grade = course.grade_band or ""
        if "9" in grade and "10" in grade and "11" not in grade and "12" not in grade:
            return (
                CourseRole.EXPLORATORY,
                TagConfidence.MEDIUM,
                "Grade band suggests early entry (9-10)",
            )
        elif "11" in grade or "12" in grade:
            if "9" not in grade and "10" not in grade:
                return (
                    CourseRole.CONCENTRATOR,
                    TagConfidence.MEDIUM,
                    "Grade band suggests upper-level course (11-12)",
                )

        # Check course numbering patterns
        if self._has_level_indicator(title_lower, 1):
            return (
                CourseRole.EXPLORATORY,
                TagConfidence.MEDIUM,
                "Course appears to be level 1 in sequence",
            )
        elif self._has_level_indicator(title_lower, 3) or self._has_level_indicator(
            title_lower, 4
        ):
            return (
                CourseRole.CONCENTRATOR,
                TagConfidence.MEDIUM,
                "Course appears to be level 3+ in sequence",
            )
        elif self._has_level_indicator(title_lower, 2):
            return (
                CourseRole.GATEKEEPER,
                TagConfidence.MEDIUM,
                "Course appears to be level 2 in sequence",
            )

        # Default to concentrator for specialized tool/language courses
        tool_specific = [
            "python",
            "java",
            "javascript",
            "c++",
            "sql",
            "cisco",
            "unity",
            "adobe",
        ]
        if any(tool in title_lower for tool in tool_specific):
            return (
                CourseRole.CONCENTRATOR,
                TagConfidence.LOW,
                "Course appears tool/language specific",
            )

        # Default
        return (
            CourseRole.CONCENTRATOR,
            TagConfidence.LOW,
            "Unable to determine role with confidence",
        )

    def _has_level_indicator(self, title: str, level: int) -> bool:
        """Check if title indicates a specific level.

        Args:
            title: Course title (lowercase)
            level: Level number to check

        Returns:
            True if level indicator found
        """
        patterns = [
            rf"\b{level}\b",
            rf"\bi{level}\b" if level <= 4 else None,
            rf"\b(one|two|three|four)[s]?\b" if level <= 4 else None,
            rf"level\s*{level}",
        ]

        level_words = {1: "one", 2: "two", 3: "three", 4: "four"}
        roman = {1: r"\bi\b", 2: r"\bii\b", 3: r"\biii\b", 4: r"\biv\b"}

        if level in roman:
            if re.search(roman[level], title):
                return True

        if level in level_words:
            if level_words[level] in title:
                return True

        if re.search(rf"\b{level}\b", title):
            return True

        return False

    def _analyze_pathway_shape(
        self, courses: List[CourseInventoryItem]
    ) -> PathwayShape:
        """Analyze the overall pathway shape.

        Args:
            courses: List of courses with roles

        Returns:
            PathwayShape classification
        """
        # Count roles
        role_counts = {role: 0 for role in CourseRole}
        for course in courses:
            if course.role:
                role_counts[course.role] += 1

        exploratory = role_counts[CourseRole.EXPLORATORY]
        gatekeeper = role_counts[CourseRole.GATEKEEPER]
        concentrator = role_counts[CourseRole.CONCENTRATOR]
        capstone = role_counts[CourseRole.CAPSTONE]

        total = len(courses)

        # Analyze shape
        if exploratory == 0:
            if concentrator > 0 or capstone > 0:
                return PathwayShape.MISSING_ENTRY
            return PathwayShape.MISSING_ENTRY

        if exploratory >= 1 and concentrator > exploratory:
            # Check if exploratory leads to concentrators (funnel)
            return PathwayShape.FUNNEL

        # Check for parallel silos
        # If we have multiple exploratory courses in different domains
        exploratory_domains = set()
        for course in courses:
            if course.role == CourseRole.EXPLORATORY and course.domain_tags:
                exploratory_domains.add(course.domain_tags.primary)

        if len(exploratory_domains) > 2:
            return PathwayShape.PARALLEL_SILOS

        # Check for late entry
        late_entry_courses = [
            c
            for c in courses
            if c.role == CourseRole.EXPLORATORY
            and c.grade_band
            and ("11" in c.grade_band or "12" in c.grade_band)
        ]
        if late_entry_courses and not any(
            c.grade_band and ("9" in c.grade_band or "10" in c.grade_band)
            for c in courses
            if c.role == CourseRole.EXPLORATORY
        ):
            return PathwayShape.LATE_ENTRY

        if exploratory >= 1:
            return PathwayShape.FUNNEL

        return PathwayShape.MISSING_ENTRY

    def _analyze_entry_point(
        self, courses: List[CourseInventoryItem]
    ) -> EntryPointAnalysis:
        """Analyze the entry point structure.

        Args:
            courses: List of courses with roles

        Returns:
            EntryPointAnalysis
        """
        # Find exploratory courses
        exploratory_courses = [c for c in courses if c.role == CourseRole.EXPLORATORY]

        if not exploratory_courses:
            # No clear entry point
            # Check if any course might serve as de facto entry
            potential_entries = [
                c
                for c in courses
                if c.role == CourseRole.GATEKEEPER
                or (c.domain_tags and c.domain_tags.confidence == TagConfidence.HIGH)
            ]

            if potential_entries:
                entry = potential_entries[0]
                return EntryPointAnalysis(
                    current_entry_course=entry.title,
                    entry_timing="unclear",
                    entry_breadth="narrow",
                    grade_band=entry.grade_band or "unknown",
                    is_intentional=False,
                    reasoning=(
                        f"No clear entry course identified. '{entry.title}' may serve as "
                        "de facto entry point but is specialized rather than exploratory."
                    ),
                )
            else:
                return EntryPointAnalysis(
                    current_entry_course=None,
                    entry_timing="unclear",
                    entry_breadth="fragmented",
                    grade_band="unknown",
                    is_intentional=False,
                    reasoning="No clear entry point identified for digital pathways.",
                )

        # Analyze the exploratory courses
        if len(exploratory_courses) == 1:
            entry = exploratory_courses[0]
            # Check if it's broad or narrow
            breadth = self._assess_course_breadth(entry)
            timing = self._assess_entry_timing(entry)

            return EntryPointAnalysis(
                current_entry_course=entry.title,
                entry_timing=timing,
                entry_breadth=breadth,
                grade_band=entry.grade_band or "9-10",
                is_intentional=True,
                reasoning=f"'{entry.title}' serves as the entry point for digital pathways.",
            )

        # Multiple exploratory courses
        # Determine if they're coordinated or fragmented
        domains = set()
        for c in exploratory_courses:
            if c.domain_tags:
                domains.add(c.domain_tags.primary)

        if len(domains) >= len(exploratory_courses):
            # Each entry goes to different domain - fragmented
            return EntryPointAnalysis(
                current_entry_course=exploratory_courses[0].title,
                entry_timing="early",
                entry_breadth="fragmented",
                grade_band="9-10",
                is_intentional=False,
                reasoning=(
                    f"Multiple entry points exist ({len(exploratory_courses)} courses) "
                    "serving different domains without clear coordination."
                ),
            )
        else:
            # Some overlap - could be intentional variety
            return EntryPointAnalysis(
                current_entry_course=exploratory_courses[0].title,
                entry_timing="early",
                entry_breadth="broad" if len(domains) > 2 else "narrow",
                grade_band="9-10",
                is_intentional=True,
                reasoning=(
                    f"Multiple entry options available, potentially by design. "
                    f"Primary entry appears to be '{exploratory_courses[0].title}'."
                ),
            )

    def _assess_course_breadth(self, course: CourseInventoryItem) -> str:
        """Assess whether a course is broad or narrow.

        Args:
            course: The course to assess

        Returns:
            'broad', 'narrow', or 'fragmented'
        """
        title_lower = course.title.lower()
        desc_lower = (course.description or "").lower()

        # Broad indicators
        broad_keywords = [
            "foundations",
            "fundamentals",
            "introduction to computing",
            "introduction to technology",
            "digital literacy",
            "computer essentials",
            "exploring",
        ]

        # Narrow indicators (tool/language specific)
        narrow_keywords = [
            "python",
            "java",
            "javascript",
            "web design",
            "graphic design",
            "networking",
            "cybersecurity",
        ]

        if any(kw in title_lower or kw in desc_lower for kw in broad_keywords):
            return "broad"

        if any(kw in title_lower for kw in narrow_keywords):
            return "narrow"

        # Check description for multiple topics
        if course.description:
            topic_count = sum(
                1
                for topic in [
                    "programming",
                    "network",
                    "data",
                    "security",
                    "ai",
                    "web",
                    "hardware",
                ]
                if topic in desc_lower
            )
            if topic_count >= 3:
                return "broad"

        return "narrow"

    def _assess_entry_timing(self, course: CourseInventoryItem) -> str:
        """Assess entry timing based on grade band.

        Args:
            course: The course to assess

        Returns:
            'early', 'late', or 'unclear'
        """
        grade = course.grade_band or ""

        if "9" in grade or "10" in grade:
            if "11" not in grade and "12" not in grade:
                return "early"
            return "early"  # 9-12 still starts early

        if "11" in grade or "12" in grade:
            return "late"

        return "unclear"

    def _identify_pathways(self, courses: List[CourseInventoryItem]) -> List[str]:
        """Identify distinct pathways in the district.

        Args:
            courses: List of courses with roles and tags

        Returns:
            List of pathway names
        """
        pathways = set()

        # Group by primary domain
        domain_courses: Dict[str, List[CourseInventoryItem]] = {}
        for course in courses:
            if course.domain_tags:
                domain = course.domain_tags.primary
                if domain not in domain_courses:
                    domain_courses[domain] = []
                domain_courses[domain].append(course)

        # Identify pathways with at least 2 courses
        for domain, domain_courses_list in domain_courses.items():
            if len(domain_courses_list) >= 2:
                # Check for progression
                has_entry = any(
                    c.role == CourseRole.EXPLORATORY for c in domain_courses_list
                )
                has_advanced = any(
                    c.role in [CourseRole.CONCENTRATOR, CourseRole.CAPSTONE]
                    for c in domain_courses_list
                )

                if has_entry or has_advanced:
                    pathways.add(domain)

        # Check for Program of Study indicators
        pos_courses = [c for c in courses if c.program_of_study]
        for course in pos_courses:
            if course.program_of_study:
                pathways.add(course.program_of_study)

        return list(pathways)

    def _generate_summary(
        self,
        district_name: str,
        courses: List[CourseInventoryItem],
        domain_coverage: DomainCoverage,
        pathway_shape: PathwayShape,
        entry_analysis: EntryPointAnalysis,
    ) -> str:
        """Generate a narrative summary of the landscape.

        Args:
            district_name: District name
            courses: List of courses
            domain_coverage: Domain coverage analysis
            pathway_shape: Pathway shape
            entry_analysis: Entry point analysis

        Returns:
            2-3 sentence summary
        """
        prompt = f"""Generate a 2-3 sentence summary of this district's digital CTE landscape.
The summary should be diagnostic only - describe "what is" without recommendations.

DISTRICT: {district_name}

PATHWAY SHAPE: {pathway_shape.value}
- funnel: Wide intro → narrow specialization
- parallel: Multiple disconnected entry points
- late: Specialization without exploration
- missing: No clear entry point

ENTRY POINT ANALYSIS:
- Current Entry: {entry_analysis.current_entry_course or "None identified"}
- Timing: {entry_analysis.entry_timing}
- Breadth: {entry_analysis.entry_breadth}
- Intentional: {entry_analysis.is_intentional}

DOMAIN COVERAGE:
- Pattern: {domain_coverage.coverage_pattern.value}
- Dominant: {domain_coverage.dominant_domain}
- Total Courses: {domain_coverage.total_courses}

SAMPLE COURSES:
{chr(10).join(f"- {c.title} ({c.role.value if c.role else 'unknown'})" for c in courses[:10])}

Write a factual, neutral summary that describes the current structure.
Do NOT make recommendations or judgments."""

        try:
            response = self.llm.complete(prompt, temperature=0.3)
            return response.strip()
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            # Fallback to template-based summary
            return self._template_summary(
                district_name, pathway_shape, entry_analysis, domain_coverage
            )

    def _template_summary(
        self,
        district_name: str,
        pathway_shape: PathwayShape,
        entry_analysis: EntryPointAnalysis,
        domain_coverage: DomainCoverage,
    ) -> str:
        """Generate a template-based summary as fallback.

        Args:
            district_name: District name
            pathway_shape: Pathway shape
            entry_analysis: Entry point analysis
            domain_coverage: Domain coverage

        Returns:
            Summary text
        """
        shape_descriptions = {
            PathwayShape.FUNNEL: "has a funnel structure with entry courses leading to specialization",
            PathwayShape.PARALLEL_SILOS: "has parallel tracks with separate entry points for different domains",
            PathwayShape.LATE_ENTRY: "has specialization courses but late or unclear entry points",
            PathwayShape.MISSING_ENTRY: "lacks a clear entry point for digital pathways",
        }

        entry_desc = ""
        if entry_analysis.current_entry_course:
            entry_desc = f"The de facto entry appears to be '{entry_analysis.current_entry_course}'"
            if entry_analysis.entry_breadth == "narrow":
                entry_desc += ", which is tool-specific rather than exploratory"
            elif entry_analysis.entry_breadth == "broad":
                entry_desc += ", which provides broad exposure"
        else:
            entry_desc = "No clear entry course was identified"

        return (
            f"{district_name} {shape_descriptions.get(pathway_shape, 'has an unclear structure')}. "
            f"{entry_desc}. "
            f"Domain coverage is {domain_coverage.coverage_pattern.value} with "
            f"{domain_coverage.total_courses} digital courses identified."
        )
