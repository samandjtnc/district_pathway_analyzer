"""
Domain tagging for CTE courses.
"""

import json
import logging
import re
from typing import Dict, List, Optional, Tuple

from district_pathway_analyzer.llm_client import get_llm_client
from district_pathway_analyzer.models import (
    CourseInventoryItem,
    CoveragePattern,
    DigitalDomain,
    DomainCoverage,
    DomainTags,
    TagConfidence,
)

logger = logging.getLogger(__name__)


# Domain definitions for reference
DOMAIN_DEFINITIONS = {
    DigitalDomain.COMPUTER_SCIENCE: (
        "Algorithms, computational thinking, programming concepts, abstraction, "
        "theoretical foundations"
    ),
    DigitalDomain.SOFTWARE_DEV: (
        "Language-specific, tool-forward coding courses (Python Programming, "
        "Java Development)"
    ),
    DigitalDomain.DATA_AI: (
        "AI concepts, data analysis, machine learning, modeling, AI ethics"
    ),
    DigitalDomain.CYBERSECURITY: (
        "Network systems, security principles, infrastructure, threat mitigation"
    ),
    DigitalDomain.IT_SYSTEMS: (
        "Hardware, operating systems, troubleshooting, IT support, help desk"
    ),
    DigitalDomain.ENGINEERING_AUTO: (
        "Robotics, mechatronics (ONLY if computing/software is explicit)"
    ),
    DigitalDomain.DIGITAL_MEDIA: (
        "Design, media production, game design, digital arts"
    ),
    DigitalDomain.EMERGING_TECH: (
        "IoT, cloud computing, AR/VR, drones, blockchain"
    ),
}

# Title keyword mappings for rule-based tagging
TITLE_KEYWORDS = {
    DigitalDomain.COMPUTER_SCIENCE: [
        "computer science",
        "ap computer science",
        "ap cs",
        "computational thinking",
        "algorithms",
        "data structures",
    ],
    DigitalDomain.SOFTWARE_DEV: [
        "programming",
        "python",
        "java",
        "javascript",
        "c++",
        "software",
        "coding",
        "app development",
        "mobile development",
        "web development",
    ],
    DigitalDomain.DATA_AI: [
        "artificial intelligence",
        "ai",
        "machine learning",
        "data science",
        "data analytics",
        "big data",
    ],
    DigitalDomain.CYBERSECURITY: [
        "cybersecurity",
        "cyber security",
        "network security",
        "information security",
        "ethical hacking",
        "networking",
        "network admin",
        "cisco",
    ],
    DigitalDomain.IT_SYSTEMS: [
        "information technology",
        "it support",
        "it essentials",
        "tech support",
        "help desk",
        "computer repair",
        "hardware",
        "a+ certification",
        "comptia",
    ],
    DigitalDomain.ENGINEERING_AUTO: [
        "robotics",
        "automation",
        "mechatronics",
        "engineering technology",
    ],
    DigitalDomain.DIGITAL_MEDIA: [
        "game design",
        "game development",
        "graphic design",
        "digital design",
        "animation",
        "multimedia",
        "video production",
        "digital media",
        "3d modeling",
        "digital art",
    ],
    DigitalDomain.EMERGING_TECH: [
        "cloud computing",
        "iot",
        "internet of things",
        "virtual reality",
        "augmented reality",
        "drone",
        "blockchain",
    ],
}


