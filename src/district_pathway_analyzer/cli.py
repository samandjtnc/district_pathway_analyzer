"""
Command-line interface for the District Pathway Analyzer.
"""

import logging
import sys
from pathlib import Path
from typing import List, Optional

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from district_pathway_analyzer import __version__
from district_pathway_analyzer.analyzer import DistrictPathwayAnalyzer
from district_pathway_analyzer.config import get_config, load_config

# Load environment variables
load_dotenv()

console = Console()


def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )


@click.group()
@click.version_option(version=__version__)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to config file")
@click.pass_context
def cli(ctx, verbose: bool, config: Optional[str]):
    """District Pathway Analyzer - AI-Powered CTE Pathway Analysis Tool.

    Analyze school district CTE programs to identify opportunities for
    integrating Code.org's AI Foundations curriculum.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

    setup_logging(verbose)

    if config:
        load_config(config)


@cli.command()
@click.argument("district_name")
@click.argument("state")
@click.option(
    "--documents",
    "-d",
    multiple=True,
    type=click.Path(exists=True),
    help="Local document files to analyze (PDF, HTML)",
)
@click.option(
    "--urls",
    "-u",
    multiple=True,
    help="URLs to analyze",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["markdown", "pdf", "json"]),
    default="markdown",
    help="Output format",
)
@click.pass_context
def analyze(
    ctx,
    district_name: str,
    state: str,
    documents: tuple,
    urls: tuple,
    output: Optional[str],
    format: str,
):
    """Analyze a school district's CTE pathways.

    DISTRICT_NAME: Name of the school district (e.g., "Johnston County Schools")
    STATE: State name or abbreviation (e.g., "North Carolina" or "NC")

    Examples:
        pathway-analyzer analyze "Johnston County Schools" "North Carolina" -d courses.pdf
        pathway-analyzer analyze "Buncombe County Schools" NC -u https://example.com/cte
    """
    console.print(
        Panel(
            f"[bold blue]District Pathway Analyzer[/bold blue]\n"
            f"Analyzing: {district_name}, {state}",
            title="CTE Analysis",
        )
    )

    # Default output path
    if not output:
        safe_name = district_name.lower().replace(" ", "_")
        output = f"reports/{safe_name}_{state.lower()}_analysis.{format if format != 'pdf' else 'md'}"

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running analysis pipeline...", total=None)

        try:
            with DistrictPathwayAnalyzer() as analyzer:
                progress.update(task, description="Phase 0: Discovery & Validation...")
                report = analyzer.analyze(
                    district_name=district_name,
                    state=state,
                    documents=list(documents) if documents else None,
                    urls=list(urls) if urls else None,
                )

                progress.update(task, description="Generating report...")
                report_path = analyzer.generate_report(report, output, format)

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            if ctx.obj.get("verbose"):
                console.print_exception()
            sys.exit(1)

    # Display results
    console.print()

    if report.pipeline_status.value == "success":
        console.print("[green]Analysis completed successfully[/green]")
    elif report.pipeline_status.value == "partial":
        console.print("[yellow]Analysis completed with warnings[/yellow]")
    else:
        console.print("[red]✗ Analysis failed[/red]")

    # Display summary table
    if report.landscape:
        table = Table(title="Analysis Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Courses Found", str(len(report.landscape.course_inventory)))
        table.add_row("Pathway Shape", report.landscape.pathway_shape.value.title())
        table.add_row(
            "Entry Point",
            report.landscape.entry_point_analysis.current_entry_course or "Not identified",
        )
        table.add_row(
            "Domain Coverage",
            report.landscape.domain_coverage.coverage_pattern.value.title(),
        )

        if report.design:
            table.add_row("Strategy", report.design.strategy.value.replace("_", " ").title())
            table.add_row("Confidence", report.design.design_confidence.title())

        console.print(table)

    # Display warnings
    if report.warnings:
        console.print()
        console.print("[yellow]Warnings:[/yellow]")
        for warning in report.warnings[:5]:  # Show first 5
            console.print(f"  • {warning[:100]}...")

    # Display errors
    if report.errors:
        console.print()
        console.print("[red]Errors:[/red]")
        for error in report.errors:
            console.print(f"  • {error}")

    console.print()
    console.print(f"[green]Report saved to: {report_path}[/green]")


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path for extracted courses",
)
@click.pass_context
def extract(ctx, file_path: str, output: Optional[str]):
    """Extract courses from a document file.

    FILE_PATH: Path to a PDF or HTML document containing course information.

    This command extracts digital/technical CTE courses from a document
    without running the full analysis pipeline.

    Examples:
        pathway-analyzer extract courses.pdf
        pathway-analyzer extract catalog.html -o courses.json
    """
    from district_pathway_analyzer.discovery import CourseExtractor

    console.print(f"[blue]Extracting courses from: {file_path}[/blue]")

    extractor = CourseExtractor()

    try:
        raw_data = extractor.extract_from_file(file_path)
        courses = extractor.raw_to_inventory(raw_data)
        courses = extractor.filter_digital_courses(courses)

        console.print(f"[green]Found {len(courses)} digital/technical courses[/green]")
        console.print()

        # Display courses
        table = Table(title="Extracted Courses")
        table.add_column("Title", style="cyan", max_width=50)
        table.add_column("Description", style="white", max_width=40)
        table.add_column("Confidence", style="yellow")

        for course in courses:
            desc = course.description[:40] + "..." if course.description and len(course.description) > 40 else (course.description or "-")
            table.add_row(course.title, desc, course.confidence.value)

        console.print(table)

        # Save if output specified
        if output:
            import json

            with open(output, "w") as f:
                json.dump(
                    [c.model_dump() for c in courses],
                    f,
                    indent=2,
                    default=str,
                )
            console.print(f"[green]Saved to: {output}[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument("report_path", type=click.Path(exists=True))
@click.option(
    "--format",
    "-f",
    type=click.Choice(["markdown", "pdf"]),
    default="pdf",
    help="Output format",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path",
)
@click.pass_context
def convert(ctx, report_path: str, format: str, output: Optional[str]):
    """Convert a JSON report to another format.

    REPORT_PATH: Path to a JSON analysis report.

    Examples:
        pathway-analyzer convert report.json -f pdf
        pathway-analyzer convert report.json -f markdown -o summary.md
    """
    import json

    from district_pathway_analyzer.models import DistrictAnalysisReport
    from district_pathway_analyzer.report import ReportGenerator

    console.print(f"[blue]Converting report: {report_path}[/blue]")

    try:
        with open(report_path, "r") as f:
            data = json.load(f)

        report = DistrictAnalysisReport(**data)

        if not output:
            base = Path(report_path).stem
            ext = "pdf" if format == "pdf" else "md"
            output = f"{base}.{ext}"

        generator = ReportGenerator()
        result_path = generator.generate(report, output, format)

        console.print(f"[green]Converted to: {result_path}[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.pass_context
def config(ctx):
    """Display current configuration."""
    cfg = get_config()

    console.print(Panel("[bold]Current Configuration[/bold]"))

    table = Table()
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("LLM Provider", cfg.llm.provider)
    table.add_row("LLM Model", cfg.llm.model)
    table.add_row("Max Tokens", str(cfg.llm.max_tokens))
    table.add_row("Temperature", str(cfg.llm.temperature))
    table.add_row("Discovery Timeout", f"{cfg.discovery.timeout_seconds}s")
    table.add_row("Cache Enabled", str(cfg.discovery.cache_enabled))
    table.add_row("Min Courses", str(cfg.gates.min_courses_found))
    table.add_row("Min Verified %", f"{cfg.gates.min_verified_percentage:.0%}")
    table.add_row("Default Output Format", cfg.output.default_format)

    console.print(table)


def main():
    """Main entry point."""
    cli(obj={})


if __name__ == "__main__":
    main()
