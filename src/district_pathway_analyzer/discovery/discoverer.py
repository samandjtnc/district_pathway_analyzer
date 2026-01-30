"""
Source discovery for finding district CTE course information.
"""

import json
import logging
from datetime import datetime
from typing import List, Optional
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from district_pathway_analyzer.config import get_config
from district_pathway_analyzer.llm_client import get_llm_client
from district_pathway_analyzer.models import (
    DistrictInput,
    Source,
    SourceType,
)

logger = logging.getLogger(__name__)


class DistrictDiscoverer:
    """Discovers sources of CTE course information for a district."""

    # Search query templates
    SEARCH_QUERIES = [
        "{district_name} {state} CTE course catalog PDF",
        "{district_name} {state} Programs of Study",
        "{district_name} {state} career technical education courses",
        "{district_name} high school course offerings computer science",
        "{district_name} {state} CTE pathways digital technology",
    ]

    def __init__(self):
        """Initialize the discoverer."""
        self.config = get_config()
        self.llm = get_llm_client()
        self.http_client = httpx.Client(
            timeout=self.config.discovery.timeout_seconds,
            follow_redirects=True,
        )

    def discover_sources(self, district_input: DistrictInput) -> List[Source]:
        """Discover sources for a district.

        Args:
            district_input: The district input specification

        Returns:
            List of discovered sources
        """
        sources = []

        # First, add any user-provided URLs
        for url in district_input.user_provided_urls:
            source = self._create_source_from_url(url)
            if source:
                sources.append(source)
                logger.info(f"Added user-provided source: {url}")

        # If we have user-provided sources, we may skip auto-discovery
        if sources and len(sources) >= 2:
            logger.info("Sufficient user-provided sources, skipping auto-discovery")
            return sources

        # Perform automated web search for additional sources
        discovered = self._search_for_sources(
            district_input.district_name, district_input.state
        )
        sources.extend(discovered)

        # Deduplicate by URL
        seen_urls = set()
        unique_sources = []
        for source in sources:
            if source.url not in seen_urls:
                seen_urls.add(source.url)
                unique_sources.append(source)

        return unique_sources

    def _search_for_sources(self, district_name: str, state: str) -> List[Source]:
        """Search the web for district CTE sources.

        Args:
            district_name: Name of the district
            state: State name or abbreviation

        Returns:
            List of discovered sources
        """
        sources = []

        # Generate search queries
        queries = [
            q.format(district_name=district_name, state=state)
            for q in self.SEARCH_QUERIES
        ]

        # Use LLM to help identify likely domain patterns
        district_domain = self._infer_district_domain(district_name, state)

        for query in queries:
            try:
                # In MVP, we simulate search with direct URL construction
                # Full implementation would use search API
                potential_urls = self._construct_potential_urls(
                    district_name, state, district_domain
                )
                for url in potential_urls:
                    source = self._create_source_from_url(url)
                    if source:
                        sources.append(source)
            except Exception as e:
                logger.warning(f"Search failed for query '{query}': {e}")

        return sources

    def _infer_district_domain(self, district_name: str, state: str) -> Optional[str]:
        """Use LLM to infer likely district domain.

        Args:
            district_name: Name of the district
            state: State name or abbreviation

        Returns:
            Likely domain pattern or None
        """
        prompt = f"""Given the school district "{district_name}" in {state}, what is the most likely
official website domain?

Common patterns:
- {district_name.lower().replace(' ', '')}.k12.{state.lower()}.us
- {district_name.lower().replace(' ', '')}schools.org
- {district_name.lower().replace(' ', '')}.schoolwires.net

Return only the domain, nothing else. If uncertain, return the most common pattern."""

        try:
            response = self.llm.complete(prompt, temperature=0.0)
            domain = response.strip().lower()
            # Basic validation
            if "." in domain and len(domain) < 100:
                return domain
        except Exception as e:
            logger.warning(f"Failed to infer domain: {e}")

        return None

    def _construct_potential_urls(
        self, district_name: str, state: str, domain: Optional[str]
    ) -> List[str]:
        """Construct potential URLs for district CTE information.

        Args:
            district_name: Name of the district
            state: State name or abbreviation
            domain: Inferred district domain

        Returns:
            List of potential URLs to check
        """
        urls = []

        if domain:
            # Common CTE page patterns
            patterns = [
                f"https://{domain}/cte",
                f"https://{domain}/academics/cte",
                f"https://{domain}/departments/cte",
                f"https://{domain}/programs-of-study",
                f"https://{domain}/career-technical-education",
                f"https://www.{domain}/cte",
                f"https://www.{domain}/academics/cte",
            ]
            urls.extend(patterns)

        return urls

    def _create_source_from_url(self, url: str) -> Optional[Source]:
        """Create a Source object from a URL after validation.

        Args:
            url: The URL to process

        Returns:
            Source object or None if URL is invalid
        """
        try:
            # Validate URL format
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return None

            # Determine source type
            source_type = self._determine_source_type(url)

            # Try to fetch and validate
            response = self.http_client.head(url)
            if response.status_code == 200:
                return Source(
                    url=url,
                    source_type=source_type,
                    confidence=0.7,  # Default confidence
                    date_accessed=datetime.now().isoformat(),
                    is_valid=True,
                )
            elif response.status_code in [301, 302, 307, 308]:
                # Follow redirect
                redirect_url = response.headers.get("location")
                if redirect_url:
                    return self._create_source_from_url(redirect_url)

        except Exception as e:
            logger.warning(f"Failed to validate URL {url}: {e}")

        return None

    def _determine_source_type(self, url: str) -> SourceType:
        """Determine the source type from URL.

        Args:
            url: The URL to analyze

        Returns:
            SourceType enum value
        """
        url_lower = url.lower()
        if url_lower.endswith(".pdf"):
            return SourceType.PDF
        elif url_lower.endswith((".doc", ".docx")):
            return SourceType.DOCUMENT
        else:
            return SourceType.HTML

    def fetch_content(self, source: Source) -> Optional[str]:
        """Fetch content from a source URL.

        Args:
            source: The source to fetch

        Returns:
            Content as string or None if fetch fails
        """
        try:
            response = self.http_client.get(source.url)
            response.raise_for_status()

            if source.source_type == SourceType.HTML:
                return response.text
            elif source.source_type == SourceType.PDF:
                # Return raw bytes for PDF processing
                return response.content
            else:
                return response.text

        except Exception as e:
            logger.error(f"Failed to fetch content from {source.url}: {e}")
            return None

    def close(self):
        """Close the HTTP client."""
        self.http_client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
