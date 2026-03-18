"""
Generate synthetic course descriptions for better analysis.

When course descriptions are missing from source documents, this module
generates them using AI to enrich the analysis pipeline.
"""

import json
import logging
import re
from typing import Dict, List, Optional

from district_pathway_analyzer.llm_client import get_llm_client
from district_pathway_analyzer.models import CourseInventoryItem

logger = logging.getLogger(__name__)

_BATCH_SIZE = 5


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

        # Process in batches of _BATCH_SIZE to reduce LLM call count
        for i in range(0, len(courses_needing_descriptions), _BATCH_SIZE):
            batch = courses_needing_descriptions[i : i + _BATCH_SIZE]
            titles = [c.title for c in batch]
            try:
                descriptions = self._generate_descriptions_batch(titles)
                for course in batch:
                    desc = descriptions.get(course.title)
                    if desc:
                        course.description = desc
                        self.generation_count += 1
                        logger.info(f"Generated description for '{course.title}': {desc[:80]}...")
                    else:
                        logger.warning(f"No description returned for '{course.title}'")
            except Exception as e:
                logger.warning(f"Batch description generation failed, retrying individually: {e}")
                # Fall back to per-course calls if batch fails
                for course in batch:
                    try:
                        desc = self._generate_description_single(course.title)
                        if desc:
                            course.description = desc
                            self.generation_count += 1
                    except Exception as inner_e:
                        logger.warning(f"Failed to generate description for '{course.title}': {inner_e}")

        logger.info(f"Successfully generated {self.generation_count} course descriptions")
        return courses

    def _generate_descriptions_batch(self, titles: List[str]) -> Dict[str, str]:
        """Generate descriptions for a batch of courses in a single LLM call.

        Args:
            titles: List of course titles (up to _BATCH_SIZE)

        Returns:
            Dict mapping title → generated description
        """
        titles_list = "\n".join(f"{i + 1}. {t}" for i, t in enumerate(titles))
        prompt = f"""Generate concise 2-3 sentence CTE course catalog descriptions for each course below.

COURSES:
{titles_list}

REQUIREMENTS for each description:
- Focus on what students will learn and do
- Mention typical software/tools used (if applicable)
- Include career connections when relevant
- Professional, catalog-appropriate language
- Under 100 words each

Respond with JSON only — an object mapping each course title exactly to its description:
{{
  "Course Title 1": "Description...",
  "Course Title 2": "Description...",
  ...
}}"""

        try:
            raw = self.llm.complete_structured(prompt, temperature=0.7)
            # complete_structured already strips markdown fences
            data = json.loads(raw)
            # Validate: only keep entries with reasonable descriptions
            return {
                title: desc
                for title, desc in data.items()
                if isinstance(desc, str) and len(desc) >= 20
            }
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Batch description parse failed: {e}")
            raise

    def _generate_description_single(self, course_title: str) -> Optional[str]:
        """Fallback: generate a description for a single course.

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
            description = self.llm.complete(prompt, temperature=0.7).strip()
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
