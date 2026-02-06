"""
AI Foundations curriculum reference information.

Source: AI_Foundations.pdf (Code.org official syllabus)
Semester 1: Final
Semester 2: DRAFT
"""

AI_FOUNDATIONS_CURRICULUM = {
    "name": "AI Foundations",
    "provider": "Code.org",
    "grade_level": "9-10",
    "prerequisites": "None required",
    "credit_type": ["CTE", "Academic"],
    "duration": {
        "semesters": 2,
        "total_class_periods": 174,
        "description": "Full year",
    },
    "overview": (
        "AI Foundations introduces students to the core principles of computer science "
        "and the growing role of artificial intelligence in everyday life. Through hands-on "
        "programming, visual problem solving, and critical analysis, students explore how "
        "computing systems work, how data powers AI, and how intelligent tools make "
        "decisions. They learn to write Python programs, analyze the structure of the "
        "Internet, investigate cybersecurity risks, and interpret data through visualizations "
        "and models. Throughout the course, students examine how AI systems impact "
        "individuals and communities, and build the skills to use computing and AI to "
        "solve meaningful problems in their world."
    ),
    "semesters": {
        "semester_1": {
            "title": "AI Foundations Semester 1",
            "status": "Final",
            "overview": (
                "AIF Semester 1 consists of six units designed to provide students with "
                "both foundational knowledge and hands-on experience. Each unit focuses "
                "on core computer science and AI topics, blending computational thinking "
                "with real-world applications."
            ),
            "learning_outcomes": [
                "Explain how generative AI models work and evaluate their outputs based on accuracy, clarity, and ethical considerations.",
                "Design and implement programs in Python using functions, loops, conditionals, and abstraction to solve structured problems.",
                "Use computational thinking strategies such as decomposition and pattern recognition to solve problems and analyze AI behavior.",
                "Describe how hardware and software components interact to input, store, process, and output information in computing systems.",
                "Explain how data moves across networks and the Internet, and analyze how AI improves reliability, accessibility, and user experience online.",
                "Identify and evaluate common cybersecurity threats and apply strategies like encryption and authentication to protect information.",
                "Analyze the social, ethical, and privacy implications of computing innovations and AI systems, especially regarding data use and decision-making.",
                "Interpret how AI systems use data to recognize patterns, make predictions, and influence real-world outcomes.",
                "Reflect on the role of personal identity and values in shaping how students use, critique, and create with computing and AI tools.",
            ],
            "units": [
                {
                    "number": 1,
                    "title": "Problem Solving with AI",
                    "class_periods": 15,
                    "description": (
                        "Students learn how generative AI models produce text and images by "
                        "identifying patterns and making predictions using training data and "
                        "probability. They develop skills in strategic prompting by experimenting "
                        "with input structure, context, and media type, and analyzing how these "
                        "choices affect AI-generated outputs. Through comparisons of human and "
                        "AI responses, students build awareness of AI's limitations and biases, "
                        "and gain practice refining AI outputs to make them clearer, more "
                        "accurate, and more aligned with user intent."
                    ),
                    "topics": [
                        "AI as an Assistant",
                        "AI Limitations",
                        "Bias and Hallucinations",
                        "AI for Creativity",
                        "AI in Decision-Making",
                    ],
                    "lessons": {
                        "week_1": [
                            "Talking to Machines",
                            "Beyond Words",
                            "The AI's Brain",
                            "Smart or Just Predictable?",
                            "Uncovering Contradictions",
                        ],
                        "week_2": [
                            "Understanding Bias",
                            "AI's Wild Imagination",
                            "Debugging and Refining Outputs",
                            "AI as a Co-Creator",
                            "Remixing, Creativity, and Originality",
                        ],
                        "week_3": [
                            "Ownership, Ethics, and Creativity",
                            "AI's Role in Society",
                            "AI Time Capsule Project",
                        ],
                    },
                    "learning_outcomes": [
                        "Explain how AI generates responses using training data, probability, and neural networks.",
                        "Analyze AI-generated content to identify bias, hallucinations, and misinformation.",
                        "Apply debugging techniques to refine AI outputs and improve response accuracy.",
                        "Use AI as a collaborative tool while recognizing its limitations and risks.",
                        "Evaluate the ethical implications of AI in decision-making and creative fields.",
                    ],
                    "unit_project": (
                        "Students curate historical data and use AI to generate future predictions "
                        "in areas like technology, fashion, media, healthcare, and climate policy. "
                        "They analyze AI's assumptions, biases, and ethical considerations, "
                        "refining AI-generated outputs and proposing responsible AI applications."
                    ),
                    "csta_standards": [
                        "3A-CS-01",
                        "3A-IC-24",
                        "3A-IC-25",
                        "3A-AP-22",
                        "3A-AP-23",
                    ],
                },
                {
                    "number": 2,
                    "title": "Foundations of AI Programming",
                    "class_periods": 15,
                    "description": (
                        "Students develop foundational programming skills in Python and "
                        "practice computational thinking through creative, visual problem "
                        "solving. Using the Painter, they learn how to sequence instructions, "
                        "define and call functions, use loops to reduce repetition, and apply "
                        "conditionals to make decisions. By solving challenges in The "
                        "Neighborhood, students build confidence as programmers while "
                        "exploring how AI systems follow rules and logic to complete tasks."
                    ),
                    "topics": [
                        "Variables",
                        "Loops",
                        "Conditionals",
                        "Functions",
                        "Debugging",
                        "Ethical Computing",
                    ],
                    "lessons": {
                        "week_1": [
                            "Computing Careers",
                            "Computational Thinking",
                            "Designing Algorithms",
                            "Variables and Data Flow",
                            "Working with Objects",
                        ],
                        "week_2": [
                            "Functions",
                            "Functions with Parameters",
                            "Introduction to Loops",
                            "Conditional Statements",
                            "Algorithms IRL",
                        ],
                        "week_3": [
                            "Decomposition",
                            "Two-Way Selection",
                            "Pixels of Me Project",
                        ],
                    },
                    "learning_outcomes": [
                        "Write and sequence Python commands.",
                        "Define and call functions to break problems into reusable parts.",
                        "Use loops and conditionals to make programs more efficient and responsive.",
                        "Apply computational thinking strategies like decomposition and pattern recognition to solve programming challenges.",
                        "Reflect on how AI systems follow instructions and make decisions using rules and logic.",
                    ],
                    "unit_project": (
                        "Students design a digital artifact using Python that represents an "
                        "aspect of their identity, such as a hobby, career aspiration, or "
                        "favorite story. They plan their design with pseudocode, break it into "
                        "components, and implement it using functions, loops, and conditionals."
                    ),
                    "csta_standards": [
                        "3A-AP-13",
                        "3A-AP-15",
                        "3A-AP-16",
                        "3A-AP-17",
                        "3A-AP-19",
                        "3A-AP-22",
                        "3A-AP-23",
                        "3A-IC-24",
                        "3A-IC-25",
                        "3A-IC-26",
                    ],
                },
                {
                    "number": 3,
                    "title": "AI and the Systems That Power It",
                    "class_periods": 15,
                    "description": (
                        "Students investigate how computing systems work by exploring the "
                        "roles of hardware and software in processing information. They "
                        "analyze how inputs, outputs, storage, and processing interact within "
                        "real-world systems and AI-powered technologies. Through hands-on "
                        "exploration and debugging challenges, students build mental models "
                        "of how computers and devices function, practice abstraction to manage "
                        "complexity, and reflect on how their personal experiences and values "
                        "can shape future pathways in computing."
                    ),
                    "topics": [
                        "Hardware",
                        "Software",
                        "Data Processing",
                        "IoT",
                        "Emerging Technologies",
                    ],
                    "lessons": {
                        "week_1": [
                            "Introduction to Computer Systems",
                            "Hardware",
                            "Troubleshooting and Optimizing Hardware",
                            "Software and Operating Systems",
                            "Troubleshooting and Optimizing Software",
                        ],
                        "week_2": [
                            "Build a Computer System",
                            "Data in Computer Systems",
                            "Processing Data in a Computer System",
                            "How AI Uses Data",
                            "IoT and Emerging Technologies",
                        ],
                        "week_3": [
                            "User Testing",
                            "Just Because We Can, Should We?",
                            "Nobel in AI Project",
                        ],
                    },
                    "learning_outcomes": [
                        "Describe how hardware and software components work together to input, store, process, and output information.",
                        "Identify examples of computing systems in everyday life and explain how they support AI applications.",
                        "Use abstraction and decomposition to explore how systems function and how problems are solved.",
                        "Apply debugging strategies to identify and fix issues in systems.",
                        "Explore computing careers and reflect on how personal interests and values connect to different pathways in tech.",
                    ],
                    "unit_project": (
                        "Students design an innovative computer system to address one of the "
                        "UN's Sustainable Development Goals. They create a product that "
                        "explores and integrates user profiles, relevant data, computer system "
                        "flowcharting, and ethical considerations."
                    ),
                    "csta_standards": [
                        "3A-CS-01",
                        "3A-CS-02",
                        "3A-CS-03",
                        "3A-DA-10",
                        "3A-AP-13",
                        "3A-AP-22",
                        "3A-AP-23",
                        "3A-IC-24",
                        "3A-IC-25",
                    ],
                },
                {
                    "number": 4,
                    "title": "The Fabric of the Internet and AI",
                    "class_periods": 15,
                    "description": (
                        "Students explore how the Internet works by examining how data "
                        "travels across physical and logical networks using protocols like "
                        "TCP/IP, HTTP, and DNS. They analyze how addressing systems, "
                        "packets, and redundancy enable reliable communication, and "
                        "investigate how AI improves network performance, accessibility, and "
                        "information retrieval."
                    ),
                    "topics": [
                        "Data Transmission",
                        "IP Addresses",
                        "Cybersecurity",
                        "Digital Divide",
                    ],
                    "lessons": {
                        "week_1": [
                            "Introduction to the Internet",
                            "Sending Bits",
                            "IP Addresses",
                            "Routers and Redundancy",
                            "Packets",
                        ],
                        "week_2": [
                            "HTTP and DNS",
                            "The Digital Divide",
                            "Internet Access Advocacy Campaign Project",
                        ],
                        "week_3": [
                            "Network Security",
                            "Emerging Technologies",
                            "Network Security Risk Assessment Project",
                        ],
                    },
                    "learning_outcomes": [
                        "Explain how data is transmitted across networks using addressing, packets, and common protocols.",
                        "Describe how the Internet's layered structure supports reliable and scalable communication.",
                        "Identify how AI is used to improve Internet systems, including content filtering, routing, and accessibility.",
                        "Analyze how design decisions in Internet infrastructure affect access, speed, and reliability.",
                        "Evaluate the societal impact of networked technologies and the role of AI in shaping online experiences.",
                    ],
                    "unit_projects": [
                        "Internet Access Advocacy Campaign",
                        "Network Security Risk Assessment",
                    ],
                    "csta_standards": [
                        "3A-NI-04",
                        "3A-NI-05",
                        "3A-AP-22",
                        "3A-IC-24",
                    ],
                },
                {
                    "number": 5,
                    "title": "AI-Powered Threats and Defenses",
                    "class_periods": 15,
                    "description": (
                        "Cybersecurity is a fast-changing field shaped by evolving threats, "
                        "intelligent systems, and the professionals who work to defend digital "
                        "infrastructure. Students take a systems-level look at how cyberattacks "
                        "happen, how defenses are built, and how artificial intelligence is "
                        "reshaping both offense and defense. Students analyze common attack "
                        "types such as phishing, malware, and denial-of-service, and examine "
                        "how AI is used in defense strategies, such as detecting anomalies, "
                        "managing access, and adapting authentication."
                    ),
                    "topics": [
                        "Privacy",
                        "Security Risks",
                        "Ethical Computing",
                        "Encryption",
                    ],
                    "lessons": {
                        "week_1": [
                            "Introduction to Cybersecurity",
                            "Cybersecurity Threats",
                            "Phishing and Password Attacks",
                            "Phishing with AI",
                            "Successful Cybersecurity Stories",
                        ],
                        "week_2": [
                            "Confidentiality, Integrity, and Availability",
                            "Authentication, Authorization, and Accounting",
                            "AAA and AI",
                            "Encryption",
                            "AI in Encryption",
                        ],
                        "week_3": [
                            "Security vs Usability",
                            "Layered Defenses",
                            "Designing Secure Systems Project",
                        ],
                    },
                    "learning_outcomes": [
                        "Explain how different types of cybersecurity attacks work, including how AI is used to enhance or scale these threats.",
                        "Describe how AI is used in cybersecurity tools to detect, prevent, or respond to attacks.",
                        "Analyze cybersecurity scenarios using concepts such as system vulnerabilities, authentication, and data protection.",
                        "Apply computational thinking strategies to examine cybersecurity threats, vulnerabilities, and defenses.",
                        "Evaluate tradeoffs between usability and security in the design of digital systems.",
                        "Propose security design improvements that consider both human-centered design principles and their impact on diverse users and communities.",
                        "Describe cybersecurity career roles and how professionals use AI tools in their work.",
                    ],
                    "unit_project": (
                        "Students analyze a realistic security scenario, identify potential risks "
                        "or vulnerabilities, and propose strategies to protect data, systems, or "
                        "users. They use AI as a support tool to explore threats, test ideas, or "
                        "refine explanations."
                    ),
                    "csta_standards": [
                        "3A-NI-06",
                        "3A-NI-07",
                        "3A-NI-08",
                        "3A-AP-22",
                        "3A-IC-24",
                    ],
                },
                {
                    "number": 6,
                    "title": "Introduction to Data Science",
                    "class_periods": 14,
                    "description": (
                        "Students build foundational data science skills by collecting, "
                        "organizing, visualizing, and interpreting data to answer meaningful "
                        "questions. They learn how to clean and analyze datasets using tools "
                        "like charts and summaries, and reflect on the role of data in shaping "
                        "understanding. Throughout the unit, students explore how AI systems "
                        "analyze data at scale, make predictions, and influence decision-making."
                    ),
                    "topics": [
                        "Data Questions",
                        "Data Cleaning and Analysis",
                        "Visualizations",
                        "Data Stories",
                        "Ethical Considerations",
                    ],
                    "lessons": {
                        "week_1": [
                            "Introduction to Data Science",
                            "Making Sense of Data",
                            "Ethical Data Collection",
                            "Data Rights",
                            "Effective Data Questions",
                        ],
                        "week_2": [
                            "Data Storytelling",
                            "Introduction to Data Visualization",
                            "Data Cleaning and Analysis Techniques",
                            "Data Interpretation",
                            "More Visualization Techniques",
                        ],
                        "week_3": [
                            "Crafting Stories with Data Project",
                        ],
                    },
                    "learning_outcomes": [
                        "Ask and refine questions that can be answered with data.",
                        "Collect, clean, and organize data to prepare it for analysis.",
                        "Use visualizations to identify patterns and communicate insights.",
                        "Interpret data in context and evaluate the strengths and limitations of conclusions.",
                        "Explain how AI systems use data to make predictions and support decision-making.",
                    ],
                    "unit_project": (
                        "Students explore a personally relevant or community-based issue "
                        "through data analysis, transforming raw data into meaningful "
                        "narratives. The project guides students through the data science "
                        "process — from identifying research questions to visualizing trends "
                        "and presenting insights."
                    ),
                    "csta_standards": [
                        "3A-DA-11",
                        "3A-AP-13",
                        "3A-AP-22",
                        "3A-AP-23",
                        "3A-IC-24",
                    ],
                },
            ],
        },
        "semester_2": {
            "title": "AI Foundations Semester 2",
            "status": "DRAFT",
            "overview": (
                "AI Foundations Semester 2 equips students to become intentional designers "
                "who work alongside AI to build meaningful, interactive web apps. Students "
                "learn JavaScript while using AI to generate, adapt, and refine code across "
                "HTML, CSS, and JavaScript, developing computational thinking, "
                "human-centered design, and systems thinking skills. Across a progression "
                "of projects, they design and build interactive applications that are both "
                "technically functional and ethically informed."
            ),
            "learning_outcomes": [
                "Apply core JavaScript concepts (variables, functions, conditionals, loops, arrays, objects, and state management) to design and implement interactive applications.",
                "Demonstrate judgment in selecting coding strategies by deciding when to write code independently, adapt existing code, or direct AI, and explain how these choices support their understanding and goals.",
                "Decompose problems and abstract patterns to structure solutions, and debug code through iterative refinement.",
                "Design user-centered applications that demonstrate usability, accessibility, and alignment with identified user needs.",
                "Critique AI outputs for bias, accuracy, and alignment with user goals, and justify design decisions that promote safety, transparency, and user agency.",
                "Reflect on their design process to explain how their choices connect to personal values, community needs, and responsible technology creation.",
            ],
            "units": [
                {
                    "number": 1,
                    "title": "AI-Generated Design",
                    "class_periods": 15,
                    "description": (
                        "Students begin by stepping into the role of designers, learning that "
                        "effective digital experiences start with empathy for a user. They apply "
                        "computational thinking to plan multi-page web apps, create wireframes, "
                        "and build prototypes using AI."
                    ),
                    "topics": [
                        "Human-Centered Design",
                        "Wireframing",
                        "Decomposition and Abstraction",
                        "Accessibility",
                        "Design Accountability",
                    ],
                    "lessons": {
                        "week_1": [
                            "Introduction to Web Apps",
                            "The User's Experience",
                            "Build Your First Web Page with AI",
                            "Finding Your Style",
                            "Brand Identity",
                        ],
                        "week_2": [
                            "Intro to CSS",
                            "Meet Your User",
                            "Site Maps",
                            "Accessibility in Design",
                            "Wireframes",
                        ],
                        "week_3": [
                            "From Wireframes to Layouts",
                            "Designing for Responsiveness",
                            "Digital Magazine Project",
                        ],
                    },
                    "learning_outcomes": [
                        "Define a problem from a specific user's perspective.",
                        "Apply computational thinking concepts of decomposition, pattern recognition, and abstraction to plan a web app's structure.",
                        "Create a visual representation (e.g., wireframe) of a multi-page web app that responds to a defined user need.",
                        "Plan a cohesive, multi-page user journey by designing for consistent navigation and visual style.",
                        "Write descriptive prompts to generate individual, responsive, and accessible HTML/CSS components.",
                        "Evaluate an AI-generated layout for its clarity, purpose, responsiveness, and accessibility.",
                        "Develop strategies for debugging AI-generated outputs, including refining prompts and reverting to previous versions.",
                        "Explain the difference between HTML for structure and CSS for styling.",
                        "Describe how design tasks relate to the professional roles of UX and UI designers.",
                    ],
                    "unit_project": (
                        "Students act as web designers creating a multi-page digital magazine "
                        "for a fictional user or community. They plan the structure and layout "
                        "of multiple pages, then use AI in Guide mode to generate the necessary "
                        "HTML and CSS components, building a functional, responsive, and "
                        "accessible website."
                    ),
                    "csta_standards": [
                        "3A-AP-17",
                        "3A-AP-21",
                        "3A-AP-23",
                        "3A-IC-24",
                        "3A-IC-25",
                    ],
                },
                {
                    "number": 2,
                    "title": "AI and Algorithmic Decisions",
                    "class_periods": 15,
                    "description": (
                        "Students bring their designs to life with JavaScript, learning "
                        "event-driven programming, variables, conditionals, and functions. "
                        "They use flowcharts to plan algorithms, practice systematic debugging, "
                        "and build confidence in reasoning about logic and interactivity. A "
                        "central theme is developing judgment about how to approach "
                        "problems — when to persist independently and when to seek support."
                    ),
                    "topics": [
                        "Event-Driven Programming",
                        "Variables",
                        "Conditionals",
                        "Functions",
                        "Algorithmic Thinking",
                        "Debugging",
                    ],
                    "lessons": {
                        "week_1": [
                            "Interactivity in Web Apps",
                            "Making a Button Respond",
                            "Variables and Live Updates",
                            "Writing Reusable Functions",
                            "Making Decisions with If/Else",
                        ],
                        "week_2": [
                            "Functions with Parameters",
                            "Building More Dynamic Pages",
                            "Nested Conditionals for Complex Logic",
                            "Combining Conditions with AND/OR",
                            "Adding NOT and Complex Conditions",
                        ],
                        "week_3": [
                            "Reactive Logic Project",
                        ],
                    },
                    "learning_outcomes": [
                        "Design a user interaction flow that involves conditional logic and considers simple trade-offs between different outcomes.",
                        "Model an algorithm using a flowchart to plan the logic of a user interaction.",
                        "Write JavaScript that uses event handlers, variables, conditional statements, and functions to control program behavior.",
                        "Apply debugging strategies, with and without AI assistance, to persevere through challenges and fix errors in JavaScript code.",
                        "Use AI as a collaborative partner to brainstorm, debug, and refine code.",
                        "Develop a personal framework for deciding when to write code themselves and when to seek AI assistance.",
                        "Describe how the tasks of planning, writing, and testing interactive code relate to the professional roles of a Front-End Developer and QA Engineer.",
                    ],
                    "unit_project": (
                        "Students act as Front-End Developers and QA Engineers to design "
                        "and implement a badge-awarding system in a web app of their choice. "
                        "They plan their logic with a flowchart, then translate it into JavaScript "
                        "functions, variables, and conditionals."
                    ),
                    "csta_standards": [
                        "3A-AP-13",
                        "3A-AP-15",
                        "3A-AP-16",
                        "3A-AP-17",
                        "3A-AP-21",
                        "3A-AP-23",
                        "3A-IC-24",
                        "3A-IC-25",
                    ],
                },
                {
                    "number": 3,
                    "title": "Building Data-Driven Systems with AI",
                    "class_periods": 15,
                    "description": (
                        "Students move from coding single interactions to creating applications "
                        "that manage collections of information. They represent real-world data "
                        "with arrays and objects, design features such as search, sort, and "
                        "filter, and begin to analyze how datasets shape user experience. "
                        "Ethical reflection is emphasized as they examine how bias or missing "
                        "perspectives in data can impact fairness and inclusivity."
                    ),
                    "topics": [
                        "Arrays and Objects",
                        "Data Modeling",
                        "Searching and Filtering",
                        "Dataset Bias",
                        "Ethical Data Use",
                    ],
                    "lessons": {
                        "week_1": [
                            "Intro to Data Structures",
                            "Turning Data into Displays",
                            "Basic Array Methods",
                            "Objects for Real-World Data",
                            "Lists of Objects",
                        ],
                        "week_2": [
                            "Rendering Lists of Objects",
                            "Evaluating Fairness and Accessibility",
                            "Filtering",
                            "Searching",
                            "Sorting and Chaining",
                        ],
                        "week_3": [
                            "Value Explorer Project",
                        ],
                    },
                    "learning_outcomes": [
                        "Apply abstraction to model real-world information as structured data using JavaScript arrays and objects.",
                        "Define a schema for a dataset by identifying its fields, types, and constraints.",
                        "Use arrays and objects to organize, access, and update collections of information in a program.",
                        "Apply decomposition and algorithmic reasoning to design procedures that operate on datasets, such as searching, sorting, or filtering.",
                        "Analyze AI-generated code scaffolds, complete missing logic, and evaluate AI outputs for clarity and correctness.",
                        "Identify examples of bias or missing context in datasets and explain how they can lead to unfair or misleading user experiences.",
                        "Analyze and revise datasets or AI-generated scaffolds to address ethical concerns and improve fairness, usability, and trustworthiness.",
                        "Describe how working with structured data relates to professional roles such as UX Researcher, Product Manager, and entry-level data-focused roles.",
                    ],
                    "unit_project": (
                        "Students act as Product Designers and Data Stewards to create a "
                        "'Value Explorer' app based on a topic of their choice. They design a "
                        "schema, curate a dataset, and build a web app with multi-criteria "
                        "sorting algorithms."
                    ),
                    "csta_standards": [
                        "3A-AP-14",
                        "3A-AP-17",
                        "3A-AP-18",
                        "3A-AP-21",
                        "3A-AP-23",
                        "3A-DA-10",
                        "3A-IC-24",
                        "3A-IC-25",
                    ],
                },
                {
                    "number": 4,
                    "title": "Iterating with AI",
                    "class_periods": 15,
                    "description": (
                        "Students deepen their programming with loops and iterative reasoning, "
                        "creating dynamic features like filters and views that allow users to "
                        "explore information. They strengthen their decomposition and debugging "
                        "skills while analyzing how algorithmic filtering can influence "
                        "transparency, trust, and user agency."
                    ),
                    "topics": [
                        "Loops",
                        "Interactive Features (Filters and Views)",
                        "Debugging Iteration",
                        "Algorithmic Filtering and Fairness",
                    ],
                    "lessons": {
                        "week_1": [
                            "Intro to Loops",
                            "Counted Repetition",
                            "Open-Ended Repetition",
                            "Displaying Arrays as List Views",
                            "Displaying Objects as Cards",
                        ],
                        "week_2": [
                            "Filtering and Transparency",
                            "Pure Functions vs Side Effects",
                            "Copy, Don't Mutate",
                            "Inclusive Filters and Clear Labels",
                            "Schema Design for Simple Features",
                        ],
                        "week_3": [
                            "Interactive Data Dashboard Project",
                        ],
                    },
                    "learning_outcomes": [
                        "Explain how iteration and loops work by describing how repeated logic enables programs to process entire collections of data rather than single items.",
                        "Implement loops in JavaScript to create interactive features such as filters, searches, and views that allow users to explore and control information.",
                        "Apply decomposition by breaking a complex, loop-driven feature into smaller, testable procedures.",
                        "Debug repeated logic by tracing iteration step-by-step, identifying common issues.",
                        "Evaluate the impact of algorithmic filtering by analyzing how design choices affect fairness, transparency, inclusivity, and user trust.",
                        "Make informed coding decisions by documenting when they adapt suggested code and when they write or refactor loop logic independently.",
                    ],
                    "unit_project": (
                        "Students act as designers of a public-facing dashboard that summarizes "
                        "and filters a dataset of their choice. They implement the dashboard "
                        "using JavaScript loops to power the filtering logic."
                    ),
                    "csta_standards": [
                        "3A-AP-14",
                        "3A-AP-15",
                        "3A-AP-17",
                        "3A-AP-21",
                        "3A-AP-23",
                        "3A-IC-24",
                        "3A-IC-25",
                    ],
                },
                {
                    "number": 5,
                    "title": "Designing Reliable Apps with AI and APIs",
                    "class_periods": 14,
                    "description": (
                        "Students expand their understanding of web apps by connecting them "
                        "to external data sources through APIs. They learn that modern "
                        "applications rarely operate in isolation; instead, they depend on "
                        "information and services provided by larger systems. By practicing "
                        "asynchronous programming and error handling, students develop the "
                        "technical skills to fetch, display, and manage data that comes from "
                        "beyond their own code."
                    ),
                    "topics": [
                        "Async Programming",
                        "API Integration",
                        "Error Handling",
                        "Status Indicators",
                        "Defensive Design",
                        "Local vs Remote Data",
                        "Trust in Data Systems",
                    ],
                    "lessons": {
                        "week_1": [
                            "Where Data Comes From",
                            "Why Apps Wait",
                            "Getting Data Online",
                            "Making Steps Clear",
                            "Making Sense of Data",
                        ],
                        "week_2": [
                            "Showing Data on the Page",
                            "When Things Break",
                            "Catching Problems",
                            "Keeping Users Informed",
                            "Local vs Live Data",
                        ],
                        "week_3": [
                            "Explore-Style App Project",
                            "Tap for More: Explore-Style App Project",
                        ],
                    },
                    "learning_outcomes": [
                        "Write asynchronous JavaScript using async/await to fetch and display data from an external API.",
                        "Use try/catch blocks to handle errors and provide clear, user-friendly feedback.",
                        "Compare local datasets with remote API data, recognizing trade-offs in reliability, control, and flexibility.",
                        "Design user interfaces that communicate system status through loading indicators, error messages, and empty-result states.",
                        "Explain how external APIs position their apps as part of larger systems and consider the implications of depending on outside data sources.",
                        "Apply defensive design strategies to ensure apps remain usable and trustworthy even when data is delayed, incomplete, or unavailable.",
                    ],
                    "unit_project": (
                        "Students design an Explore-style web app inspired by platforms like "
                        "Instagram, TikTok, or Yelp. They connect their app to a real public "
                        "API to display live data, handling real-world challenges like loading "
                        "delays, missing data, and errors."
                    ),
                    "csta_standards": [
                        "3A-AP-15",
                        "3A-AP-17",
                        "3A-AP-18",
                        "3A-CS-03",
                        "3A-DA-10",
                        "3A-IC-24",
                    ],
                },
                {
                    "number": 6,
                    "title": "Web Apps with AI Capstone Project",
                    "class_periods": 10,
                    "description": (
                        "Unit 6 is the capstone of Semester 2, where students synthesize "
                        "their learning to design and build a complete web app with a clear "
                        "purpose and audience. They integrate technical fluency, "
                        "human-centered design, and AI literacy, making choices that are "
                        "transparent, ethical, and aligned with their values."
                    ),
                    "topics": [
                        "App Planning",
                        "State & Data Flow",
                        "Interactive Features",
                        "Human-Centered Design",
                        "Iterative Development",
                        "Systems Thinking",
                        "Documentation & Ethics",
                    ],
                    "lessons": {
                        "week_1": [
                            "Web App with AI Capstone Project",
                        ],
                        "week_2": [
                            "Web App with AI Capstone Project",
                        ],
                    },
                    "learning_outcomes": [
                        "Plan a complete web app with a clear audience and purpose.",
                        "Design interactive features that integrate local data and external APIs to support user goals.",
                        "Write well-structured JavaScript that manages state, processes input, and supports dynamic behaviors.",
                        "Apply human-centered design principles to ensure usability, accessibility, and responsiveness.",
                        "Analyze their application as a system, explaining how components interact to shape the user experience.",
                        "Document their development process, including how prompts and edits evolved during development.",
                        "Reflect on the ethical implications of their application and propose strategies to address risks and trade-offs.",
                        "Demonstrate the mindset of an intentional designer, showing confidence, adaptability, and values-driven decision-making.",
                    ],
                    "unit_project": (
                        "Students design and build a complete, public-facing web application "
                        "that reflects their interests while showcasing the full range of skills "
                        "developed throughout the unit. Acting in rotating professional roles, "
                        "such as software engineer, UX designer, and product manager, "
                        "students iteratively design, prototype, and implement an app that "
                        "integrates live data from an external API."
                    ),
                    "csta_standards": [
                        "3A-AP-16",
                        "3A-AP-17",
                        "3A-AP-19",
                        "3A-AP-21",
                        "3A-AP-23",
                        "3A-DA-11",
                        "3A-IC-24",
                    ],
                },
            ],
        },
    },
    "positioning": {
        "level": "Entry-level",
        "accessibility": (
            "Accessible to beginners with no prior programming knowledge. "
            "Also provides opportunities for students with some background "
            "in computing to deepen their understanding of key topics."
        ),
        "scope": "Broad exploratory course covering multiple Digital Technology sub-clusters",
        "bridge_to": "AP Computer Science A (CSA)",
        "pathway_connections": [
            "AP Computer Science A",
            "AP Computer Science Principles",
            "Data Science pathways",
            "Cybersecurity pathways",
            "Software Development pathways",
            "Web Development pathways",
        ],
    },
    "key_features": [
        "No prerequisites required",
        "Hands-on Python programming (Semester 1)",
        "JavaScript and web app development (Semester 2)",
        "AI concepts integrated throughout",
        "Human-centered design emphasis",
        "Covers breadth of digital technology",
        "Prepares students for multiple pathways",
        "Free and open curriculum",
        "Modular design for flexibility",
        "Student-centered pedagogy",
        "Ethical and societal awareness in every unit",
        "Collaborative, supportive learning environments",
    ],
    "alignment": {
        "career_cluster": "Digital Technology",
        "sub_clusters_covered": [
            "Data Science & Artificial Intelligence",
            "Software Solutions",
            "Network Systems & Cybersecurity",
            "Information Technology (IT) Support & Services",
            "Web & Cloud",
        ],
        "standards": [
            "CSTA K-12 Computer Science Standards",
            "ISTE Standards for Students",
        ],
    },
}
