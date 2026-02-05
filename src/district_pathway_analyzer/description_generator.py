"""
Generate synthetic course descriptions for better analysis.

When course descriptions are missing from source documents, this module
generates them using AI to enrich the analysis pipeline.
"""

import logging
import os
from typing import List, Optional

from district_pathway_analyzer.llm_client import get_llm_client
from district_pathway_analyzer.models import CourseInventoryItem

logger = logging.getLogger(__name__)


class DescriptionGenerator:
    """Generates course descriptions using AI for courses missing descriptions."""

    def __init__(self, model: str = "claude-haiku-4-5-20251101"):
        """Initialize the description generator.

        Args:
            model: Model to use for generation. Defaults to Haiku for cost efficiency.
        """
        self.llm = get_llm_client()
        self.model = model
        self.generation_count = 0

    def enrich_courses(self, courses: List[CourseInventoryItem]) -> List[CourseInventoryItem]:
        """Enrich courses with generated descriptions where missing.

        Args:
            courses: List of courses to enrich

        Returns:
            List of courses with generated descriptions added
        """
        courses_needing_descriptions = [
            course for course in courses if not course.description or course.description.strip() == ""
        ]

        if not courses_needing_descriptions:
            logger.info("All courses already have descriptions")
            return courses

        logger.info(
            f"Generating descriptions for {len(courses_needing_descriptions)} courses "
            f"(out of {len(courses)} total)"
        )

        # Generate descriptions in batches for efficiency
        for course in courses_needing_descriptions:
            try:
                description = self._generate_description(course.title)
                if description:
                    course.description = description
                    self.generation_count += 1
                    logger.debug(f"Generated description for: {course.title}")
            except Exception as e:
                logger.warning(f"Failed to generate description for '{course.title}': {e}")
                # Continue without description rather than failing the entire pipeline

        logger.info(f"Successfully generated {self.generation_count} course descriptions")
        return courses

    def _generate_description(self, course_title: str) -> Optional[str]:
        """Generate a description for a single course.

        Args:
            course_title: Title of the course

        Returns:
            Generated description or None if generation fails
        """
        prompt = f"""Create a concise 2-3 sentence description for a high school CTE course catalog.

Course Title: {course_title}

Requirements:
- Focus on what students will learn and do
- Mention typical software/tools used (if applicable)
- Include career connections when relevant
- Use professional, catalog-appropriate language
- Keep it under 100 words

Description:"""

        try:
            response = self.llm.messages.create(
                model=self.model,
                max_tokens=200,  # Short descriptions only
                temperature=0.7,  # Some creativity but mostly factual
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            description = response.content[0].text.strip()

            # Sanity check: description should be reasonable length
            if len(description) < 20:
                logger.warning(f"Generated description too short for '{course_title}'")
                return None

            return description

        except Exception as e:
            logger.error(f"API call failed for '{course_title}': {e}")
            return None

    def get_generation_stats(self) -> dict:
        """Get statistics about description generation.

        Returns:
            Dictionary with generation statistics
        """
        return {
            "descriptions_generated": self.generation_count,
            "model_used": self.model,
        }
