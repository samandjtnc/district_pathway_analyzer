"""
Report generation for analysis results.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from district_pathway_analyzer.config import get_config
from district_pathway_analyzer.models import (
    CourseInventoryItem,
    DistrictAnalysisReport,
    DownstreamRelationship,
)

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates reports from analysis results."""

    def __init__(self):
        """Initialize the report generator."""
        self.config = get_config()

    def generate(
        self,
        report: DistrictAnalysisReport,
        output_path: str,
        format: str = "markdown",
    ) -> str:
        """Generate a report in the specified format.

        Args:
            report: The analysis report
            output_path: Path to write the report
            format: Output format ('markdown', 'pdf', 'json')

        Returns:
            Path to the generated report
        """
        if format == "markdown":
            return self._generate_markdown(report, output_path)
        elif format == "json":
            return self._generate_json(report, output_path)
        elif format == "pdf":
            return self._generate_pdf(report, output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _generate_markdown(
        self, report: DistrictAnalysisReport, output_path: str
    ) -> str:
        """Generate a Markdown report.

        Args:
            report: The analysis report
            output_path: Path to write the report

        Returns:
            Path to the generated report
        """
        content = self._build_markdown_content(report)

        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Generated Markdown report: {output_path}")
        return output_path

    def _generate_json(
        self, report: DistrictAnalysisReport, output_path: str
    ) -> str:
        """Generate a JSON report.

        Args:
            report: The analysis report
            output_path: Path to write the report

        Returns:
            Path to the generated report
        """
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report.model_dump_json(indent=2))

        logger.info(f"Generated JSON report: {output_path}")
        return output_path

    def _generate_pdf(
        self, report: DistrictAnalysisReport, output_path: str
    ) -> str:
        """Generate a PDF report.

        Args:
            report: The analysis report
            output_path: Path to write the report

        Returns:
            Path to the generated report
        """
        try:
            from weasyprint import HTML

            # First generate markdown
            markdown_content = self._build_markdown_content(report)

            # Convert markdown to HTML
            import markdown

            html_content = markdown.markdown(
                markdown_content,
                extensions=["tables", "fenced_code"],
            )

            # Wrap in HTML document with styling
            full_html = self._wrap_html(html_content, report.district_name)

            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            # Generate PDF
            HTML(string=full_html).write_pdf(output_path)

            logger.info(f"Generated PDF report: {output_path}")
            return output_path

        except ImportError:
            logger.warning("WeasyPrint not available, falling back to markdown")
            md_path = output_path.replace(".pdf", ".md")
            return self._generate_markdown(report, md_path)

    def _build_markdown_content(self, report: DistrictAnalysisReport) -> str:
        """Build the markdown content for the report.

        Args:
            report: The analysis report

        Returns:
            Markdown content string
        """
        sections = []

        # Title
        sections.append(f"# District Digital Technology Pathway Analysis")
        sections.append(f"## {report.district_name}, {report.state}")
        sections.append("")
        sections.append(f"**Generated:** {report.generated_date}")
        sections.append(f"**Status:** {report.pipeline_status.value.title()}")
        sections.append("")
        sections.append("---")
        sections.append("")

        # Executive Summary
        sections.append("## EXECUTIVE SUMMARY")
        sections.append("")
        sections.append(self._build_executive_summary(report))
        sections.append("")
        sections.append("---")
        sections.append("")

        # Section 1: Current Landscape
        if report.landscape:
            sections.append("## 1. CURRENT DIGITAL TECHNOLOGY LANDSCAPE")
            sections.append("")
            sections.append(self._build_landscape_section(report))
            sections.append("")
            sections.append("---")
            sections.append("")

        # Section 2: Alignment Analysis
        if report.alignment:
            sections.append("## 2. ALIGNMENT TO DIGITAL TECHNOLOGY CROSS-CUTTING CLUSTER")
            sections.append("")
            sections.append(self._build_alignment_section(report))
            sections.append("")
            sections.append("---")
            sections.append("")

        # Section 3: Recommendations
        if report.design:
            sections.append("## 3. DESIGNED ENTRY-POINT RECOMMENDATION")
            sections.append("")
            sections.append(self._build_design_section(report))
            sections.append("")
            sections.append("---")
            sections.append("")

        # Section 4: Value Proposition
        if report.design:
            sections.append("## 4. DISTRICT-FACING VALUE PROPOSITION")
            sections.append("")
            sections.append(self._build_value_proposition(report))
            sections.append("")
            sections.append("---")
            sections.append("")

        # Section 5: Implementation Considerations
        if report.design:
            sections.append("## 5. IMPLEMENTATION CONSIDERATIONS")
            sections.append("")
            sections.append(self._build_implementation_section(report))
            sections.append("")
            sections.append("---")
            sections.append("")

        # Appendix A: Course Inventory
        if report.landscape:
            sections.append("## APPENDIX A: COURSE & PATHWAY INVENTORY")
            sections.append("")
            sections.append(self._build_inventory_table(report))
            sections.append("")
            sections.append("---")
            sections.append("")

        # Appendix B: Design Confidence
        if report.design:
            sections.append("## APPENDIX B: DESIGN CONFIDENCE & CAVEATS")
            sections.append("")
            sections.append(self._build_confidence_section(report))
            sections.append("")
            sections.append("---")
            sections.append("")

        # Appendix C: About AI Foundations
        sections.append("## APPENDIX C: ABOUT AI FOUNDATIONS")
        sections.append("")
        sections.append(self._build_aif_section())
        sections.append("")

        return "\n".join(sections)

    def _build_executive_summary(self, report: DistrictAnalysisReport) -> str:
        """Build the executive summary section."""
        parts = []

        if report.pipeline_status.value == "failed":
            parts.append("**Analysis Status:** Incomplete")
            parts.append("")
            if report.errors:
                parts.append("**Issues Encountered:**")
                for error in report.errors:
                    parts.append(f"- {error}")
            return "\n".join(parts)

        # Successful analysis
        if report.landscape:
            parts.append(f"**Courses Identified:** {len(report.landscape.course_inventory)}")
            parts.append(f"**Pathway Shape:** {report.landscape.pathway_shape.value.title()}")
            parts.append(f"**Entry Point:** {report.landscape.entry_point_analysis.current_entry_course or 'Not identified'}")
            parts.append("")

        if report.design:
            parts.append(f"**Recommended Strategy:** {report.design.strategy.value.replace('_', ' ').title()}")
            parts.append(f"**AI Foundations Role:** {report.design.aif_role.value.replace('_', ' ').title()}")
            parts.append(f"**Design Confidence:** {report.design.design_confidence.title()}")
            parts.append("")
            parts.append("**Summary:**")
            parts.append(report.design.design_narrative)

        return "\n".join(parts)

    def _build_landscape_section(self, report: DistrictAnalysisReport) -> str:
        """Build the landscape analysis section."""
        parts = []
        landscape = report.landscape

        parts.append(f"**Entry Point:** {landscape.entry_point_analysis.current_entry_course or 'Not identified'}")
        parts.append(f"**Entry Timing:** {landscape.entry_point_analysis.entry_timing.title()}")
        parts.append(f"**Entry Breadth:** {landscape.entry_point_analysis.entry_breadth.title()}")
        parts.append("")
        parts.append(f"**Pathway Shape:** {landscape.pathway_shape.value.title()}")
        parts.append(f"**Pathways Identified:** {landscape.pathway_count}")
        if landscape.identified_pathways:
            parts.append(f"- {', '.join(landscape.identified_pathways)}")
        parts.append("")
        parts.append(f"**Domain Coverage:** {landscape.domain_coverage.coverage_pattern.value.title()}")
        if landscape.domain_coverage.dominant_domain:
            parts.append(f"**Dominant Domain:** {landscape.domain_coverage.dominant_domain}")
        parts.append("")
        parts.append("### Landscape Summary")
        parts.append("")
        parts.append(landscape.landscape_summary)

        return "\n".join(parts)

    def _build_alignment_section(self, report: DistrictAnalysisReport) -> str:
        """Build the alignment analysis section."""
        parts = []
        alignment = report.alignment
        profile = alignment.alignment_profile

        parts.append("### Alignment Profile")
        parts.append("")
        parts.append(f"| Dimension | Assessment |")
        parts.append(f"|-----------|------------|")
        parts.append(f"| Entry Timing | {profile.entry_timing.value.replace('_', ' ').title()} |")
        parts.append(f"| Specialization Pattern | {profile.specialization_pattern.value.replace('_', ' ').title()} |")
        parts.append(f"| Domain Balance | {profile.domain_balance.value.title()} |")
        parts.append(f"| Pathway Coherence | {profile.pathway_coherence.value.replace('_', ' ').title()} |")
        parts.append(f"| Choice Architecture | {profile.choice_architecture.value.replace('_', ' ').title()} |")
        parts.append(f"| AI Integration | {profile.ai_integration.value.replace('_', ' ').title()} |")
        parts.append("")

        parts.append("### Alignment Narrative")
        parts.append("")
        parts.append(alignment.alignment_narrative)
        parts.append("")

        if alignment.opportunity_signals.opportunities:
            parts.append("### Opportunities Identified")
            parts.append("")
            for opp in alignment.opportunity_signals.opportunities:
                parts.append(f"- {opp}")
            parts.append("")

        if alignment.opportunity_signals.risk_flags:
            parts.append("### Risk Considerations")
            parts.append("")
            for risk in alignment.opportunity_signals.risk_flags:
                parts.append(f"- {risk}")

        return "\n".join(parts)

    def _build_design_section(self, report: DistrictAnalysisReport) -> str:
        """Build the pathway design section."""
        parts = []
        design = report.design

        parts.append(f"**Strategy:** {design.strategy.value.replace('_', ' ').title()}")
        parts.append("")

        if design.existing_course_to_align:
            parts.append(f"**Existing Course for Alignment:** {design.existing_course_to_align}")
            parts.append("")

        parts.append("### Proposed Structure")
        parts.append("")
        parts.append(f"- **Role:** {design.aif_role.value.replace('_', ' ').title()}")
        parts.append(f"- **Grade Band:** {design.design_variables.grade_band}")
        parts.append(f"- **Credit Framing:** {design.design_variables.credit_framing}")
        parts.append(f"- **Entry Strength:** {design.design_variables.entry_strength.title()}")
        parts.append("")

        parts.append("### Design Narrative")
        parts.append("")
        parts.append(design.design_narrative)
        parts.append("")

        if design.downstream_pathways:
            parts.append("### Downstream Pathway View")
            parts.append("")
            parts.append("| Pathway | Courses | Relationship |")
            parts.append("|---------|---------|--------------|")
            for dp in design.downstream_pathways:
                courses = ", ".join(dp.courses[:3]) if dp.courses else "-"
                if len(dp.courses) > 3:
                    courses += "..."
                rel = dp.relationship.value.replace("_", " ").title()
                parts.append(f"| {dp.name} | {courses} | {rel} |")

        return "\n".join(parts)

    def _build_value_proposition(self, report: DistrictAnalysisReport) -> str:
        """Build the district-facing value proposition."""
        parts = []
        design = report.design

        emphasis = design.design_variables.narrative_emphasis

        if emphasis == "access":
            parts.append("### Opening Doors to Digital Futures")
            parts.append("")
            parts.append(
                "AI Foundations provides all students with an accessible entry point "
                "to explore digital technology pathways. With no prerequisites required, "
                "students can discover their interests across computing, AI, data, and "
                "cybersecurity before committing to a specialization."
            )
        elif emphasis == "coherence":
            parts.append("### Clarifying the Digital Pathway Structure")
            parts.append("")
            parts.append(
                "AI Foundations brings coherence to the digital pathway options by "
                "providing a shared foundation across Computer Science, IT, and Digital Media. "
                "Students gain clarity on how different pathways connect and can make "
                "informed choices about their specialization."
            )
        else:  # connection
            parts.append("### Connecting Students to Multiple Futures")
            parts.append("")
            parts.append(
                "AI Foundations serves as a bridge connecting students to multiple "
                "digital career pathways. Rather than requiring early specialization, "
                "students explore the breadth of digital technology before choosing "
                "their focus area."
            )

        parts.append("")
        parts.append("**Key Benefits:**")
        parts.append("- Entry-level course accessible to all students (no prerequisites)")
        parts.append("- Covers AI, programming, data, networks, and cybersecurity")
        parts.append("- Prepares students for multiple downstream pathways")
        parts.append("- Aligns with national Digital Technology career cluster framework")

        return "\n".join(parts)

    def _build_implementation_section(self, report: DistrictAnalysisReport) -> str:
        """Build the implementation considerations section."""
        parts = []
        design = report.design

        parts.append("### Recommended Next Steps")
        parts.append("")

        if design.strategy.value == "align_existing":
            parts.append(f"1. Review curriculum alignment with '{design.existing_course_to_align}' instructor")
            parts.append("2. Compare existing syllabus with AI Foundations content")
            parts.append("3. Develop phased transition plan")
            parts.append("4. Plan professional development for curriculum adoption")
        elif design.strategy.value == "hybrid":
            parts.append(f"1. Discuss integration approach with '{design.existing_course_to_align}' instructor")
            parts.append("2. Identify content gaps and overlaps")
            parts.append("3. Develop complementary curriculum structure")
            parts.append("4. Plan coordinated implementation")
        else:  # position_new
            parts.append("1. Present pathway design to CTE coordinator/director")
            parts.append("2. Identify instructor for AI Foundations course")
            parts.append("3. Determine course scheduling and catalog placement")
            parts.append("4. Develop communication plan for students and counselors")

        parts.append("")
        parts.append("### Validation Needed")
        parts.append("")
        if design.validation_needed:
            for v in design.validation_needed:
                parts.append(f"- {v}")
        else:
            parts.append("- Verify course inventory with district CTE coordinator")
            parts.append("- Confirm pathway structure accuracy")

        return "\n".join(parts)

    def _build_inventory_table(self, report: DistrictAnalysisReport) -> str:
        """Build the course inventory table."""
        parts = []
        courses = report.landscape.course_inventory

        parts.append("| Course Title | Domain (Primary) | Domain (Secondary) | Role | Confidence |")
        parts.append("|--------------|------------------|-------------------|------|------------|")

        for course in courses:
            primary = course.domain_tags.primary if course.domain_tags else "-"
            secondary = ", ".join(course.domain_tags.secondary) if course.domain_tags and course.domain_tags.secondary else "-"
            role = course.role.value if course.role else "-"
            confidence = course.confidence.value

            # Truncate long titles
            title = course.title
            if len(title) > 40:
                title = title[:37] + "..."

            parts.append(f"| {title} | {primary} | {secondary} | {role} | {confidence} |")

        return "\n".join(parts)

    def _build_confidence_section(self, report: DistrictAnalysisReport) -> str:
        """Build the confidence and caveats section."""
        parts = []
        design = report.design

        parts.append(f"**Overall Design Confidence:** {design.design_confidence.title()}")
        parts.append("")

        if design.assumptions:
            parts.append("### Assumptions Made")
            parts.append("")
            for assumption in design.assumptions:
                parts.append(f"- {assumption}")
            parts.append("")

        if design.validation_needed:
            parts.append("### Validation Needed")
            parts.append("")
            for validation in design.validation_needed:
                parts.append(f"- {validation}")
            parts.append("")

        # Invariant status
        parts.append("### Design Invariant Status")
        parts.append("")
        invariants = design.invariants
        parts.append(f"- AI Foundations as entry experience: {'✓' if invariants.aif_is_entry else '✗'}")
        parts.append(f"- Downstream pathways intact: {'✓' if invariants.downstream_intact else '✗'}")
        parts.append(f"- Reduces cognitive load: {'✓' if invariants.reduces_cognitive_load else '✗'}")
        parts.append(f"- Aligns with cross-cutting nature: {'✓' if invariants.aligns_cross_cutting else '✗'}")
        parts.append(f"- Two-minute explainable: {'✓' if invariants.two_minute_explainable else '✗'}")

        return "\n".join(parts)

    def _build_aif_section(self) -> str:
        """Build the AI Foundations information section."""
        parts = []

        parts.append("### AI Foundations Curriculum Overview")
        parts.append("")
        parts.append("**Course Name:** AI Foundations")
        parts.append("**Grade Level:** 9-10")
        parts.append("**Prerequisites:** None required")
        parts.append("**Credit Type:** CTE or Academic")
        parts.append("**Duration:** Full year (2 semesters)")
        parts.append("")
        parts.append("**Key Topics:**")
        parts.append("1. Problem Solving with AI")
        parts.append("2. Foundations of AI Programming (Python)")
        parts.append("3. AI and the Systems That Power It")
        parts.append("4. The Fabric of the Internet and AI")
        parts.append("5. AI-Powered Threats and Defenses")
        parts.append("6. Insights from Data and AI")
        parts.append("")
        parts.append(
            "**Positioning:** Entry-level course accessible to beginners with no prior "
            "CS experience. Bridges to AP Computer Science A and other specialized pathways."
        )

        return "\n".join(parts)

    def _wrap_html(self, content: str, title: str) -> str:
        """Wrap HTML content in a full document with styling.

        Args:
            content: HTML content
            title: Document title

        Returns:
            Full HTML document
        """
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title} - Pathway Analysis</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1 {{
            color: #1a5f7a;
            border-bottom: 2px solid #1a5f7a;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #2c7da0;
            margin-top: 30px;
        }}
        h3 {{
            color: #468faf;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }}
        th {{
            background-color: #1a5f7a;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
        }}
        blockquote {{
            border-left: 4px solid #2c7da0;
            margin: 0;
            padding-left: 20px;
            color: #555;
        }}
        hr {{
            border: none;
            border-top: 1px solid #ddd;
            margin: 30px 0;
        }}
        .status-success {{
            color: #2e7d32;
        }}
        .status-failed {{
            color: #c62828;
        }}
    </style>
</head>
<body>
{content}
</body>
</html>"""