class DomainTagger:
    """Tags courses with their Digital Technology domains."""

    def __init__(self):
        """Initialize the tagger."""
        self.llm = get_llm_client()

    def tag_course(self, course: CourseInventoryItem) -> CourseInventoryItem:
        """Tag a course with its domain(s).

        Args:
            course: The course to tag

        Returns:
            Course with domain_tags populated
        """
        # First, try rule-based tagging
        rule_result = self._rule_based_tag(course.title, course.description)

        if rule_result and rule_result[1] == TagConfidence.HIGH:
            # High confidence from rules, use it
            course.domain_tags = DomainTags(
                primary=rule_result[0].value,
                secondary=[d.value for d in rule_result[2]],
                confidence=rule_result[1],
                reasoning=f"Rule-based: title contains '{rule_result[3]}'",
            )
            return course

        # Use LLM for more nuanced tagging
        llm_result = self._llm_tag(course.title, course.description)

        if llm_result:
            course.domain_tags = llm_result
        elif rule_result:
            # Fall back to rule-based if LLM fails
            course.domain_tags = DomainTags(
                primary=rule_result[0].value,
                secondary=[d.value for d in rule_result[2]],
                confidence=rule_result[1],
                reasoning=f"Rule-based: title contains '{rule_result[3]}'",
            )

        return course

    def tag_courses(
        self, courses: List[CourseInventoryItem]
    ) -> List[CourseInventoryItem]:
        """Tag multiple courses.

        Args:
            courses: List of courses to tag

        Returns:
            List of courses with domain_tags populated
        """
        tagged = []
        for course in courses:
            tagged.append(self.tag_course(course))
        return tagged

    def _rule_based_tag(
        self, title: str, description: Optional[str]
    ) -> Optional[Tuple[DigitalDomain, TagConfidence, List[DigitalDomain], str]]:
        """Apply rule-based tagging.

        Args:
            title: Course title
            description: Course description

        Returns:
            Tuple of (primary_domain, confidence, secondary_domains, matched_keyword)
            or None if no match
        """
        title_lower = title.lower()
        desc_lower = description.lower() if description else ""

        primary = None
        primary_keyword = ""
        secondary = []
        confidence = TagConfidence.LOW

        # Check title for keywords (highest priority)
        for domain, keywords in TITLE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in title_lower:
                    if primary is None:
                        primary = domain
                        primary_keyword = keyword
                        confidence = TagConfidence.HIGH
                    elif domain not in secondary and domain != primary:
                        secondary.append(domain)

        # If no title match, check description (medium confidence)
        if primary is None and desc_lower:
            for domain, keywords in TITLE_KEYWORDS.items():
                for keyword in keywords:
                    if keyword in desc_lower:
                        if primary is None:
                            primary = domain
                            primary_keyword = keyword
                            confidence = TagConfidence.MEDIUM
                        elif domain not in secondary and domain != primary:
                            secondary.append(domain)

        # Special rules

        # Rule 3: Engineering ONLY if computing explicit
        if primary == DigitalDomain.ENGINEERING_AUTO:
            has_computing = any(
                kw in title_lower or kw in desc_lower
                for kw in ["programming", "python", "code", "software"]
            )
            if not has_computing:
                # Demote to secondary or remove
                if secondary:
                    primary = secondary.pop(0)
                else:
                    return None

        # Rule 5: AI is not assumed from general CS
        # (already handled by keyword specificity)

        if primary:
            return (primary, confidence, secondary[:2], primary_keyword)  # Max 2 secondary
        return None

    def _llm_tag(
        self, title: str, description: Optional[str]
    ) -> Optional[DomainTags]:
        """Use LLM for nuanced domain tagging.

        Args:
            title: Course title
            description: Course description

        Returns:
            DomainTags or None if tagging fails
        """
        domain_list = "\n".join(
            f"- {d.value}: {DOMAIN_DEFINITIONS[d]}" for d in DigitalDomain
        )

        prompt = f"""Classify this CTE course into Digital Technology domains.

COURSE TITLE: {title}
COURSE DESCRIPTION: {description or "Not provided"}

AVAILABLE DOMAINS:
{domain_list}

TAGGING RULES:
1. Title-First Tagging: The course title is the strongest signal
2. Description Clarifies Ambiguous Titles: Use description for unclear cases
3. Engineering ONLY if Computing Explicit: Don't tag as Engineering unless programming/software is mentioned
4. Creative ≠ Non-Technical: Game Design, Graphic Design are valid Digital Media courses
5. AI is Not Assumed: Don't assume AI content unless explicitly mentioned

Select exactly ONE primary domain and 0-2 secondary domains.

Respond with JSON only:
{{
    "primary": "Domain Name (exactly as listed)",
    "secondary": ["Optional secondary domain(s)"],
    "confidence": "High" | "Medium" | "Low",
    "reasoning": "Brief explanation of classification"
}}"""

        system = """You are an expert in Career and Technical Education (CTE) curriculum classification.
You classify courses into Digital Technology domains based on their titles and descriptions.
You follow the tagging rules precisely and provide accurate, conservative classifications."""

        try:
            response = self.llm.complete_structured(prompt, system=system)

            # Parse JSON
            json_match = re.search(r"\{[\s\S]*\}", response)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(response)

            # Validate primary domain
            primary = data.get("primary", "")
            valid_domains = [d.value for d in DigitalDomain]
            if primary not in valid_domains:
                # Try to find closest match
                for vd in valid_domains:
                    if primary.lower() in vd.lower() or vd.lower() in primary.lower():
                        primary = vd
                        break
                else:
                    logger.warning(f"Invalid domain returned: {primary}")
                    return None

            # Validate secondary domains
            secondary = []
            for s in data.get("secondary", []):
                if s in valid_domains and s != primary:
                    secondary.append(s)

            # Validate confidence
            conf_str = data.get("confidence", "Medium")
            try:
                confidence = TagConfidence(conf_str)
            except ValueError:
                confidence = TagConfidence.MEDIUM

            return DomainTags(
                primary=primary,
                secondary=secondary[:2],
                confidence=confidence,
                reasoning=data.get("reasoning", ""),
            )

        except Exception as e:
            logger.error(f"LLM tagging failed: {e}")
            return None

    def analyze_coverage(
        self, courses: List[CourseInventoryItem]
    ) -> DomainCoverage:
        """Analyze domain coverage across courses.

        Args:
            courses: List of tagged courses

        Returns:
            DomainCoverage analysis
        """
        domain_counts: Dict[str, int] = {}

        for course in courses:
            if course.domain_tags:
                primary = course.domain_tags.primary
                domain_counts[primary] = domain_counts.get(primary, 0) + 1

        # Determine coverage pattern
        total = len(courses)
        num_domains = len(domain_counts)

        if num_domains >= 5:
            # Check for reasonable distribution
            max_count = max(domain_counts.values()) if domain_counts else 0
            if total > 0 and max_count / total < 0.5:
                pattern = CoveragePattern.BALANCED
            else:
                pattern = CoveragePattern.SKEWED
        elif num_domains >= 3:
            max_count = max(domain_counts.values()) if domain_counts else 0
            if total > 0 and max_count / total >= 0.8:
                pattern = CoveragePattern.SKEWED
            else:
                pattern = CoveragePattern.SKEWED
        else:
            pattern = CoveragePattern.NARROW

        # Find gaps
        all_domains = {d.value for d in DigitalDomain}
        covered = set(domain_counts.keys())
        gaps = list(all_domains - covered)

        # Find dominant domain
        dominant = None
        if domain_counts:
            dominant = max(domain_counts, key=domain_counts.get)

        return DomainCoverage(
            domains_present=domain_counts,
            coverage_pattern=pattern,
            gaps=gaps,
            dominant_domain=dominant,
            total_courses=total,
        )
