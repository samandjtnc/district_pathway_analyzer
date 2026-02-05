"""
Generate pathway comparison HTML visualization showing before/after with AI Foundations.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Set

from district_pathway_analyzer.models import DistrictAnalysisReport


class PathwayComparisonGenerator:
    """Generates before/after pathway comparison HTML."""

    def generate(self, report: DistrictAnalysisReport, output_path: str) -> str:
        """Generate pathway comparison HTML.

        Args:
            report: The analysis report
            output_path: Path to write the HTML file

        Returns:
            Path to the generated HTML file
        """
        html_content = self._build_html(report)

        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return output_path

    def _build_html(self, report: DistrictAnalysisReport) -> str:
        """Build the complete HTML content."""
        district_name = report.district_name
        state = report.state

        # Extract pathway data
        current_pathways = self._extract_current_pathways(report)
        current_shape = report.landscape.pathway_shape.value if report.landscape else "unknown"

        # Build HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{district_name}: Before and After AI Foundations</title>
    <link href="https://fonts.googleapis.com/css2?family=Barlow+Semi+Condensed:wght@500;600&family=Figtree:wght@400;600&display=swap" rel="stylesheet">
    {self._get_styles()}
</head>
<body>
    <div class="main-title">{district_name}, {state} - Digital Technology Pathways</div>
    <div class="subtitle">Current {current_shape.replace('_', ' ')} structure vs. designed entry point with AI Foundations</div>

    <div class="comparison-container">
        {self._build_current_state(report, current_pathways)}
        {self._build_designed_state(report, current_pathways)}
    </div>

    {self._build_impact_section(report)}

    <div class="logo">code.org | {district_name} Pathway Analysis | Generated {datetime.now().strftime('%B %d, %Y')}</div>
</body>
</html>"""
        return html

    def _extract_base_name(self, title: str) -> str:
        """Extract the base course name by removing level indicators.

        Args:
            title: Course title

        Returns:
            Base course name without level indicators
        """
        # Remove common level indicators
        patterns = [
            r'\s+[I]+\s*$',  # Roman numerals at end (I, II, III)
            r'\s+[0-9]+\s*$',  # Arabic numerals at end (1, 2, 3)
            r'\s+(One|Two|Three|Four)\s*$',  # Word numbers at end
            r'\s+(Beginning|Intermediate|Advanced)\s*$',  # Level words
            r'\s+(Intro|Introduction)\s+to\s+',  # Intro prefix
        ]

        base = title
        for pattern in patterns:
            base = re.sub(pattern, '', base, flags=re.IGNORECASE)

        return base.strip()

    def _get_course_sequence(self, title: str) -> Tuple[str, int]:
        """Get the sequence information from a course title.

        Args:
            title: Course title

        Returns:
            Tuple of (base_name, sequence_number)
        """
        title_lower = title.lower()

        # Check for Roman numerals
        roman_map = {'i': 1, 'ii': 2, 'iii': 3, 'iv': 4}
        for roman, num in roman_map.items():
            if re.search(rf'\b{roman}\b', title_lower):
                return (self._extract_base_name(title), num)

        # Check for Arabic numerals
        match = re.search(r'\b([1-4])\b', title_lower)
        if match:
            return (self._extract_base_name(title), int(match.group(1)))

        # Check for word numbers
        word_map = {'one': 1, 'two': 2, 'three': 3, 'four': 4,
                    'beginning': 1, 'intermediate': 2, 'advanced': 3}
        for word, num in word_map.items():
            if word in title_lower:
                return (self._extract_base_name(title), num)

        # No sequence found
        return (title, 0)

    def _compute_title_similarity(self, title1: str, title2: str) -> float:
        """Compute similarity between two course titles.

        Args:
            title1: First course title
            title2: Second course title

        Returns:
            Similarity score between 0 and 1
        """
        # Extract base names
        base1 = self._extract_base_name(title1).lower()
        base2 = self._extract_base_name(title2).lower()

        # Exact match
        if base1 == base2:
            return 1.0

        # Tokenize into words
        words1 = set(re.findall(r'\w+', base1))
        words2 = set(re.findall(r'\w+', base2))

        # Remove common words
        stop_words = {'and', 'the', 'a', 'an', 'of', 'to', 'in', 'for'}
        words1 = words1 - stop_words
        words2 = words2 - stop_words

        if not words1 or not words2:
            return 0.0

        # Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def _group_into_sequences(self, courses: List[Dict]) -> Dict[str, List[Dict]]:
        """Group courses into logical sequences based on document order, role progression, and title similarity.

        Args:
            courses: List of course dictionaries (in document order)

        Returns:
            Dictionary mapping sequence names to course lists
        """
        if not courses:
            return {}

        sequences = {}
        used_indices = set()

        # Add document index to preserve order
        for i, course in enumerate(courses):
            course['_doc_index'] = i

        for i, course in enumerate(courses):
            if i in used_indices:
                continue

            # Get sequence info for this course
            base_name, seq_num = self._get_course_sequence(course['title'])

            # Find all related courses in the sequence
            sequence_courses = [course]
            used_indices.add(i)

            # Look for related courses using multiple signals
            candidate_indices = []
            for j, other_course in enumerate(courses):
                if j in used_indices or j == i:
                    continue

                # Signal 1: High title similarity (same course family)
                similarity = self._compute_title_similarity(course['title'], other_course['title'])
                is_similar = similarity >= 0.7

                # Signal 2: Sequential in document + compatible roles + MINIMUM similarity
                # This prevents grouping totally unrelated courses just because they're next to each other
                is_sequential = abs(j - i) <= 3  # Within 3 positions
                role_order = ['exploratory', 'gatekeeper', 'concentrator', 'capstone']
                current_role_idx = role_order.index(course['role']) if course['role'] in role_order else -1
                other_role_idx = role_order.index(other_course['role']) if other_course['role'] in role_order else -1
                is_role_progression = (current_role_idx >= 0 and other_role_idx >= 0 and
                                     other_role_idx >= current_role_idx)
                # ADDED: Require at least SOME similarity even for sequential courses
                has_minimum_similarity = similarity >= 0.25

                # Signal 3: Moderate similarity + sequential
                is_moderate_and_sequential = similarity >= 0.4 and is_sequential

                # Group if any strong signal is present
                if is_similar or (is_sequential and is_role_progression and has_minimum_similarity) or is_moderate_and_sequential:
                    sequence_courses.append(other_course)
                    candidate_indices.append(j)

            # SANITY CHECK: Validate pathway coherence
            if len(sequence_courses) > 1:
                original_count = len(sequence_courses)
                sequence_courses = self._validate_pathway_coherence(sequence_courses)

                # Only mark as used the courses that passed coherence check
                # (First course is always kept, so we skip it)
                kept_count = len(sequence_courses)
                for idx in candidate_indices[:kept_count - 1]:
                    used_indices.add(idx)
            else:
                # Mark all candidates as used since no filtering happened
                for idx in candidate_indices:
                    used_indices.add(idx)

            # Sort by: sequence number, then role, then document order
            sequence_courses.sort(key=lambda c: (
                self._get_course_sequence(c['title'])[1],  # Explicit sequence (I, II, III)
                {'exploratory': 0, 'gatekeeper': 1, 'concentrator': 2, 'capstone': 3, 'unknown': 4}.get(c['role'], 5),
                c.get('_doc_index', 999)  # Document order as tiebreaker
            ))

            # Create a sequence name
            if len(sequence_courses) > 1:
                sequence_name = self._infer_pathway_name(sequence_courses)
            else:
                sequence_name = course['title']

            sequences[sequence_name] = sequence_courses

        return sequences

    def _validate_pathway_coherence(self, courses: List[Dict]) -> List[Dict]:
        """Validate that courses in a pathway are topically coherent.

        Split out courses that don't belong based on title coherence.

        Args:
            courses: List of courses in a potential pathway

        Returns:
            Filtered list of courses that are topically coherent
        """
        if len(courses) <= 2:
            return courses  # Keep small sequences together - trust initial grouping

        # For sequences of 3-4 courses, be lenient (only split if very different)
        # For sequences of 5+, be more strict
        is_small_sequence = len(courses) <= 4

        # Extract meaningful keywords from all titles (excluding stop words and common CTE terms)
        def get_topic_keywords(title: str) -> Set[str]:
            words = set(re.findall(r'\w+', title.lower()))
            stop_words = {'intro', 'introduction', 'to', 'and', 'the', 'a', 'an', 'of',
                         'in', 'for', 'i', 'ii', 'iii', 'iv', '1', '2', '3', '4',
                         'beginning', 'intermediate', 'advanced', 'one', 'two', 'three'}

            # Expand with semantic equivalents for CTE domains
            semantic_expansions = {
                'coding': {'programming', 'code', 'coding', 'development', 'software'},
                'programming': {'programming', 'code', 'coding', 'development', 'software'},
                'python': {'programming', 'code', 'coding', 'python'},
                'java': {'programming', 'code', 'coding', 'java'},
                'web': {'web', 'website', 'internet', 'online'},
                'design': {'design', 'designing', 'designer'},
                'digital': {'digital', 'computer', 'electronic'},
                'print': {'print', 'printing', 'graphic', 'publishing'},
                'image': {'image', 'photo', 'picture', 'graphic', 'visual'},
                'edit': {'edit', 'editing', 'editor', 'manipulation'},
            }

            expanded_words = words - stop_words
            for word in list(expanded_words):
                if word in semantic_expansions:
                    expanded_words.update(semantic_expansions[word])

            return expanded_words

        # Get keywords from first course (the anchor)
        anchor_keywords = get_topic_keywords(courses[0]['title'])

        if not anchor_keywords:
            return courses  # No meaningful keywords to check

        coherent_courses = [courses[0]]

        # Check each subsequent course for topical coherence
        for course in courses[1:]:
            course_keywords = get_topic_keywords(course['title'])

            if not course_keywords:
                coherent_courses.append(course)  # Keep generic courses
                continue

            # Check if course shares ANY significant keywords with anchor
            # OR if it shares keywords with the pathway name we'd infer
            shared_keywords = anchor_keywords & course_keywords

            # Also check against accumulated coherent courses
            all_coherent_keywords = set()
            for coherent_course in coherent_courses:
                all_coherent_keywords |= get_topic_keywords(coherent_course['title'])

            course_shared_with_group = course_keywords & all_coherent_keywords

            # Keep course if it shares keywords OR has high similarity with ANY course in group
            max_similarity = max(
                self._compute_title_similarity(course['title'], coherent_course['title'])
                for coherent_course in coherent_courses
            )

            # For small sequences (3-4 courses), use lower threshold
            # For larger sequences (5+), be stricter
            similarity_threshold = 0.3 if is_small_sequence else 0.5

            if shared_keywords or course_shared_with_group or max_similarity >= similarity_threshold:
                coherent_courses.append(course)
            # else: drop this course from the sequence (it'll form its own pathway)

        return coherent_courses

    def _infer_pathway_name(self, courses: List[Dict]) -> str:
        """Infer a pathway name from a sequence of courses.

        Args:
            courses: List of courses in the sequence

        Returns:
            Inferred pathway name
        """
        # Try to find common theme from titles
        first_title = courses[0]['title'].lower()

        # Check for common programming patterns
        if any(word in first_title for word in ['coding', 'programming', 'python', 'java', 'c++']):
            # Check if it's a full programming sequence
            if len(courses) >= 2:
                return 'Software Development & Programming'
            return 'Programming'

        # Check for web development
        if 'web' in first_title:
            return 'Web Development'

        # Check for digital media/design
        if any(word in first_title for word in ['design', 'digital', 'image', 'print', 'media']):
            return 'Digital Media & Design'

        # Fall back to base name of first course
        base_name, _ = self._get_course_sequence(courses[0]['title'])
        return base_name

    def _extract_current_pathways(self, report: DistrictAnalysisReport) -> List[Dict]:
        """Extract pathway information from the report using intelligent grouping."""
        if not report.landscape:
            return []

        pathways = []
        courses = report.landscape.course_inventory

        # Convert to simpler format (preserving document order)
        course_list = [
            {
                'title': course.title,
                'role': course.role.value if course.role else 'unknown',
                'domain': course.domain_tags.primary if course.domain_tags else None
            }
            for course in courses
        ]

        # Group by domain first (preserve order within domain)
        domain_groups = {}
        for course in course_list:
            domain = course.get('domain', 'Digital Technology')
            if domain not in domain_groups:
                domain_groups[domain] = []
            domain_groups[domain].append(course)

        # Process each domain group
        for domain, domain_courses in domain_groups.items():
            # Group courses into sequences within this domain (respects document order)
            sequences = self._group_into_sequences(domain_courses)

            # Create pathways from sequences
            for seq_name, seq_courses in sequences.items():
                # Determine pathway name (use inferred name if already computed)
                if len(seq_courses) > 1 and seq_name != seq_courses[0]['title']:
                    pathway_name = seq_name  # Already inferred by _infer_pathway_name
                else:
                    pathway_name = self._determine_pathway_name(seq_name, seq_courses)

                # Already sorted in _group_into_sequences, but clean up temp fields
                for course in seq_courses:
                    course.pop('_doc_index', None)

                # Show up to 5 courses per pathway (increased from 3)
                pathways.append({
                    'name': pathway_name,
                    'courses': seq_courses[:5],
                    'color_class': self._get_color_class(pathway_name)
                })

        # Show up to 6 pathways (increased from 4)
        return pathways[:6]

    def _determine_pathway_name(self, sequence_name: str, courses: List[Dict]) -> str:
        """Determine a clear pathway name for a sequence of courses.

        Args:
            sequence_name: Base name of the course sequence
            courses: List of courses in the sequence

        Returns:
            Human-readable pathway name
        """
        # Use the sequence name if it's already descriptive
        if len(courses) > 1:
            # Multiple courses - use the base name
            return sequence_name

        # Single course - use more specific categorization
        title_lower = courses[0]['title'].lower()

        # Check for highly specific patterns first (more specific = higher priority)
        if '3d' in title_lower and ('modeling' in title_lower or 'animation' in title_lower):
            return '3D Modeling & Animation'
        elif 'drafting' in title_lower or 'cad' in title_lower or 'technical drawing' in title_lower:
            return 'Technical Drafting'
        elif 'python' in title_lower or 'java' in title_lower or 'c++' in title_lower:
            return 'Programming'
        elif 'web' in title_lower and ('design' in title_lower or 'development' in title_lower):
            return 'Web Development'
        elif 'network' in title_lower or 'cisco' in title_lower or 'ccna' in title_lower:
            return 'Networking'
        elif 'cyber' in title_lower or 'security' in title_lower:
            return 'Cybersecurity'
        elif 'data' in title_lower and ('science' in title_lower or 'analytics' in title_lower):
            return 'Data Science'
        elif 'game' in title_lower and ('design' in title_lower or 'development' in title_lower):
            return 'Game Development'
        elif 'video' in title_lower or 'film' in title_lower or 'production' in title_lower:
            return 'Video Production'
        elif 'graphic' in title_lower or ('digital' in title_lower and 'design' in title_lower):
            return 'Graphic Design'

        # Fall back to domain if available
        domain = courses[0].get('domain')
        if domain:
            domain_map = {
                'computer_science': 'Computer Science',
                'software_development': 'Software Development',
                'networking': 'Networking',
                'cybersecurity': 'Cybersecurity',
                'data_science': 'Data Science',
                'digital_media': 'Digital Media',
                'it_support': 'IT Support'
            }
            return domain_map.get(domain, sequence_name)

        return sequence_name

    def _get_color_class(self, pathway_name: str) -> str:
        """Get CSS color class for a pathway."""
        pathway_colors = {
            'Programming': 'track-python',
            'Computer Science': 'track-python',
            'Software Development': 'track-python',
            'Software Development & Programming': 'track-python',
            'Web Development': 'track-web',
            'Networking': 'track-network',
            'IT Support': 'track-network',
            'Digital Design': 'track-design',
            'Digital Media': 'track-design',
            'Digital Media & Design': 'track-design',
            'Graphic Design': 'track-design',
            '3D Modeling & Animation': 'track-design',
            'Technical Drafting': 'track-design',
            'Cybersecurity': 'track-security',
            'Data Science': 'track-data'
        }
        return pathway_colors.get(pathway_name, 'track-python')

    def _build_current_state(self, report: DistrictAnalysisReport, pathways: List[Dict]) -> str:
        """Build the current state (before) section."""
        if not report.landscape:
            return ""

        shape = report.landscape.pathway_shape.value
        shape_description = {
            'parallel_silos': 'Parallel silos - students forced to specialize immediately',
            'funnel': 'Funnel - but missing modern AI/data content',
            'late_entry': 'Late entry - students miss foundational concepts',
            'missing_entry': 'Missing clear entry point - students confused about where to start'
        }.get(shape, 'Students must choose specialized tracks immediately')

        # Build pathway tracks
        tracks_html = ""
        num_pathways = len(pathways)
        # Dynamic grid: 2 cols for 2-4 pathways, 3 cols for 5-6, 4 cols for 7+
        if num_pathways <= 4:
            grid_cols = 2
        elif num_pathways <= 6:
            grid_cols = 3
        else:
            grid_cols = 4

        for pathway in pathways:
            courses_html = ""
            for i, course in enumerate(pathway['courses']):
                courses_html += f'<div class="course-box">{course["title"]}</div>\n'
                if i < len(pathway['courses']) - 1:
                    courses_html += '<div class="course-arrow">↓</div>\n'

            tracks_html += f"""
                <div class="track {pathway['color_class']}">
                    <div class="track-title">{pathway['name']}</div>
                    {courses_html}
                </div>
            """

        problems = self._extract_problems(report)
        problems_html = "\n".join([f"<li>{p}</li>" for p in problems])

        return f"""
        <div class="pathway-section current-state">
            <div class="section-header">
                <span>Current State</span>
                <span class="status-badge">⚠️ PROBLEM</span>
            </div>
            <div class="section-subtitle">{shape_description}</div>

            <div class="grade-label">Grade 9-10: Choose Your Track (Limited Exploration)</div>

            <div class="confusion-box">
                <div class="confusion-title">😕 Students face {num_pathways} entry points with no shared foundation</div>
                <div class="confusion-text">
                    "Which track is right for me? What's the difference between these options?
                    I haven't learned about any of this yet. I guess I'll just pick one..."
                </div>
            </div>

            <div class="parallel-tracks" style="grid-template-columns: repeat({grid_cols}, 1fr);">
                {tracks_html}
            </div>

            <div class="problem-box">
                <div class="problem-title">
                    <span>⚠️</span>
                    <span>Critical Problems:</span>
                </div>
                <ul class="problem-list">
                    {problems_html}
                </ul>
            </div>
        </div>
        """

    def _build_designed_state(self, report: DistrictAnalysisReport, pathways: List[Dict]) -> str:
        """Build the designed state (after) section."""
        if not report.design:
            return ""

        strategy = report.design.strategy.value.replace('_', ' ').title()
        aif_role = report.design.aif_role.value.replace('_', ' ').title()

        # Build informed tracks
        tracks_html = ""
        num_pathways = len(pathways)
        grid_cols = 2 if num_pathways <= 4 else 3

        for pathway in pathways:
            courses_html = ""
            for i, course in enumerate(pathway['courses']):
                courses_html += f'<div class="course-box {pathway["color_class"]}">{course["title"]}</div>\n'
                if i < len(pathway['courses']) - 1:
                    courses_html += '<div class="course-arrow">↓</div>\n'

            benefit_text = self._get_pathway_benefit(pathway['name'])

            tracks_html += f"""
                <div class="informed-track">
                    <div class="informed-track-title">{pathway['name']}</div>
                    {courses_html}
                    <div style="text-align: center; font-size: 10px; color: #0093A4; margin-top: 6px; font-style: italic;">
                        ✓ {benefit_text}
                    </div>
                </div>
            """

        benefits = self._extract_benefits(report)
        benefits_html = "\n".join([f"<li>{b}</li>" for b in benefits])

        return f"""
        <div class="pathway-section designed-state">
            <div class="section-header">
                <span>Designed State</span>
                <span class="status-badge">✅ SOLUTION</span>
            </div>
            <div class="section-subtitle">Strategy: {strategy} - {aif_role}</div>

            <div class="grade-label">Grade 9: Shared Entry Point (Broad Exploration)</div>

            <div class="entry-point">
                <div class="entry-course">
                    <div class="entry-course-title">🤖 AI Foundations</div>
                    <div class="entry-course-subtitle">Every student explores the breadth of digital technology</div>

                    <div class="exploration-topics">
                        <div class="topic-badge">🧠 Artificial Intelligence</div>
                        <div class="topic-badge">🐍 Python Programming</div>
                        <div class="topic-badge">💻 Computer Systems</div>
                        <div class="topic-badge">🌐 Networks</div>
                        <div class="topic-badge">🔒 Cybersecurity</div>
                        <div class="topic-badge">📊 Data Science</div>
                    </div>
                </div>
            </div>

            <div class="big-arrow">
                <div class="big-arrow-text">Students now make INFORMED choices</div>
                <div class="big-arrow-icon">↓</div>
            </div>

            <div class="grade-label">Grades 10-12: Choose Your Specialization (With Context)</div>

            <div class="informed-tracks" style="grid-template-columns: repeat({grid_cols}, 1fr);">
                {tracks_html}
            </div>

            <div class="benefit-box">
                <div class="benefit-title">
                    <span>✅</span>
                    <span>Transformative Benefits:</span>
                </div>
                <ul class="benefit-list">
                    {benefits_html}
                </ul>
            </div>
        </div>
        """

    def _get_pathway_benefit(self, pathway_name: str) -> str:
        """Get specific benefit text for a pathway."""
        benefits = {
            'Programming': 'Already learned Python basics in AI Foundations',
            'Computer Science': 'Already learned programming fundamentals',
            'Web Development': 'Knows Python, can build full-stack applications',
            'Networking': 'Already explored networks & cybersecurity',
            'Digital Design': 'Understands how design connects to technology',
            'Cybersecurity': 'Already learned security fundamentals',
            'Data Science': 'Already explored data analysis with AI'
        }
        return benefits.get(pathway_name, 'Has shared foundation from AI Foundations')

    def _extract_problems(self, report: DistrictAnalysisReport) -> List[str]:
        """Extract problems from the current pathway structure."""
        problems = []

        if report.landscape:
            shape = report.landscape.pathway_shape.value

            if shape == 'parallel_silos':
                problems.append("<strong>❌ Premature specialization</strong> - Students locked into narrow tracks before understanding the field")
                problems.append("<strong>❌ No shared foundation</strong> - Missing cross-cutting concepts (AI, data, systems thinking)")
                problems.append("<strong>❌ Parallel silos</strong> - Multiple separate entry points create confusion and fragmentation")
            elif shape == 'missing_entry':
                problems.append("<strong>❌ No clear starting point</strong> - Students confused about which course to take first")
                problems.append("<strong>❌ Disconnected courses</strong> - No obvious pathway progression")
            elif shape == 'late_entry':
                problems.append("<strong>❌ Late introduction</strong> - Students miss foundational concepts")
                problems.append("<strong>❌ Limited exploration</strong> - Advanced courses before students understand basics")

        # Add common problems
        problems.append("<strong>❌ Limited switching</strong> - Hard to change tracks once started")
        problems.append("<strong>❌ Missing modern topics</strong> - Limited exposure to AI, machine learning, data science")
        problems.append("<strong>❌ Student confusion</strong> - \"How do I know which track is right if I haven't tried any?\"")

        return problems

    def _extract_benefits(self, report: DistrictAnalysisReport) -> List[str]:
        """Extract benefits from the designed pathway structure."""
        benefits = [
            "<strong>✅ Informed choice</strong> - Students explore before specializing, choose with confidence",
            "<strong>✅ Shared foundation</strong> - All students get AI, data, systems, networks, cybersecurity basics",
            "<strong>✅ Single clear entry</strong> - One obvious starting point eliminates confusion",
            "<strong>✅ Flexible pathways</strong> - Students can switch tracks with foundation intact",
            "<strong>✅ Modern skills</strong> - Early exposure to AI, ML, data science throughout career",
            "<strong>✅ All tracks preserved</strong> - Every existing course remains, just better-prepared students"
        ]

        if report.alignment and report.alignment.opportunity_signals:
            # Add specific opportunities from the analysis
            for opp in report.alignment.opportunity_signals.opportunities[:2]:
                benefits.append(f"<strong>✅</strong> {opp}")

        return benefits

    def _build_impact_section(self, report: DistrictAnalysisReport) -> str:
        """Build the impact comparison section."""
        district_name = report.district_name

        return f"""
    <div class="impact-section">
        <div class="impact-title">The Transformation: Same Courses, Radically Different Student Experience</div>

        <div class="impact-grid">
            <div class="impact-column before">
                <div class="impact-column-title">❌ Before: Fragmented Entry</div>
                <div class="impact-text">
                    <strong>Student at Grade 9:</strong> "I have to pick between these different tracks. I don't know what any of these really are or which one is right for me. I guess I'll just pick one..."
                    <br><br>
                    <strong>Student at Grade 11:</strong> "I don't like this track as much as I thought. But I'm already two years in—too late to switch now without starting over."
                    <br><br>
                    <strong>Result:</strong> Accidental pathways, narrow skills, student frustration, high dropout rates.
                </div>
            </div>

            <div class="impact-column after">
                <div class="impact-column-title">✅ After: Exploration → Informed Choice</div>
                <div class="impact-text">
                    <strong>Student at Grade 9:</strong> "In AI Foundations, I'm learning Python, networks, data, AI, and cybersecurity. I'm discovering what I'm really interested in!"
                    <br><br>
                    <strong>Student at Grade 11:</strong> "I chose this pathway because I discovered my passion in grade 9. And I can apply all my foundational skills. I know where I'm headed."
                    <br><br>
                    <strong>Result:</strong> Confident choices, well-rounded skills, student engagement, clear career paths.
                </div>
            </div>
        </div>
    </div>
        """

    def _get_styles(self) -> str:
        """Return the CSS styles for the HTML."""
        return """
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Figtree', sans-serif;
            background: #FFFFFF;
            padding: 40px;
            min-height: 100vh;
        }

        .main-title {
            font-family: 'Barlow Semi Condensed', sans-serif;
            font-size: 42px;
            font-weight: 600;
            color: #292F36;
            text-align: center;
            margin-bottom: 10px;
        }

        .subtitle {
            font-size: 18px;
            color: #6B7280;
            text-align: center;
            margin-bottom: 50px;
            font-style: italic;
        }

        .comparison-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            margin-bottom: 40px;
        }

        .pathway-section {
            border-radius: 16px;
            padding: 30px;
            position: relative;
            min-height: 800px;
        }

        .current-state {
            background: linear-gradient(135deg, rgba(237, 96, 96, 0.1) 0%, rgba(237, 96, 96, 0.15) 100%);
            border: 4px solid #ED6060;
        }

        .designed-state {
            background: linear-gradient(135deg, rgba(0, 147, 164, 0.05) 0%, rgba(0, 147, 164, 0.1) 100%);
            border: 4px solid #0093A4;
        }

        .section-header {
            font-family: 'Barlow Semi Condensed', sans-serif;
            font-size: 34px;
            font-weight: 600;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .current-state .section-header {
            color: #ED6060;
        }

        .designed-state .section-header {
            color: #0093A4;
        }

        .status-badge {
            font-size: 16px;
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: 600;
        }

        .current-state .status-badge {
            background: #ED6060;
            color: white;
        }

        .designed-state .status-badge {
            background: #0093A4;
            color: white;
        }

        .section-subtitle {
            font-size: 14px;
            margin-bottom: 30px;
            font-style: italic;
        }

        .current-state .section-subtitle {
            color: #ED6060;
        }

        .designed-state .section-subtitle {
            color: #0093A4;
        }

        .parallel-tracks {
            display: grid;
            gap: 16px;
            margin-bottom: 20px;
        }

        .track {
            background: white;
            border: 3px solid rgba(237, 96, 96, 0.4);
            border-radius: 12px;
            padding: 16px;
        }

        .track-title {
            font-family: 'Barlow Semi Condensed', sans-serif;
            font-size: 14px;
            font-weight: 600;
            color: #ED6060;
            text-align: center;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .course-box {
            padding: 10px 14px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            text-align: center;
            margin-bottom: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .track-python .course-box, .course-box.track-python {
            background: rgba(0, 147, 164, 0.15);
            border: 2px solid #0093A4;
            color: #0093A4;
        }

        .track-design .course-box, .course-box.track-design {
            background: rgba(140, 82, 186, 0.15);
            border: 2px solid #8C52BA;
            color: #8C52BA;
        }

        .track-network .course-box, .course-box.track-network {
            background: rgba(0, 255, 245, 0.2);
            border: 2px solid #00FFF5;
            color: #0093A4;
        }

        .track-web .course-box, .course-box.track-web {
            background: rgba(140, 82, 186, 0.1);
            border: 2px solid #8C52BA;
            color: #8C52BA;
        }

        .track-security .course-box, .course-box.track-security {
            background: rgba(237, 96, 96, 0.15);
            border: 2px solid #ED6060;
            color: #ED6060;
        }

        .track-data .course-box, .course-box.track-data {
            background: rgba(0, 147, 164, 0.1);
            border: 2px solid #0093A4;
            color: #0093A4;
        }

        .course-arrow {
            text-align: center;
            color: #9CA3AF;
            font-size: 16px;
            margin: 4px 0;
        }

        .confusion-box {
            background: rgba(237, 96, 96, 0.1);
            border: 3px dashed #ED6060;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
        }

        .confusion-title {
            font-family: 'Barlow Semi Condensed', sans-serif;
            font-size: 18px;
            font-weight: 600;
            color: #ED6060;
            margin-bottom: 8px;
        }

        .confusion-text {
            font-size: 13px;
            color: #292F36;
            line-height: 1.5;
        }

        .entry-point {
            margin-bottom: 30px;
        }

        .entry-course {
            background: linear-gradient(135deg, #00FFF5 0%, #00D9D0 100%);
            border: 4px solid #00D9D0;
            border-radius: 16px;
            padding: 24px;
            text-align: center;
            box-shadow: 0 8px 16px rgba(0, 255, 245, 0.3);
        }

        .entry-course-title {
            font-family: 'Barlow Semi Condensed', sans-serif;
            font-size: 28px;
            font-weight: 600;
            color: #292F36;
            margin-bottom: 8px;
        }

        .entry-course-subtitle {
            font-size: 14px;
            color: #0093A4;
            font-weight: 600;
        }

        .exploration-topics {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
            margin-top: 16px;
            padding-top: 16px;
            border-top: 2px solid #0093A4;
        }

        .topic-badge {
            background: rgba(255, 255, 255, 0.9);
            padding: 6px 10px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            color: #0093A4;
            text-align: center;
        }

        .big-arrow {
            text-align: center;
            margin: 20px 0;
        }

        .big-arrow-text {
            font-family: 'Barlow Semi Condensed', sans-serif;
            font-size: 18px;
            font-weight: 600;
            color: #0093A4;
            margin-bottom: 8px;
        }

        .big-arrow-icon {
            font-size: 36px;
            color: #0093A4;
        }

        .informed-tracks {
            display: grid;
            gap: 12px;
        }

        .informed-track {
            background: white;
            border: 3px solid #0093A4;
            border-radius: 8px;
            padding: 12px;
        }

        .informed-track-title {
            font-family: 'Barlow Semi Condensed', sans-serif;
            font-size: 12px;
            font-weight: 600;
            color: #0093A4;
            text-align: center;
            margin-bottom: 8px;
            text-transform: uppercase;
        }

        .informed-track .course-box {
            font-size: 12px;
            padding: 8px 10px;
        }

        .grade-label {
            font-family: 'Barlow Semi Condensed', sans-serif;
            font-size: 16px;
            font-weight: 600;
            color: #6B7280;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: 8px 0;
            border-bottom: 2px solid #E5E7EB;
        }

        .problem-box {
            background: #FFFFFF;
            border: 3px solid #ED6060;
            border-radius: 12px;
            padding: 20px;
            margin-top: 20px;
        }

        .problem-title {
            font-family: 'Barlow Semi Condensed', sans-serif;
            font-size: 18px;
            font-weight: 600;
            color: #ED6060;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .problem-list {
            font-size: 13px;
            color: #292F36;
            line-height: 1.8;
        }

        .problem-list li {
            margin-bottom: 8px;
            padding-left: 8px;
        }

        .benefit-box {
            background: #FFFFFF;
            border: 3px solid #0093A4;
            border-radius: 12px;
            padding: 20px;
            margin-top: 20px;
        }

        .benefit-title {
            font-family: 'Barlow Semi Condensed', sans-serif;
            font-size: 18px;
            font-weight: 600;
            color: #0093A4;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .benefit-list {
            font-size: 13px;
            color: #292F36;
            line-height: 1.8;
        }

        .benefit-list li {
            margin-bottom: 8px;
            padding-left: 8px;
        }

        .impact-section {
            background: linear-gradient(135deg, rgba(0, 147, 164, 0.05) 0%, rgba(0, 147, 164, 0.1) 100%);
            border: 4px solid #0093A4;
            border-radius: 16px;
            padding: 40px;
            text-align: center;
        }

        .impact-title {
            font-family: 'Barlow Semi Condensed', sans-serif;
            font-size: 32px;
            font-weight: 600;
            color: #0093A4;
            margin-bottom: 20px;
        }

        .impact-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-top: 30px;
        }

        .impact-column {
            text-align: left;
        }

        .impact-column-title {
            font-family: 'Barlow Semi Condensed', sans-serif;
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 12px;
        }

        .impact-column.before .impact-column-title {
            color: #ED6060;
        }

        .impact-column.after .impact-column-title {
            color: #0093A4;
        }

        .impact-text {
            font-size: 14px;
            color: #292F36;
            line-height: 1.8;
        }

        .logo {
            text-align: right;
            margin-top: 30px;
            font-family: 'Barlow Semi Condensed', sans-serif;
            font-size: 14px;
            color: #6B7280;
        }

        @media print {
            body {
                padding: 20px;
            }
            .comparison-container {
                page-break-inside: avoid;
            }
        }
    </style>
    """
