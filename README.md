# District Pathway Analyzer

AI-Powered District CTE Pathway Analysis Tool for analyzing school district Career and Technical Education (CTE) programs to identify strategic opportunities for integrating Code.org's AI Foundations curriculum.

## Overview

This tool automates the analysis of school district CTE programs to:

1. Discover and inventory all digital/technical CTE courses
2. Analyze the current pathway structure
3. Identify alignment gaps with the Digital Technology cluster
4. Design a specific role for AI Foundations
5. Produce a comprehensive report with recommendations

## Features

- **Automated Discovery**: Finds and extracts course information from district websites and documents
- **Domain Tagging**: Classifies courses into Digital Technology domains (CS, Software Dev, Data/AI, Cybersecurity, IT, Digital Media, etc.)
- **Landscape Modeling**: Builds a structural model of the district's pathway organization
- **Alignment Analysis**: Compares district structure to the National Career Clusters Framework
- **Pathway Design**: Generates strategic recommendations for AI Foundations integration
- **Report Generation**: Produces professional reports in Markdown, PDF, or JSON format

## Installation

### Prerequisites

- Python 3.10 or higher
- Anthropic API key

### Setup

1. Clone the repository:
```bash
git clone https://github.com/your-org/district-pathway-analyzer.git
cd district-pathway-analyzer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package:
```bash
pip install -e .
```

4. Set up your API key:
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Usage

### Command Line Interface

#### Analyze a District

```bash
# Basic analysis with auto-discovery
pathway-analyzer analyze "Johnston County Schools" "North Carolina"

# Analysis with local documents
pathway-analyzer analyze "Buncombe County Schools" NC -d courses.pdf -d catalog.pdf

# Analysis with specific URLs
pathway-analyzer analyze "Example District" CA -u https://example.com/cte-courses

# Specify output format
pathway-analyzer analyze "Test District" TX -o report.pdf -f pdf
```

#### Extract Courses from a Document

```bash
# Extract courses from a PDF
pathway-analyzer extract courses.pdf

# Save extracted courses to JSON
pathway-analyzer extract catalog.html -o courses.json
```

#### Convert Report Formats

```bash
# Convert JSON report to PDF
pathway-analyzer convert report.json -f pdf

# Convert to Markdown
pathway-analyzer convert report.json -f markdown -o summary.md
```

#### View Configuration

```bash
pathway-analyzer config
```

### Python API

```python
from district_pathway_analyzer import DistrictPathwayAnalyzer

# Initialize analyzer
with DistrictPathwayAnalyzer() as analyzer:
    # Run analysis
    report = analyzer.analyze(
        district_name="Johnston County Schools",
        state="North Carolina",
        documents=["courses.pdf"],
    )

    # Generate report
    analyzer.generate_report(report, "output/report.md", format="markdown")

    # Access results
    print(f"Found {len(report.landscape.course_inventory)} courses")
    print(f"Strategy: {report.design.strategy.value}")
```

## Analysis Pipeline

The tool follows a multi-phase analysis pipeline:

### Phase 0: Discovery & Validation
- Finds district CTE course information from web sources or uploaded documents
- Extracts course titles, descriptions, and metadata
- Validates data quality and passes through a discovery gate

### Phase 1: Domain Tagging
- Classifies each course into Digital Technology domains
- Applies rule-based and LLM-assisted tagging
- Analyzes domain coverage patterns

### Phase 2: Landscape Modeling (Layer 1)
- Infers course roles (exploratory, gatekeeper, concentrator, capstone)
- Analyzes pathway shape (funnel, parallel silos, late entry, missing entry)
- Identifies entry points and pathway structure

### Phase 3: Alignment Analysis (Layer 2)
- Compares district structure to Digital Technology cluster framework
- Assesses entry timing, specialization patterns, and coherence
- Identifies opportunities and risk flags

### Phase 4: Pathway Design (Layer 3)
- Determines optimal strategy (position new, align existing, hybrid)
- Designs AI Foundations role within district structure
- Maps connections to downstream pathways
- Validates design against invariants

## Configuration

Configuration is managed through `config.yaml`:

```yaml
llm:
  provider: "anthropic"
  model: "claude-sonnet-4-20250514"
  max_tokens: 4000
  temperature: 0.3

discovery:
  max_search_results: 10
  timeout_seconds: 30
  cache_enabled: true

gates:
  min_courses_found: 3
  min_verified_percentage: 0.80

output:
  default_format: "pdf"
```

## Report Structure

Generated reports include:

1. **Executive Summary**: Key findings and recommendations
2. **Current Landscape**: Pathway shape, entry points, domain coverage
3. **Alignment Analysis**: Comparison to national framework
4. **Recommendations**: Designed role for AI Foundations
5. **Value Proposition**: District-facing benefits summary
6. **Implementation Considerations**: Next steps and validation needs
7. **Appendices**: Course inventory, confidence notes, AI Foundations overview

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest tests/
```

### Code Formatting

```bash
black src/
ruff check src/
```

### Type Checking

```bash
mypy src/
```

## Project Structure

```
district_pathway_analyzer/
├── src/
│   └── district_pathway_analyzer/
│       ├── __init__.py
│       ├── analyzer.py          # Main orchestrator
│       ├── cli.py               # Command-line interface
│       ├── config.py            # Configuration management
│       ├── llm_client.py        # Claude API client
│       ├── models.py            # Data models and enums
│       ├── discovery/           # Phase 0: Discovery
│       ├── tagging/             # Phase 1: Domain Tagging
│       ├── landscape/           # Phase 2: Landscape Modeling
│       ├── alignment/           # Phase 3: Alignment Analysis
│       ├── design/              # Phase 4: Pathway Design
│       ├── report/              # Report Generation
│       ├── knowledge_base/      # Reference documents
│       └── utils/               # Utilities
├── tests/
├── config.yaml
├── pyproject.toml
└── README.md
```

## Design Principles

1. **Hard discovery gate**: The tool does not proceed without validated data
2. **Layered analysis**: Diagnostic layers inform but don't prescribe solutions
3. **Preserve downstream pathways**: Recommendations never displace existing advanced courses
4. **Conservative tagging**: Prefer accuracy over coverage
5. **Transparent confidence**: All assumptions and uncertainties are documented

## License

MIT License

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

## Support

For issues and feature requests, please use the GitHub issue tracker.
