"""
Course data extraction from various source types.
"""

import io
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from bs4 import BeautifulSoup

from district_pathway_analyzer.llm_client import get_llm_client
from district_pathway_analyzer.models import (
    ConfidenceLevel,
    CourseInventoryItem,
    RawCourseData,
    Source,
    SourceType,
)

logger = logging.getLogger(__name__)


# Keywords that indicate digital/technical CTE courses
DIGITAL_KEYWORDS = [
    "computer",
    "computing",
    "programming",
    "software",
    "web",
    "digital",
    "technology",
    "cyber",
    "security",
    "network",
    "data",
    "database",
    "python",
    "java",
    "javascript",
    "coding",
    "AI",
    "artificial intelligence",
    "machine learning",
    "robotics",
    "IT",
    "information technology",
    "game design",
    "game development",
    "animation",
    "multimedia",
    "graphic design",
    "app development",
    "mobile",
    "cloud",
    "systems",
    "engineering",  # when combined with technology
]

# Course title patterns to exclude
EXCLUDE_PATTERNS = [
    r"^physical education",
    r"^pe\s",
    r"^health\s",
    r"^art\s[1-4]",
    r"^music\s",
    r"^band\s",
    r"^choir",
    r"^orchestra",
    r"^drama",
    r"^theater",
    r"^foreign language",
    r"^spanish",
    r"^french",
    r"^german",
    r"^chinese",
    r"^latin",
]


class CourseExtractor:
    """Extracts course information from various source types."""

    def __init__(self):
        """Initialize the extractor."""
        self.llm = get_llm_client()

    def extract_from_source(self, source: Source, content: Any) -> RawCourseData:
        """Extract course data from a source.

        Args:
            source: The source metadata
            content: The source content (text or bytes)

        Returns:
            RawCourseData with extracted information
        """
        if source.source_type == SourceType.HTML:
            return self._extract_from_html(content, source.url)
        elif source.source_type == SourceType.PDF:
            return self._extract_from_pdf(content, source.url)
        else:
            return self._extract_from_text(content, source.url)

    def extract_from_file(self, file_path: str) -> RawCourseData:
        """Extract course data from a local file.

        Args:
            file_path: Path to the file

        Returns:
            RawCourseData with extracted information
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        suffix = path.suffix.lower()

        if suffix == ".pdf":
            with open(path, "rb") as f:
                content = f.read()
            return self._extract_from_pdf(content, f"file://{file_path}")
        elif suffix in [".html", ".htm"]:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return self._extract_from_html(content, f"file://{file_path}")
        else:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return self._extract_from_text(content, f"file://{file_path}")

    def _extract_from_html(self, html_content: str, source_url: str) -> RawCourseData:
        """Extract course data from HTML content.

        Args:
            html_content: The HTML content
            source_url: The source URL

        Returns:
            RawCourseData with extracted information
        """
        soup = BeautifulSoup(html_content, "html.parser")

        # Remove script and style elements
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()

        # Get text content
        text = soup.get_text(separator="\n", strip=True)

        # Use LLM to extract structured course data
        return self._extract_with_llm(text, source_url)

    def _extract_from_pdf(self, pdf_content: bytes, source_url: str) -> RawCourseData:
        """Extract course data from PDF content.

        Args:
            pdf_content: The PDF content as bytes
            source_url: The source URL

        Returns:
            RawCourseData with extracted information
        """
        try:
            # Try to extract text from PDF
            from PyPDF2 import PdfReader

            reader = PdfReader(io.BytesIO(pdf_content))
            text_parts = []

            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

            text = "\n".join(text_parts)

            if len(text.strip()) < 100:
                # PDF might be image-based, need OCR
                logger.warning("PDF appears to be image-based, text extraction limited")
                return RawCourseData(source_url=source_url, extraction_confidence=0.3)

            return self._extract_with_llm(text, source_url)

        except Exception as e:
            logger.error(f"Failed to extract from PDF: {e}")
            return RawCourseData(source_url=source_url, extraction_confidence=0.0)

    def _extract_from_text(self, text_content: str, source_url: str) -> RawCourseData:
        """Extract course data from plain text content.

        Args:
            text_content: The text content
            source_url: The source URL

        Returns:
            RawCourseData with extracted information
        """
        return self._extract_with_llm(text_content, source_url)

    def _extract_with_llm(self, text: str, source_url: str) -> RawCourseData:
        """Use LLM to extract structured course data from text.

        Args:
            text: The text content to analyze
            source_url: The source URL

        Returns:
            RawCourseData with extracted information
        """
        # Truncate text if too long
        max_chars = 50000
        if len(text) > max_chars:
            text = text[:max_chars] + "\n...[truncated]..."

        prompt = f"""Analyze this school district document and extract information about digital technology and computer-related CTE (Career and Technical Education) courses.

Focus on courses related to:
- Computer Science
- Programming/Software Development
- Information Technology
- Cybersecurity/Networking
- Data Science/AI
- Digital Media/Design
- Web Development
- Robotics (if programming-focused)

For each course found, extract:
1. Course title (exact name)
2. Course code (if available)
3. Description (if available)
4. Grade level (if stated)
5. Credit type (CTE, Academic, Elective if stated)

