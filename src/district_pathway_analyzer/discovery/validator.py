"""
Source validation and discovery gate checking.
"""

import logging
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

from district_pathway_analyzer.config import get_config
from district_pathway_analyzer.models import (
    ConfidenceLevel,
    CourseInventory,
    DiscoveryGateResult,
    Source,
    SourceValidation,
)

logger = logging.getLogger(__name__)


class SourceValidator:
    """Validates discovered sources."""

    def __init__(self, district_name: str):
        """Initialize the validator.

        Args:
            district_name: Name of the district for validation
        """
        self.district_name = district_name.lower()
        self.config = get_config()

    def validate(self, source: Source) -> SourceValidation:
        """Validate a source.

        Args:
            source: The source to validate

        Returns:
            SourceValidation result
        """
        reasons = []
        confidence = 1.0

        # Check domain relevance
        domain = self._extract_domain(source.url)
        if domain:
            # Check if domain likely belongs to district
            district_words = set(self.district_name.replace("-", " ").split())
            domain_words = set(domain.replace("-", "").replace(".", " ").split())

            overlap = district_words & domain_words
            if not overlap:
                # Check for common educational domains
                if not any(
                    edu in domain for edu in [".edu", ".k12.", "schools", "school"]
                ):
                    confidence *= 0.5
                    reasons.append("Domain may not belong to district")

        # Check URL patterns for CTE content
        url_lower = source.url.lower()
        cte_indicators = ["cte", "career", "technical", "program", "course", "pathway"]
        if not any(indicator in url_lower for indicator in cte_indicators):
            confidence *= 0.8
            reasons.append("URL does not indicate CTE content")

        # Check recency (if we can determine)
        year_patterns = ["2024", "2025", "2026", "24-25", "25-26"]
        if any(year in source.url for year in year_patterns):
            confidence *= 1.1  # Boost for recent
        elif any(year in source.url for year in ["2020", "2021", "2022"]):
            confidence *= 0.7
            reasons.append("Source may be outdated")

        # Cap confidence at 1.0
        confidence = min(confidence, 1.0)

        valid = confidence >= 0.5
        reason = "; ".join(reasons) if reasons else "Source appears valid"

        return SourceValidation(valid=valid, confidence=confidence, reason=reason)

    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract domain from URL.

        Args:
            url: The URL

        Returns:
            Domain string or None
        """
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except Exception:
            return None


class DiscoveryGate:
    """Checks if discovery results pass the gate criteria.

    The discovery gate focuses on data availability and quality:
    - At least 1 verified source
    - Minimum number of courses found
    - Acceptable confidence levels

    Note: Domain coverage is checked AFTER tagging in Phase 1, not here.
    """

    def __init__(self):
        """Initialize the gate checker."""
        self.config = get_config()

    def check(self, inventory: CourseInventory) -> DiscoveryGateResult:
        """Check if the inventory passes the discovery gate.

        Args:
            inventory: The course inventory to check

        Returns:
            DiscoveryGateResult indicating pass/fail and details
        """
        result = DiscoveryGateResult()
        result.courses_found = len(inventory.courses)

        issues = []
        suggestions = []

        # Log extracted courses for debugging
        if inventory.courses:
            logger.info(f"Discovery found {len(inventory.courses)} courses:")
            for i, course in enumerate(inventory.courses, 1):
                logger.info(f"  {i}. {course.title} [{course.confidence.value}]")
        else:
            logger.warning("No courses were extracted from the sources")

        # Check 1: At least 1 verified source
        verified_sources = [s for s in inventory.sources if s.is_valid]
        if not verified_sources:
            issues.append("No verified sources found")
            suggestions.append("Provide direct link to district CTE course catalog (PDF or webpage)")
            result.passed = False
            result.reason = "No verified sources found"
            result.issues = issues
            result.suggestions = suggestions
            return result

        # Check 2: Minimum courses found
        min_courses = self.config.gates.min_courses_found
        if result.courses_found < min_courses:
            issues.append(f"Only {result.courses_found} courses found (minimum: {min_courses})")
            suggestions.append("Upload Program of Study document or course catalog")

        # Check 3: Verified percentage
        result.verified_percentage = inventory.verified_percentage
        min_verified = self.config.gates.min_verified_percentage
        if result.verified_percentage < min_verified:
            issues.append(
                f"Only {result.verified_percentage:.0%} of courses verified "
                f"(minimum: {min_verified:.0%})"
            )
            suggestions.append("Provide more authoritative source documents")

        # Check 4: Uncertain percentage
        uncertain_count = len(
            [c for c in inventory.courses if c.confidence == ConfidenceLevel.UNCERTAIN]
        )
        uncertain_pct = uncertain_count / len(inventory.courses) if inventory.courses else 1.0
        max_uncertain = self.config.gates.max_uncertain_percentage
        if uncertain_pct > max_uncertain:
            issues.append(
                f"{uncertain_pct:.0%} of courses are uncertain (maximum: {max_uncertain:.0%})"
            )
            suggestions.append("Provide clearer course descriptions or catalog")

        # Note: Domain coverage is checked AFTER tagging in Phase 1, not here.
        # At this stage, courses don't have domain_tags assigned yet.
        # The discovery gate focuses on: sources, course count, and confidence levels.

        # Determine pass/fail
        if len(issues) >= 3:
            result.passed = False
            result.reason = "Multiple data quality issues"
        elif result.courses_found < min_courses:
            result.passed = False
            result.reason = f"Insufficient courses found ({result.courses_found} < {min_courses})"
        else:
            result.passed = True
            result.reason = "Discovery gate passed"

        result.issues = issues
        result.suggestions = suggestions

        return result

    def generate_failure_message(self, result: DiscoveryGateResult) -> str:
        """Generate a user-friendly failure message.

        Args:
            result: The gate result

        Returns:
            Formatted failure message
        """
        if result.passed:
            return "Discovery gate passed successfully."

        message = f"""Status: Discovery Incomplete

Issue: {result.reason}

What This Means:
The system could not reliably identify the district's current digital CTE course offerings.

Issues Found:
"""
        for issue in result.issues:
            message += f"  - {issue}\n"

        message += """
What Would Help:
"""
        for suggestion in result.suggestions:
            message += f"  - {suggestion}\n"

        message += """
You can provide documents manually using the --documents option."""

        return message
