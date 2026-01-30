"""
Tests for data models.
"""

import pytest

from district_pathway_analyzer.models import (
    AIFStrategy,
    AIFoundationsRole,
    ConfidenceLevel,
    CourseInventoryItem,
    CourseRole,
    DesignInvariants,
    DigitalDomain,
    DistrictInput,
    DomainTags,
    PathwayShape,
    TagConfidence,
)


class TestDistrictInput:
    """Tests for DistrictInput model."""

    def test_basic_creation(self):
        """Test basic DistrictInput creation."""
        input_data = DistrictInput(
            district_name="Johnston County Schools",
            state="North Carolina",
        )
        assert input_data.district_name == "Johnston County Schools"
        assert input_data.state == "North Carolina"
        assert input_data.user_provided_urls == []

    def test_with_urls(self):
        """Test DistrictInput with URLs."""
        input_data = DistrictInput(
            district_name="Test District",
            state="CA",
            user_provided_urls=["https://example.com/cte"],
        )
        assert len(input_data.user_provided_urls) == 1


class TestCourseInventoryItem:
    """Tests for CourseInventoryItem model."""

    def test_required_fields_only(self):
        """Test creation with only required fields."""
        course = CourseInventoryItem(
            title="Introduction to Computer Science",
            source_url="https://example.com",
            offering_schools=["High School A"],
            confidence=ConfidenceLevel.VERIFIED,
        )
        assert course.title == "Introduction to Computer Science"
        assert course.course_code is None
        assert course.domain_tags is None

    def test_with_domain_tags(self):
        """Test creation with domain tags."""
        tags = DomainTags(
            primary=DigitalDomain.COMPUTER_SCIENCE.value,
            secondary=[DigitalDomain.SOFTWARE_DEV.value],
            confidence=TagConfidence.HIGH,
            reasoning="Title explicitly mentions computer science",
        )
        course = CourseInventoryItem(
            title="AP Computer Science A",
            source_url="https://example.com",
            offering_schools=[],
            confidence=ConfidenceLevel.VERIFIED,
            domain_tags=tags,
        )
        assert course.domain_tags.primary == "Computer Science (CS)"
        assert len(course.domain_tags.secondary) == 1

    def test_alignment_candidate(self):
        """Test alignment candidate flagging."""
        course = CourseInventoryItem(
            title="Computing Foundations",
            source_url="https://example.com",
            offering_schools=[],
            confidence=ConfidenceLevel.VERIFIED,
            is_alignment_candidate=True,
            alignment_candidate_reason="Broad digital foundations course",
        )
        assert course.is_alignment_candidate is True


class TestDesignInvariants:
    """Tests for DesignInvariants model."""

    def test_all_satisfied(self):
        """Test when all invariants are satisfied."""
        invariants = DesignInvariants()
        assert invariants.all_satisfied() is True
        assert len(invariants.violations()) == 0

    def test_violations(self):
        """Test when invariants are violated."""
        invariants = DesignInvariants(
            aif_is_entry=False,
            downstream_intact=True,
            reduces_cognitive_load=False,
        )
        assert invariants.all_satisfied() is False
        violations = invariants.violations()
        assert len(violations) == 2
        assert any("entry experience" in v for v in violations)
        assert any("cognitive load" in v for v in violations)


class TestEnums:
    """Tests for enum values."""

    def test_digital_domain_values(self):
        """Test DigitalDomain enum values."""
        assert DigitalDomain.COMPUTER_SCIENCE.value == "Computer Science (CS)"
        assert DigitalDomain.DATA_AI.value == "Data Science & Artificial Intelligence"

    def test_pathway_shape_values(self):
        """Test PathwayShape enum values."""
        assert PathwayShape.FUNNEL.value == "funnel"
        assert PathwayShape.PARALLEL_SILOS.value == "parallel"

    def test_course_role_values(self):
        """Test CourseRole enum values."""
        assert CourseRole.EXPLORATORY.value == "exploratory"
        assert CourseRole.CAPSTONE.value == "capstone"

    def test_aif_strategy_values(self):
        """Test AIFStrategy enum values."""
        assert AIFStrategy.POSITION_NEW.value == "position_new"
        assert AIFStrategy.ALIGN_EXISTING.value == "align_existing"
