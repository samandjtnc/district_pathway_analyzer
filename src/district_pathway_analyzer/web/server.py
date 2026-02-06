"""
FastAPI server for the District Pathway Analyzer web interface.
"""

import logging
import os
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import uvicorn
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from district_pathway_analyzer.analyzer import DistrictPathwayAnalyzer
from district_pathway_analyzer.models import PipelineStatus
from district_pathway_analyzer.report.generator import ReportGenerator
from district_pathway_analyzer.report.pathway_comparison import PathwayComparisonGenerator

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="District Pathway Analyzer",
    description="AI-Powered CTE Pathway Analysis Tool",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store for analysis jobs (in production, use Redis or database)
analysis_jobs: Dict[str, dict] = {}

# Get the directory containing this file
WEB_DIR = Path(__file__).parent
STATIC_DIR = WEB_DIR / "static"
TEMPLATES_DIR = WEB_DIR / "templates"

# Reports directory (outside of package, in working directory)
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class AnalysisRequest(BaseModel):
    """Request model for analysis."""

    district_name: str
    state: str


class AnalysisStatus(BaseModel):
    """Status of an analysis job."""

    job_id: str
    status: str  # "pending", "running", "completed", "failed"
    progress: str
    result: Optional[dict] = None
    error: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main page."""
    index_path = TEMPLATES_DIR / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text())
    return HTMLResponse(content="<h1>District Pathway Analyzer</h1><p>Template not found</p>")


@app.post("/api/analyze")
async def start_analysis(
    background_tasks: BackgroundTasks,
    district_name: str = Form(...),
    state: str = Form(...),
    document: Optional[UploadFile] = File(None),
):
    """Start a new analysis job."""
    job_id = str(uuid.uuid4())

    # Initialize job status
    analysis_jobs[job_id] = {
        "status": "pending",
        "progress": "Initializing...",
        "result": None,
        "error": None,
        "created_at": datetime.now().isoformat(),
    }

    # Save uploaded file if provided
    doc_path = None
    if document and document.filename:
        # Create temp file
        suffix = Path(document.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await document.read()
            tmp.write(content)
            doc_path = tmp.name
        logger.info(f"Saved uploaded document to {doc_path}")

    # Run analysis in background
    background_tasks.add_task(
        run_analysis_task, job_id, district_name, state, doc_path
    )

    return {"job_id": job_id, "status": "pending"}


def run_analysis_task(
    job_id: str,
    district_name: str,
    state: str,
    doc_path: Optional[str],
):
    """Run the analysis task in the background."""
    try:
        analysis_jobs[job_id]["status"] = "running"
        analysis_jobs[job_id]["progress"] = "Starting analysis..."

        # Run the analyzer
        with DistrictPathwayAnalyzer() as analyzer:
            analysis_jobs[job_id]["progress"] = "Phase 0: Discovery & Validation..."

            documents = [doc_path] if doc_path else None
            report = analyzer.analyze(
                district_name=district_name,
                state=state,
                documents=documents,
            )

            # Convert report to dict for JSON serialization
            result = {
                "district_name": report.district_name,
                "state": report.state,
                "generated_date": report.generated_date,
                "pipeline_status": report.pipeline_status.value,
                "warnings": report.warnings,
                "errors": report.errors,
            }

            if report.landscape:
                result["landscape"] = {
                    "course_count": len(report.landscape.course_inventory),
                    "pathway_shape": report.landscape.pathway_shape.value,
                    "pathway_count": report.landscape.pathway_count,
                    "identified_pathways": report.landscape.identified_pathways,
                    "landscape_summary": report.landscape.landscape_summary,
                    "entry_point": {
                        "course": report.landscape.entry_point_analysis.current_entry_course,
                        "timing": report.landscape.entry_point_analysis.entry_timing,
                        "breadth": report.landscape.entry_point_analysis.entry_breadth,
                    },
                    "domain_coverage": {
                        "pattern": report.landscape.domain_coverage.coverage_pattern.value,
                        "domains": report.landscape.domain_coverage.domains_present,
                        "gaps": report.landscape.domain_coverage.gaps,
                    },
                    "courses": [
                        {
                            "title": c.title,
                            "domain": c.domain_tags.primary if c.domain_tags else None,
                            "role": c.role.value if c.role else None,
                            "confidence": c.confidence.value,
                        }
                        for c in report.landscape.course_inventory
                    ],
                }

            if report.alignment:
                result["alignment"] = {
                    "narrative": report.alignment.alignment_narrative,
                    "profile": {
                        "entry_timing": report.alignment.alignment_profile.entry_timing.value,
                        "specialization": report.alignment.alignment_profile.specialization_pattern.value,
                        "domain_balance": report.alignment.alignment_profile.domain_balance.value,
                        "coherence": report.alignment.alignment_profile.pathway_coherence.value,
                        "choice_architecture": report.alignment.alignment_profile.choice_architecture.value,
                        "ai_integration": report.alignment.alignment_profile.ai_integration.value,
                    },
                    "opportunities": report.alignment.opportunity_signals.opportunities,
                    "risks": report.alignment.opportunity_signals.risk_flags,
                }

            if report.design:
                result["design"] = {
                    "strategy": report.design.strategy.value,
                    "existing_course": report.design.existing_course_to_align,
                    "role": report.design.aif_role.value,
                    "narrative": report.design.design_narrative,
                    "confidence": report.design.design_confidence,
                    "variables": {
                        "grade_band": report.design.design_variables.grade_band,
                        "credit_framing": report.design.design_variables.credit_framing,
                        "entry_strength": report.design.design_variables.entry_strength,
                    },
                    "downstream_pathways": [
                        {
                            "name": dp.name,
                            "courses": dp.courses,
                            "relationship": dp.relationship.value,
                        }
                        for dp in report.design.downstream_pathways
                    ],
                    "assumptions": report.design.assumptions,
                    "validation_needed": report.design.validation_needed,
                }

            # Generate markdown report
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_filename = f"{district_name.replace(' ', '_')}_{state.replace(' ', '_')}_{timestamp}"

            markdown_filename = f"{base_filename}.md"
            markdown_path = REPORTS_DIR / markdown_filename

            report_generator = ReportGenerator()
            report_generator.generate(report, str(markdown_path), format="markdown")

            # Generate pathway comparison HTML
            comparison_filename = f"{base_filename}_pathway_comparison.html"
            comparison_path = REPORTS_DIR / comparison_filename

            comparison_generator = PathwayComparisonGenerator()
            comparison_generator.generate(report, str(comparison_path))

            # Store file paths in result
            result["markdown_file"] = markdown_filename
            result["comparison_html_file"] = comparison_filename

            analysis_jobs[job_id]["status"] = "completed"
            analysis_jobs[job_id]["progress"] = "Analysis complete"
            analysis_jobs[job_id]["result"] = result

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        analysis_jobs[job_id]["status"] = "failed"
        analysis_jobs[job_id]["error"] = str(e)
        analysis_jobs[job_id]["progress"] = "Analysis failed"

    finally:
        # Clean up temp file
        if doc_path and os.path.exists(doc_path):
            try:
                os.unlink(doc_path)
            except Exception:
                pass


@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    """Get the status of an analysis job."""
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = analysis_jobs[job_id]
    return AnalysisStatus(
        job_id=job_id,
        status=job["status"],
        progress=job["progress"],
        result=job["result"],
        error=job["error"],
    )


@app.get("/api/download/{job_id}")
async def download_report(job_id: str):
    """Download the full markdown report for a completed analysis."""
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = analysis_jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed")

    if not job["result"] or "markdown_file" not in job["result"]:
        raise HTTPException(status_code=404, detail="Report not available")

    markdown_filename = job["result"]["markdown_file"]
    markdown_path = REPORTS_DIR / markdown_filename

    if not markdown_path.exists():
        raise HTTPException(status_code=404, detail="Report file not found")

    return FileResponse(
        path=str(markdown_path),
        filename=markdown_filename,
        media_type="text/markdown",
    )


@app.get("/api/view-comparison/{job_id}")
async def view_comparison(job_id: str):
    """View the pathway comparison HTML visualization in browser."""
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = analysis_jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed")

    if not job["result"] or "comparison_html_file" not in job["result"]:
        raise HTTPException(status_code=404, detail="Comparison not available")

    comparison_filename = job["result"]["comparison_html_file"]
    comparison_path = REPORTS_DIR / comparison_filename

    if not comparison_path.exists():
        raise HTTPException(status_code=404, detail="Comparison file not found")

    # Read and return HTML content directly for inline viewing
    with open(comparison_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    return HTMLResponse(content=html_content)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


def main():
    """Run the web server."""
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")

    print(f"\nDistrict Pathway Analyzer Web Interface")
    print(f"   Starting server at http://{host}:{port}")
    print(f"   Press Ctrl+C to stop\n")

    uvicorn.run(
        "district_pathway_analyzer.web.server:app",
        host=host,
        port=port,
        reload=True,
    )


if __name__ == "__main__":
    main()
