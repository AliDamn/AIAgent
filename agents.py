import os
from crewai import Agent
from crewai_tools import FileReadTool, PDFSearchTool, DOCXSearchTool, JSONSearchTool, TXTSearchTool
from crewai_tools import LlamaIndexTool, FirecrawlSearchTool, RagTool, CodeInterpreterTool, VisionTool
from crewai_tools import SerperDevTool
from llama_index.core.tools import FunctionTool
from typing import List

MAX_RESULT_LENGTH = 8000

def create_firecrawl_tool(topic: str):
    def truncated_web_search(query: str) -> str:
        try:
            base_firecrawl = FirecrawlSearchTool(
                query=query,
                api_key=os.getenv("FIRECRAWL_API_KEY"),
                limit=1,
                fetchPageContent=False
            )
            result = base_firecrawl._run(query)
            if not isinstance(result, str):
                result = str(result)
            if len(result) > MAX_RESULT_LENGTH:
                result = result[:MAX_RESULT_LENGTH] + "\n\n[Результат обрезан для экономии токенов...]"
            return result
        except Exception as e:
            return f"Ошибка при поиске: {str(e)}"
    
    firecrawl_og_tool = FunctionTool.from_defaults(
        truncated_web_search,
        name="Firecrawl Web Search",
        description="Search the web for information. Results are automatically truncated to prevent token overflow."
    )
    return LlamaIndexTool.from_tool(firecrawl_og_tool)


def search_data(topics: str) -> str:
    return f"Results for: {topics}"

og_tool = FunctionTool.from_defaults(
    search_data,
    name="DataSearchTool",
    description="Search for information in the data"
)

llama_tool = LlamaIndexTool.from_tool(og_tool)
rag_tool = RagTool(similarity_threshold=0.6, limit=2)

MAX_CHUNK_TOKENS = 4000

def chunk_text(text: str, chunk_size: int = MAX_CHUNK_TOKENS) -> List[str]:
    words = text.split()
    chunks = []
    current_chunk = []
    current_len = 0
    for word in words:
        current_chunk.append(word)
        current_len += len(word) + 1
        if current_len >= chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_len = 0
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

def safe_llm_call(agent, text: str) -> str:
    chunks = chunk_text(text, chunk_size=MAX_CHUNK_TOKENS)
    results = []
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}...")
        result = agent.ask(f"Analyze this part of the data:\n{chunk}")
        results.append(result)
    return "\n".join(results)

llm_model = "gpt-4o-mini"

chatbot_analyst = Agent(
    role="AI Business Analyst Chatbot",
    goal="""Conduct interactive dialogue with bank employees to understand their business needs,
collect requirements, clarify context, and gather all necessary information about business processes,
pain points, and desired improvements. Act as a professional business analyst chatbot that asks
clarifying questions and structures the conversation to extract complete business context.""",
    backstory="""You are an AI-powered business analyst chatbot designed to interact with internal
bank department employees. Your role is to conduct professional dialogues to understand business
situations, identify stakeholders, gather requirements, and clarify all necessary details about
business processes, constraints, regulations, and goals. You ask targeted questions to ensure
complete understanding before formalizing requirements. You work in Russian and English, adapting
to the user's language preference.""",
        llm=llm_model,
        verbose=False,
        tools=[llama_tool, rag_tool],
        max_iter=5,
        max_execution_time=600
    )

def create_business_researcher(topic: str):
    firecrawl = create_firecrawl_tool(topic)
    return Agent(
        role=f"Business Context Researcher for: {topic}",
        goal=f"""Conduct deep exploration of the business context for the specific business problem: {topic}.
Uncover hidden constraints, identify stakeholders, and gather all relevant background information.
Focus on banking sector specifics, regulations, existing processes, and pain points.
Provide clean, structured insights for further business analysis.""",
        backstory="""You are an experienced business researcher specializing in banking sector analysis.
You excel at uncovering essential details in complex banking environments. You're skilled at extracting
business rules, regulatory constraints, risks, KPIs, and AS-IS process descriptions from raw or incomplete
information. Your strong analytical intuition helps teams clarify ambiguous statements and understand
what the business truly needs in the context of banking operations.""",
        llm=llm_model,
        verbose=False,
        tools=[llama_tool, firecrawl, rag_tool],
        max_iter=3,
        max_execution_time=300
    )

business_researcher = None

