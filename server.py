"""Main MCP server entry point with clean modular structure."""

import asyncio
import logging
import os

from fastmcp import FastMCP

from config import DEFAULT_PORT, DEFAULT_HOST
from tools.job_tools import JobTools
from tools.math_tools import MathTools
from tools.candidate_tools import CandidateTools

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

# Initialize FastMCP server
mcp = FastMCP("MCP Server on Cloud Run")

# Initialize tool instances
job_tools = JobTools()
math_tools = MathTools()
candidate_tools = CandidateTools()


# Register job description tools
@mcp.tool()
async def extract_job_requirements(jd_text: str) -> str:
    """Extract structured job requirements from job description text.
    
    Args:
        jd_text: The job description text to analyze
    
    Returns:
        JSON string containing structured job requirements including title, company, 
        location, required_qualifications, preferred_qualifications, description, 
        experience_level, and employment_type.
    """
    return await job_tools.extract_job_requirements(jd_text)


# Register mathematical operation tools
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together.
    
    Args:
        a: The first number
        b: The second number
    
    Returns:
        The sum of the two numbers
    """
    return math_tools.add(a, b)


@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers.
    
    Args:
        a: The first number
        b: The second number
    
    Returns:
        The difference of the two numbers
    """
    return math_tools.subtract(a, b)


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers.
    
    Args:
        a: The first number
        b: The second number
    
    Returns:
        The product of the two numbers
    """
    return math_tools.multiply(a, b)


# Register candidate retrieval tools
@mcp.tool()
async def find_matching_candidates(required_qualifications: str, preferred_qualifications: str = "", top_k: int = 10, enable_reranking: bool = True) -> str:
    """Find candidates matching job qualifications from LlamaCloud resume index.
    
    Args:
        required_qualifications: Comma-separated string of required qualifications (e.g., "Python, Machine Learning, 3+ years experience")
        preferred_qualifications: Comma-separated string of preferred qualifications (optional, e.g., "AWS, Docker, PhD")
        top_k: Number of top candidates to retrieve (default: 10, max: 50)
        enable_reranking: Whether to enable reranking for better results (default: True)
    
    Returns:
        JSON string containing list of matching candidates with their scores and information
    """
    return await candidate_tools.find_matching_candidates(required_qualifications, preferred_qualifications, top_k, enable_reranking)


@mcp.tool()
async def search_candidates_by_skills(skills: str, top_k: int = 10) -> str:
    """Search candidates by specific skills or keywords from LlamaCloud resume index.
    
    Args:
        skills: Comma-separated list of skills or keywords to search for (e.g., "Python, Machine Learning, AWS")
        top_k: Number of top candidates to retrieve (default: 10, max: 50)
    
    Returns:
        JSON string containing list of matching candidates with their scores and information
    """
    return await candidate_tools.search_candidates_by_skills(skills, top_k)


@mcp.tool()
async def score_candidate_qualifications(
    candidate_resume: str, 
    required_qualifications: str, 
    preferred_qualifications: str = "", 
    job_title: str = "", 
    job_description: str = ""
) -> str:
    """Score a candidate's resume against specific job qualifications using LLM evaluation.
    
    Args:
        candidate_resume: The candidate's resume text content
        required_qualifications: Comma-separated string of required qualifications (e.g., "Python, 3+ years experience, Bachelor's degree")
        preferred_qualifications: Comma-separated string of preferred qualifications (optional, e.g., "AWS, Docker, Master's degree")
        job_title: Job title for context (optional)
        job_description: Job description for context (optional)
    
    Returns:
        JSON string containing detailed scoring results for each qualification with explanations and overall feedback
    """
    return await candidate_tools.score_candidate_qualifications(
        candidate_resume, 
        required_qualifications, 
        preferred_qualifications, 
        job_title, 
        job_description
    )


async def main():
    """Main server startup function."""
    port = int(os.getenv("PORT", DEFAULT_PORT))
    logger.info(f"MCP server starting on {DEFAULT_HOST}:{port}")
    
    try:
        # Could also use 'sse' transport, host="0.0.0.0" required for Cloud Run.
        await mcp.run_async(
            transport="streamable-http", 
            host=DEFAULT_HOST, 
            port=port,
        )
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 