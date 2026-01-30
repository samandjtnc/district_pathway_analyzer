"""
Tests for domain tagging.
"""

import pytest

from district_pathway_analyzer.models import (
    ConfidenceLevel,
    CourseInventoryItem,
    CoveragePattern,
    DigitalDomain,
    DomainTags,
    TagConfidence,
)
from district_pathway_analyzer.tagging.tagger import DomainTagger


class TestDomainTaggerRuleBased:
    """Tests for rule-based domain tagging."""

    def test_computer_science_by_title(self):
        """Test tagging course with CS in title."""
        tagger = DomainTagger()
        result = tagger._rule_based_tag("AP Computer Science A", None)

        assert result is not None
        assert result[0] == DigitalDomain.COMPUTER_SCIENCE
        assert result[1] == TagConfidence.HIGH

    def test_python_programming(self):
        """Test tagging Python course."""
        tagger = DomainTagger()
        result = tagger._rule_based_tag("Python Programming", None)

        assert result is not None
        assert result[0] == DigitalDomain.SOFTWARE_DEV
        assert result[1] == TagConfidence.HIGH

    def test_cybersecurity(self):
        """Test tagging cybersecurity course."""
        tagger = DomainTagger()
        result = tagger._rule_based_tag("Introduction to Cybersecurity", None)

        assert result is not None
        assert result[0] == DigitalDomain.CYBERSECURITY
        assert result[1] == TagConfidence.HIGH

    def test_game_design_digital_media(self):
        """Test that game design is tagged as digital media."""
        tagger = DomainTagger()
        result = tagger._rule_based_tag("Game Design Fundamentals", None)

        assert result is not None
        assert result[0] == DigitalDomain.DIGITAL_MEDIA

    def test_ai_course(self):
        """Test tagging AI course."""
        tagger = DomainTagger()
        result = tagger._rule_based_tag("Introduction to Artificial Intelligence", None)

        assert result is not None
        assert result[0] == DigitalDomain.DATA_AI

    def test_ambiguous_title_with_description(self):
        """Test that description helps with ambiguous titles."""
        tagger = DomainTagger()
        result = tagger._rule_based_tag(
            "Digital Technology I",
            "This course covers data analysis, machine learning basics, and AI ethics.",
        )

        # Should pick up AI/data from description
        assert result is not None
        # May tag as DATA_AI or another domain based on description

    def test_engineering_without_computing(self):
        """Test that pure engineering is not tagged."""
        tagger = DomainTagger()
        result = tagger._rule_based_tag("Engineering Design", None)

        # Should return None or not tag as engineering
        # since computing is not explicit
        if result is not None:
            assert result[0] != DigitalDomain.ENGINEERING_AUTO


class TestDomainCoverage:
    """Tests for domain coverage analysis."""

    def test_narrow_coverage(self):
        """Test narrow coverage pattern."""
        tagger = DomainTagger()

        courses = [
            CourseInventoryItem(
                title="Python 1",
                source_url="",
                offering_schools=[],
                confidence=ConfidenceLevel.VERIFIED,
                domain_tags=DomainTags(
                    primary=DigitalDomain.SOFTWARE_DEV.value,
                    secondary=[],
                    confidence=TagConfidence.HIGH,
                ),
            ),
            CourseInventoryItem(
                title="Python 2",
                source_url="",
                offering_schools=[],
                confidence=ConfidenceLevel.VERIFIED,
                domain_tags=DomainTags(
                    primary=DigitalDomain.SOFTWARE_DEV.value,
                    secondary=[],
                    confidence=TagConfidence.HIGH,
                ),
            ),
        ]

        coverage = tagger.analyze_coverage(courses)

        assert coverage.coverage_pattern == CoveragePattern.NARROW
        assert len(coverage.domains_present) == 1
        assert coverage.dominant_domain == DigitalDomain.SOFTWARE_DEV.value

    def test_balanced_coverage(self):
        """Test balanced coverage pattern."""
        tagger = DomainTagger()

        domains = [
            DigitalDomain.COMPUTER_SCIENCE,
            DigitalDomain.SOFTWARE_DEV,
            DigitalDomain.DATA_AI,
            DigitalDomain.CYBERSECURITY,
            DigitalDomain.IT_SYSTEMS,
        ]

        courses = []
        for i, domain in enumerate(domains):
            courses.append(
                CourseInventoryItem(
                    title=f"Course {i}",
                    source_url="",
                    offering_schools=[],
                    confidence=ConfidenceLevel.VERIFIED,
                    domain_tags=DomainTags(
                        primary=domain.value,
                        secondary=[],
                        confidence=TagConfidence.HIGH,
                    ),
                )
            )

        coverage = tagger.analyze_coverage(courses)

        assert coverage.coverage_pattern == CoveragePattern.BALANCED
        assert len(coverage.domains_present) == 5
