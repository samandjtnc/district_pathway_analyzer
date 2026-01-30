"""
Digital Technology Career Cluster reference information.

Based on the National Career Clusters Framework.
"""

DIGITAL_TECH_CLUSTER = {
    "name": "Digital Technology",
    "type": "Cross-Cutting Cluster",
    "definition": (
        "The Digital Technology Career Cluster focuses on developing digital "
        "systems for communication and data storage using critical technologies "
        "such as artificial intelligence (AI), data analytics, and cybersecurity. "
        "This Cluster builds skills necessary for all careers to navigate and "
        "lead in the constantly evolving tech landscape and drives innovation "
        "across all industries."
    ),
    "key_concept": (
        "Digital Technology is CROSS-CUTTING, meaning it spans all industries "
        "and sectors. It is not a narrow single pathway but rather a foundation "
        "for multiple specialized careers."
    ),
    "entry_philosophy": (
        "Entry-level courses should be exploratory and broad, not immediately "
        "specialized. Students should gain exposure to the breadth of digital "
        "technology before committing to a specific pathway."
    ),
}

DIGITAL_TECH_SUB_CLUSTERS = [
    {
        "name": "Data Science & Artificial Intelligence",
        "description": (
            "Focuses on collecting, analyzing, and interpreting large datasets "
            "to inform decision-making, as well as developing AI systems that "
            "can learn and make predictions."
        ),
        "sample_careers": [
            "Data Scientist",
            "Machine Learning Engineer",
            "AI Researcher",
            "Business Intelligence Analyst",
            "Data Engineer",
        ],
        "key_skills": [
            "Statistical analysis",
            "Programming (Python, R)",
            "Machine learning",
            "Data visualization",
            "Critical thinking",
        ],
    },
    {
        "name": "IT Support & Services",
        "description": (
            "Focuses on providing technical support, maintaining computer systems, "
            "and ensuring technology infrastructure operates effectively."
        ),
        "sample_careers": [
            "IT Support Specialist",
            "Help Desk Technician",
            "Systems Administrator",
            "Desktop Support Analyst",
            "Technical Support Engineer",
        ],
        "key_skills": [
            "Troubleshooting",
            "Customer service",
            "Hardware knowledge",
            "Operating systems",
            "Documentation",
        ],
    },
    {
        "name": "Network Systems & Cybersecurity",
        "description": (
            "Focuses on designing, implementing, and securing computer networks, "
            "as well as protecting systems and data from cyber threats."
        ),
        "sample_careers": [
            "Network Administrator",
            "Cybersecurity Analyst",
            "Security Engineer",
            "Penetration Tester",
            "Network Architect",
        ],
        "key_skills": [
            "Network configuration",
            "Security protocols",
            "Threat analysis",
            "Firewall management",
            "Incident response",
        ],
    },
    {
        "name": "Software Solutions",
        "description": (
            "Focuses on designing, developing, and maintaining software "
            "applications that solve problems and meet user needs."
        ),
        "sample_careers": [
            "Software Developer",
            "Full-Stack Engineer",
            "Mobile App Developer",
            "DevOps Engineer",
            "Quality Assurance Engineer",
        ],
        "key_skills": [
            "Programming languages",
            "Software design",
            "Version control",
            "Testing",
            "Agile methodology",
        ],
    },
    {
        "name": "Unmanned Vehicle Technology",
        "description": (
            "Focuses on the design, operation, and maintenance of unmanned "
            "vehicles including drones and autonomous systems."
        ),
        "sample_careers": [
            "Drone Operator",
            "UAV Technician",
            "Autonomous Vehicle Engineer",
            "Robotics Technician",
            "Flight Controller",
        ],
        "key_skills": [
            "Flight operations",
            "Sensor technology",
            "Navigation systems",
            "Regulations compliance",
            "Maintenance",
        ],
    },
    {
        "name": "Web & Cloud",
        "description": (
            "Focuses on developing web applications and managing cloud-based "
            "infrastructure and services."
        ),
        "sample_careers": [
            "Web Developer",
            "Cloud Architect",
            "Cloud Engineer",
            "Front-End Developer",
            "Back-End Developer",
        ],
        "key_skills": [
            "HTML/CSS/JavaScript",
            "Cloud platforms (AWS, Azure, GCP)",
            "Database management",
            "API development",
            "Responsive design",
        ],
    },
]

# Alignment matrix showing how entry courses should connect to sub-clusters
ENTRY_COURSE_ALIGNMENT = {
    "ideal_characteristics": [
        "Covers fundamentals from multiple sub-clusters",
        "No prerequisites required",
        "Emphasizes exploration over specialization",
        "Includes hands-on projects",
        "Introduces computational thinking",
        "Addresses AI/data literacy",
    ],
    "warning_signs": [
        "Immediate tool/language specialization",
        "Prerequisites that limit access",
        "Narrow focus on single sub-cluster",
        "Lacks connection to multiple pathways",
        "No AI/data science exposure",
    ],
}