def create_requirement_analyst(topic: str):
    return Agent(
        role=f"Business Requirements Analyst for: {topic}",
        goal=f"""Transform raw business information collected through dialogue into complete,
well-structured Business Requirements Documents (BRD) specifically for: {topic}.
Produce detailed BRD sections including goal, background, detailed description, scope,
business rules, KPIs, functional and non-functional requirements. Focus on banking sector
specifics and ensure all requirements are clear, testable, and implementation-ready.""",
        backstory="""You are a senior business analyst specializing in banking sector requirements
engineering. You are known for your precision and structured thinking. You excel at converting
unstructured dialogues and conversations into formal BRD documentation following industry best
practices. You identify missing elements, organize requirements into standard BA formats, ensure
clarity, consistency, and readiness for implementation. You understand banking regulations, compliance
requirements, and operational constraints.""",
        llm=llm_model,
        verbose=False,
        tools=[llama_tool, rag_tool, FileReadTool(), TXTSearchTool(), PDFSearchTool(),
               DOCXSearchTool(), JSONSearchTool()],
        max_iter=3,
        max_execution_time=300
    )

requirement_analyst = None

def create_diagram_architect(topic: str):
    return Agent(
        role=f"BPMN & Diagram Architect for: {topic}",
        goal=f"""Transform requirements and business context for {topic} into clear,
standards-compliant BPMN 2.0 diagrams, process flows, use-case diagrams, and system
interaction schemas. Create detailed AS-IS and TO-BE process diagrams that clearly
show current state and proposed improvements. Ensure all diagrams are specific to
the business problem and eliminate ambiguities.""",
        backstory="""You are a senior enterprise architect with years of experience designing
formal process diagrams for banking systems. You specialize in turning textual requirements
and business context into precise BPMN 2.0 models, UML diagrams, and high-level architecture
artifacts. Your diagrams eliminate ambiguity and ensure developers, analysts, auditors, and
stakeholders share the same understanding. You understand banking processes, compliance flows,
and operational workflows.""",
        llm=llm_model,
        verbose=False,
        tools=[rag_tool, CodeInterpreterTool(), JSONSearchTool(), VisionTool(), llama_tool],
        max_iter=3,
        max_execution_time=300
    )

diagram_architect = None

def create_confluence_publisher(topic: str):
    return Agent(
        role=f"Confluence Documentation Publisher for: {topic}",
        goal=f"""Create and update comprehensive documentation pages in Confluence for the
business analysis project: {topic}. Ensure all BRD sections, Use Cases, User Stories,
diagrams, and validation reports are properly formatted, organized with clear hierarchy,
and linked together. Apply consistent formatting, templates, and metadata following
banking sector documentation standards.""",
        backstory="""You are a documentation automation expert specializing in banking sector
documentation. You are responsible for publishing clean, well-structured materials to Confluence.
You understand how Confluence organizes pages, how to apply templates, and how to embed diagrams,
tables, and metadata. Your job is to turn the team's outputs into polished, high-quality
documentation that meets banking sector compliance and audit requirements.""",
        llm=llm_model,
        verbose=False,
        tools=[CodeInterpreterTool(), SerperDevTool(), rag_tool, TXTSearchTool(), llama_tool],
        max_iter=3,
        max_execution_time=300
    )

confluence_publisher = None

def create_requirements_validator(topic: str):
    return Agent(
        role=f"Requirements Quality Auditor for: {topic}",
        goal=f"""Review and validate all requirements, BRD sections, user stories, and BPMN
artifacts for the project: {topic}. Ensure quality, completeness, clarity, consistency,
and alignment with business objectives. Identify gaps, ambiguities, risks, and conflicts.
Verify that all acceptance criteria are quantifiable and testable, and that requirements
meet banking sector standards.""",
        backstory="""You are a senior business analyst and requirements engineer specializing
in banking sector validation. You are known for your rigorous validation skills. You specialize
in detecting ambiguous formulations, missing edge cases, unclear actors, weak acceptance criteria,
inconsistent business rules, and undocumented dependencies. Your feedback ensures that requirements
are implementation-ready, audit-compliant, and meet regulatory standards for banking operations.""",
        llm=llm_model,
        verbose=False,
        tools=[CodeInterpreterTool(), rag_tool, llama_tool],
        max_iter=3,
        max_execution_time=300
    )

requirements_validator = None

