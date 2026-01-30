"""
Main analyzer that orchestrates the analysis pipeline.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from district_pathway_analyzer.alignment import AlignmentAnalyzer
from district_pathway_analyzer.config import get_config
from district_pathway_analyzer.design import PathwayDesignEngine
from district_pathway_analyzer.discovery import (
    CourseExtractor,
    DiscoveryGate,
    DistrictDiscoverer,
    SourceValidator,
)
from district_pathway_analyzer.landscape import LandscapeModeler
from district_pathway_analyzer.models import (
    CourseInventory,
    DistrictAnalysisReport,
    DistrictInput,
    PipelineStatus,
)
from district_pathway_analyzer.report import ReportGenerator
from district_pathway_analyzer.tagging import DomainTagger

logger = logging.getLogger(__name__)


class DistrictPathwayAnalyzer:
    """Main analyzer for district CTE pathway analysis."""

    def __init__(self):
        """Initialize the analyzer with all components."""
        self.config = get_config()
        self.discoverer = DistrictDiscoverer()
        self.extractor = CourseExtractor()
        self.tagger = DomainTagger()
        self.landscape_modeler = LandscapeModeler()
        self.alignment_analyzer = AlignmentAnalyzer()
        self.design_engine = PathwayDesignEngine()
        self.report_generator = ReportGenerator()

    def analyze(
        self,
        district_name: str,
        state: str,
        documents: Optional[List[str]] = None,
        urls: Optional[List[str]] = None,
    ) -> DistrictAnalysisReport:
        """Run the full analysis pipeline for a district.

        Args:
            district_name: Name of the school district
            state: State name or abbreviation
            documents: Optional list of local document paths
            urls: Optional list of URLs to analyze

        Returns:
            DistrictAnalysisReport with complete analysis
        """
        logger.info(f"Starting analysis for {district_name}, {state}")

        # Create input
        district_input = DistrictInput(
            district_name=district_name,
            state=state,
            user_provided_urls=urls or [],
        )

        # Initialize report
        report = DistrictAnalysisReport(
            district_name=district_name,
            state=state,
            input_data=district_input,
            pipeline_status=PipelineStatus.FAILED,
            current_phase="discovery",
        )

        try:
            # Phase 0: Discovery & Validation
            logger.info("Phase 0: Discovery & Validation")
            inventory = self._run_discovery(district_input, documents, report)

            if not inventory or not report.discovery_gate.passed:
                logger.warning("Discovery gate failed")
                report.errors.append("Discovery gate failed - insufficient data")
                return report

            report.current_phase = "tagging"

            # Phase 1: Domain Tagging
            logger.info("Phase 1: Domain Tagging")
            tagged_courses = self.tagger.tag_courses(inventory.courses)
            domain_coverage = self.tagger.analyze_coverage(tagged_courses)

            report.current_phase = "landscape"

            # Phase 2: Landscape Modeling (Layer 1)
            logger.info("Phase 2: Landscape Modeling")
            landscape = self.landscape_modeler.model_landscape(
                district_name=district_name,
                state=state,
                courses=tagged_courses,
                domain_coverage=domain_coverage,
            )
            report.landscape = landscape

            report.current_phase = "alignment"

            # Phase 3: Alignment Analysis (Layer 2)
            logger.info("Phase 3: Alignment Analysis")
            alignment = self.alignment_analyzer.analyze(landscape)
            report.alignment = alignment

            report.current_phase = "design"

            # Phase 4: Pathway Design (Layer 3)
            logger.info("Phase 4: Pathway Design")
            design = self.design_engine.design(landscape, alignment)
            report.design = design

            # Mark success
            report.pipeline_status = PipelineStatus.SUCCESS
            report.current_phase = "complete"

            logger.info(f"Analysis complete for {district_name}")

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            report.errors.append(str(e))
            report.pipeline_status = PipelineStatus.FAILED

        return report

    def _run_discovery(
        self,
        district_input: DistrictInput,
        documents: Optional[List[str]],
        report: DistrictAnalysisReport,
    ) -> Optional[CourseInventory]:
        """Run the discovery phase.

        Args:
            district_input: The district input
            documents: Optional local documents
            report: The report to update

        Returns:
            CourseInventory or None if discovery fails
        """
        inventory = CourseInventory()

        # Process local documents first
        if documents:
            for doc_path in documents:
                try:
                    raw_data = self.extractor.extract_from_file(doc_path)
                    courses = self.extractor.raw_to_inventory(raw_data)
                    courses = self.extractor.filter_digital_courses(courses)
                    inventory.courses.extend(courses)
                    logger.info(f"Extracted {len(courses)} courses from {doc_path}")
                except Exception as e:
                    logger.error(f"Failed to extract from {doc_path}: {e}")
                    report.warnings.append(f"Failed to process document: {doc_path}")

        # Discover and process URLs
        if district_input.user_provided_urls or not documents:
            with self.discoverer as discoverer:
                sources = discoverer.discover_sources(district_input)
                report.sources = sources

                # Validate sources
                validator = SourceValidator(district_input.district_name)
                valid_sources = []
                for source in sources:
                    validation = validator.validate(source)
                    source.is_valid = validation.valid
                    source.confidence = validation.confidence
                    source.validation_reason = validation.reason
                    if validation.valid:
                        valid_sources.append(source)

                # Extract from valid sources
                for source in valid_sources:
                    try:
                        content = discoverer.fetch_content(source)
                        if content:
                            raw_data = self.extractor.extract_from_source(source, content)
                            courses = self.extractor.raw_to_inventory(raw_data)
                            courses = self.extractor.filter_digital_courses(courses)
                            inventory.courses.extend(courses)
                            inventory.sources.append(source)
                            logger.info(f"Extracted {len(courses)} courses from {source.url}")
                    except Exception as e:
                        logger.error(f"Failed to extract from {source.url}: {e}")
                        report.warnings.append(f"Failed to process source: {source.url}")

        # Deduplicate courses by title
        seen_titles = set()
        unique_courses = []
        for course in inventory.courses:
            if course.title.lower() not in seen_titles:
                seen_titles.add(course.title.lower())
                unique_courses.append(course)
        inventory.courses = unique_courses

        # Check discovery gate
        gate = DiscoveryGate()
        gate_result = gate.check(inventory)
        report.discovery_gate = gate_result

        if not gate_result.passed:
            failure_msg = gate.generate_failure_message(gate_result)
            logger.warning(failure_msg)
            report.warnings.append(failure_msg)

        return inventory if gate_result.passed else None

    def generate_report(
        self,
        report: DistrictAnalysisReport,
        output_path: str,
        format: str = "markdown",
    ) -> str:
        """Generate a report from analysis results.

        Args:
            report: The analysis report
            output_path: Path for the output file
            format: Output format ('markdown', 'pdf', 'json')

        Returns:
            Path to the generated report
        """
        return self.report_generator.generate(report, output_path, format)

    def close(self):
        """Clean up resources."""
        self.discoverer.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