DOCUMENT CONTENT:
{text}

Respond with a JSON object in this exact format:
{{
    "courses": [
        {{
            "title": "Course Title",
            "code": "ABC123 or null",
            "description": "Course description or null",
            "grade_level": "9-12 or null",
            "credit_type": "CTE or null"
        }}
    ],
    "extraction_confidence": 0.8,
    "notes": "Any relevant notes about the extraction"
}}

Only include courses that are clearly digital/technical CTE courses. Do not include general education courses, arts courses, or non-technical electives."""

        system = """You are an expert at extracting structured information from educational documents.
You carefully identify CTE (Career and Technical Education) courses related to digital technology,
computer science, and information technology. You provide accurate, well-structured JSON output."""

        try:
            response = self.llm.complete_structured(prompt, system=system)

            # Parse JSON response
            # Try to extract JSON from response (may have markdown code blocks)
            json_match = re.search(r"\{[\s\S]*\}", response)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(response)

            # Build RawCourseData
            raw_data = RawCourseData(
                source_url=source_url,
                extraction_confidence=data.get("extraction_confidence", 0.5),
            )

            for course in data.get("courses", []):
                title = course.get("title")
                if title:
                    raw_data.titles.append(title)
                    if course.get("description"):
                        raw_data.descriptions[title] = course["description"]
                    if course.get("code"):
                        raw_data.course_codes[title] = course["code"]
                    if course.get("grade_level"):
                        raw_data.grade_levels[title] = course["grade_level"]
                    if course.get("credit_type"):
                        raw_data.credit_types[title] = course["credit_type"]

            return raw_data

        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return RawCourseData(source_url=source_url, extraction_confidence=0.0)

    def raw_to_inventory(
        self, raw_data: RawCourseData, schools: Optional[List[str]] = None
    ) -> List[CourseInventoryItem]:
        """Convert raw course data to inventory items.

        Args:
            raw_data: The raw extracted data
            schools: Optional list of school names offering these courses

        Returns:
            List of CourseInventoryItem objects
        """
        items = []

        for title in raw_data.titles:
            # Determine confidence level
            confidence = ConfidenceLevel.VERIFIED
            if raw_data.extraction_confidence < 0.7:
                confidence = ConfidenceLevel.INFERRED
            if raw_data.extraction_confidence < 0.4:
                confidence = ConfidenceLevel.UNCERTAIN

            item = CourseInventoryItem(
                title=title,
                source_url=raw_data.source_url,
                offering_schools=schools or [],
                confidence=confidence,
                course_code=raw_data.course_codes.get(title),
                description=raw_data.descriptions.get(title),
                credit_type=raw_data.credit_types.get(title),
                grade_band=raw_data.grade_levels.get(title),
            )

            # Check if this might be an alignment candidate
            if self._is_potential_entry_course(title, item.description):
                item.is_alignment_candidate = True
                item.alignment_candidate_reason = (
                    "Course title/description suggests it may serve as a digital entry experience"
                )

            items.append(item)

        return items

    def _is_potential_entry_course(
        self, title: str, description: Optional[str]
    ) -> bool:
        """Check if a course might be an existing entry/foundations course.

        Args:
            title: Course title
            description: Course description

        Returns:
            True if this appears to be an entry-level foundations course
        """
        title_lower = title.lower()

        # Keywords suggesting entry-level foundations course
        entry_keywords = [
            "foundations",
            "introduction",
            "intro to",
            "fundamentals",
            "essentials",
            "basics",
            "principles",
            "exploring",
            "discovery",
        ]

        # Scope keywords suggesting broad digital coverage
        scope_keywords = [
            "digital",
            "computing",
            "technology",
            "computer",
            "information",
        ]

        has_entry_keyword = any(kw in title_lower for kw in entry_keywords)
        has_scope_keyword = any(kw in title_lower for kw in scope_keywords)

        if has_entry_keyword and has_scope_keyword:
            return True

        # Check description if available
        if description:
            desc_lower = description.lower()
            # Look for broad coverage indicators
            topics_mentioned = sum(
                1
                for topic in ["programming", "networking", "data", "security", "ai"]
                if topic in desc_lower
            )
            if topics_mentioned >= 3:
                return True

        return False

    def filter_digital_courses(
        self, items: List[CourseInventoryItem]
    ) -> List[CourseInventoryItem]:
        """Filter inventory to only digital/technical CTE courses.

        Args:
            items: List of course inventory items

        Returns:
            Filtered list containing only digital/technical courses
        """
        filtered = []

        for item in items:
            title_lower = item.title.lower()

            # Check exclusion patterns
            if any(re.match(pattern, title_lower) for pattern in EXCLUDE_PATTERNS):
                continue

            # Check for digital keywords
            has_keyword = any(kw.lower() in title_lower for kw in DIGITAL_KEYWORDS)

            if not has_keyword and item.description:
                desc_lower = item.description.lower()
                has_keyword = any(kw.lower() in desc_lower for kw in DIGITAL_KEYWORDS)

            if has_keyword:
                filtered.append(item)

        return filtered
