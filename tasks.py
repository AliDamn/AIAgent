from crewai import Task, Crew
from agents import (
    chatbot_analyst,
    create_business_researcher,
    create_requirement_analyst,
    create_diagram_architect,
    create_requirements_validator,
    create_confluence_publisher
)

def create_tasks(topic: str, user_input: str):
    
    business_researcher = create_business_researcher(topic)
    requirement_analyst = create_requirement_analyst(topic)
    diagram_architect = create_diagram_architect(topic)
    requirements_validator = create_requirements_validator(topic)
    confluence_publisher = create_confluence_publisher(topic)
    
    collect_requirements_dialogue = Task(
        description=f"""Based on the user's initial input: "{user_input}", conduct a comprehensive analysis to understand their business need.
        
        Since this is an automated system, you should analyze the business need and create a structured summary as if you conducted a dialogue.
        Gather complete information about:
        - The specific business problem or need (analyze from: {user_input})
        - Current process (AS-IS) - how things work now (infer from banking best practices)
        - Desired outcome (TO-BE) - what they want to achieve
        - Key stakeholders involved (typical for banking credit processing)
        - Pain points and challenges (common issues in manual credit processing)
        - Business constraints and regulations (banking sector standards)
        - Success criteria and KPIs (typical metrics for credit automation)
        - Scope boundaries (what's in and out of scope)
        
        IMPORTANT: Create a detailed, realistic dialogue summary and structured analysis based on the business need: {user_input}.
        Be thorough and include specific details relevant to credit application automation in banking.""",
        agent=chatbot_analyst,
        expected_output="""Complete dialogue transcript and structured summary including:
        - Business problem statement (clear and specific based on: {user_input})
        - Current AS-IS process description (detailed manual process)
        - Desired TO-BE state (automated process)
        - Identified stakeholders with their roles (Customer, Credit Analyst, Risk Manager, Compliance Officer, etc.)
        - Business objectives and goals (reduce processing time, improve accuracy, ensure compliance)
        - Constraints (regulatory, technical, organizational)
        - Pain points and challenges (manual errors, slow processing, high costs)
        - Success metrics and KPIs (processing time reduction, error rate, customer satisfaction)
        - Scope definition (in-scope and out-of-scope items)
        - Initial glossary of business terms"""
    )
    
    gather_business_text = Task(
        description=f"""Based on the dialogue transcript from the previous task, conduct a deep investigation of the business problem: {topic}.
        
        Use the information collected in the dialogue to analyze and expand on:
        - Detailed stakeholder analysis (roles, responsibilities, interests)
        - Regulatory and compliance requirements specific to banking sector
        - Related systems and their interactions
        - Detailed workflow analysis
        - Risk identification
        - Dependencies and integration points
        
        IMPORTANT: You MUST use the context from the previous dialogue task. Review what was collected and build upon it.
        Produce a comprehensive structured summary of the business environment.""",
        agent=business_researcher,
        context=[collect_requirements_dialogue],
        expected_output="""Comprehensive structured context document including:
        - Detailed problem statement with root cause analysis
        - Complete stakeholder map with roles, responsibilities, and interests
        - Business objectives with priorities
        - Regulatory and compliance constraints (banking sector specific)
        - Technical and organizational constraints
        - Detailed AS-IS process description with pain points
        - Risk analysis
        - Related systems and integration points
        - Complete glossary of terms"""
    )
    extract_requirements = Task(
        description=f"""Convert the researched business context and dialogue information into a formal,
comprehensive Business Requirements Document (BRD) for: {topic}.
        
        IMPORTANT: Use ALL context from previous tasks - the dialogue transcript and business context research.
        
        Create a detailed BRD following banking sector best practices with:
        - Executive summary
        - Goal and background (why this project is needed)
        - Detailed business problem description
        - Business objectives (SMART format)
        - Functional requirements (detailed, numbered, testable) - at least 8-10 functional requirements
        - Non-functional requirements (performance, security, compliance, usability)
        - Business rules (clear, unambiguous) - at least 5 business rules
        - KPIs and success metrics (quantifiable)
        - Acceptance criteria for each requirement
        - In-scope and out-of-scope items (clearly defined)
        - Assumptions and dependencies
        - Risk register
        
        Ensure all requirements are specific, measurable, and aligned with banking sector standards.
        DO NOT just summarize - create a complete, detailed BRD document.""",
        agent=requirement_analyst,
        context=[collect_requirements_dialogue, gather_business_text],
        expected_output="""Complete, detailed BRD document including:
        - Executive Summary
        - Goal & Background (context and business drivers)
        - Detailed Business Problem Description
        - Business Objectives (SMART format)
        - Functional Requirements (numbered, detailed, testable) - minimum 8 requirements
        - Non-Functional Requirements (performance, security, compliance, usability)
        - Business Rules (clear and unambiguous) - minimum 5 rules
        - KPIs and Success Metrics (quantifiable with targets)
        - Acceptance Criteria (for each requirement)
        - In-Scope / Out-of-Scope Lists (clearly defined boundaries)
        - Assumptions and Dependencies
        - Risk Register"""
    )
    generate_use_cases_and_user_stories = Task(
        description=f"""Based on the BRD and requirements for {topic}, generate comprehensive
Use Case specifications and structured User Stories.
        
        IMPORTANT: Use the BRD from the previous task. For EACH functional requirement in the BRD:
        - Create formal Use Case specifications with:
          * Use Case ID (e.g., UC-001) and name
          * Actors (primary and secondary)
          * Preconditions
          * Main flow (detailed step-by-step, at least 5-7 steps)
          * Alternative flows (at least 2-3 alternative scenarios)
          * Exception flows (error handling scenarios)
          * Postconditions
          * Business rules
          * Success criteria
        
        - Create User Stories following INVEST principles:
          * Story ID (e.g., US-001)
          * As a [role], I want [goal], So that [benefit]
          * Detailed acceptance criteria (Gherkin format: Given-When-Then) - at least 3 scenarios
          * Definition of Done
        
        CRITICAL: You MUST generate actual Use Cases and User Stories content, not just say "successfully created".
        Generate at least 5-8 detailed Use Cases and 8-12 User Stories.
        Ensure complete traceability: every functional requirement must be traced to at least one Use Case.
        All User Stories must be independent, negotiable, valuable, estimable, small, and testable.""",
        agent=requirement_analyst,
        context=[extract_requirements],
        expected_output="""Complete Use Cases and User Stories documentation with FULL CONTENT:
        - Use Case List (with IDs and names) - minimum 5 use cases
        - Full Use Case Descriptions for each use case (detailed, not just summaries):
          * Use Case ID, Name, Description
          * Actors (Primary, Secondary)
          * Preconditions
          * Main Flow (detailed step-by-step, 5-7 steps minimum)
          * Alternative Flows (all variations, 2-3 minimum)
          * Exception Flows (error handling scenarios)
          * Postconditions
          * Business Rules
          * Success Criteria
        - User Stories (INVEST compliant) - minimum 8 stories:
          * Story ID
          * As a [role], I want [goal], So that [benefit]
          * Acceptance Criteria (Gherkin: Given-When-Then, 3+ scenarios per story)
          * Definition of Done
        - Requirements Traceability Matrix (requirement -> use case -> user story)"""
    )
    create_process_diagrams = Task(
        description=f"""Using the collected requirements, BRD, Use Cases, and business context for {topic},
design comprehensive AS-IS and TO-BE BPMN 2.0 diagrams, activity diagrams, use-case diagrams,
and sequence diagrams.
        
        IMPORTANT: Use ALL context from previous tasks - BRD, Use Cases, and business context.
        
        Create detailed diagrams that:
        - AS-IS BPMN: Show current process with all steps, decision points, actors, and pain points clearly marked
        - TO-BE BPMN: Show proposed improved process with automation, optimization, and clear improvements
        - Activity Diagram: Show detailed activity flows for key processes
        - Use Case Diagram: Show all actors and use cases with relationships
        - Sequence Diagram: Show interactions between actors and system for key use cases (at least 2-3 sequence diagrams)
        
        Ensure all diagrams:
        - Are consistent with requirements and Use Cases from previous tasks
        - Eliminate ambiguities
        - Include all decision points and alternative flows
        - Show clear improvement from AS-IS to TO-BE
        - Are specific to the business problem: {topic}
        
        Output diagrams in Mermaid syntax for easy rendering. Include ALL diagrams, not just summaries.""",
        agent=diagram_architect,
        context=[extract_requirements, generate_use_cases_and_user_stories],
        expected_output="""Complete set of process diagrams with FULL Mermaid code:
        - AS-IS BPMN Process Diagram (detailed, showing current state with pain points)
        - TO-BE BPMN Process Diagram (detailed, showing improved process with automation)
        - Activity Diagram (for key business processes)
        - Use Case Diagram (showing all actors and use cases)
        - Sequence Diagrams (for at least 2-3 critical use cases showing actor-system interactions)
        All diagrams in Mermaid syntax, properly formatted and documented"""
    )
    validate_requirements_quality = Task(
        description=f"""Perform a comprehensive quality review of all produced business artifacts for {topic}.
        
        IMPORTANT: Review ALL previous artifacts - BRD, Use Cases, User Stories, and Diagrams.
        
        Evaluate:
        - Clarity: Are all requirements clear and unambiguous?
        - Consistency: Are there contradictions between documents?
        - Completeness: Are all necessary requirements captured?
        - Traceability: Can each requirement be traced from business objective to implementation?
        - Testability: Can each requirement be tested/verified?
        - Alignment: Do requirements align with business goals?
        - Banking Sector Compliance: Do requirements meet regulatory standards?
        
        Check specifically for:
        - Missing acceptance criteria (all must be quantifiable)
        - Unclear definitions of key terms
        - Missing edge cases and exception handling
        - Incomplete BPMN diagrams (missing decision points, alternative flows)
        - Weak user stories (not INVEST compliant)
        - Missing non-functional requirements
        - Incomplete traceability matrix
        
        Provide actionable recommendations for improvement with specific examples.""",
        agent=requirements_validator,
        context=[extract_requirements, generate_use_cases_and_user_stories, create_process_diagrams],
        expected_output="""Comprehensive Validation Report including:
        - Executive Summary
        - Issues Found (categorized by severity: Critical, High, Medium, Low) - with specific examples
        - Contradictions or Missing Details (with specific examples from documents)
        - Unclear Definitions (list of terms needing clarification)
        - Missing Acceptance Criteria (for each affected requirement)
        - Incomplete Diagrams (specific gaps identified)
        - Traceability Gaps (missing links in traceability matrix)
        - Recommended Fixes (actionable, prioritized)
        - Compliance Assessment (banking sector standards)
        - Overall Quality Score and Readiness Assessment"""
    )
    publish_to_confluence = Task(
        description=f"""Publish the complete business analysis documentation for {topic} to Confluence.
        
        CRITICAL: You MUST compile ALL content from previous tasks:
        - Dialogue summary from chatbot
        - Business context research
        - Complete BRD document
        - All Use Cases with full details
        - All User Stories with acceptance criteria
        - All diagrams (AS-IS, TO-BE, Activity, Use Case, Sequence)
        - Validation report
        
        Create a comprehensive documentation structure:
        - Parent page: Project Index with overview
        - Child pages: BRD, Requirements/Use Cases, Diagrams, Validation Report
        
        IMPORTANT: Include the ACTUAL CONTENT from all previous tasks, not just summaries.
        Format everything properly with:
        - Professional formatting following banking sector documentation standards
        - Proper hierarchy and navigation
        - All diagrams embedded and properly formatted (include the actual Mermaid code)
        - Tables, lists, and structured content properly formatted
        - Metadata and labels applied
        - Cross-references and links between pages
        - All content is complete, accurate, and ready for stakeholder review
        
        DO NOT just say "I have gathered information" - actually compile and format ALL the documentation.""",
        agent=confluence_publisher,
        context=[collect_requirements_dialogue, gather_business_text, extract_requirements, 
                 generate_use_cases_and_user_stories, create_process_diagrams, validate_requirements_quality],
        expected_output="""Complete Confluence documentation structure with FULL CONTENT:
        - Project Index Page (overview, navigation, project metadata)
        - BRD Page (complete Business Requirements Document with all sections)
        - Requirements / Use Cases Page (all use cases and user stories with full details)
        - Diagrams Page (all BPMN, activity, use case, and sequence diagrams with Mermaid code)
        - Validation Report Page (complete quality assessment)
        All pages properly formatted, linked, and ready for Confluence import with actual content included""",
        output_file="report.txt"
    )
    
    return [
        collect_requirements_dialogue,
        gather_business_text,
        extract_requirements,
        generate_use_cases_and_user_stories,
        create_process_diagrams,
        validate_requirements_quality,
        publish_to_confluence
    ], [
        chatbot_analyst,
        business_researcher,
        requirement_analyst,
        diagram_architect,
        requirements_validator,
        confluence_publisher
    ]

def create_crew(topic: str, user_input: str):
    tasks, agents = create_tasks(topic, user_input)
    
    crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=True
    )
    
    return crew
