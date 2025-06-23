"""Candidate retrieval tools using LlamaCloud."""

import json
import logging
import traceback
from typing import Dict, Any

from services.llamacloud_service import LlamaCloudService
from models import JobDescriptionData

logger = logging.getLogger(__name__)


class CandidateTools:
    """Container class for candidate retrieval MCP tools."""
    
    def __init__(self):
        """Initialize CandidateTools with LlamaCloud service."""
        try:
            self.llamacloud_service = LlamaCloudService()
            logger.info("CandidateTools initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize CandidateTools: {e}")
            self.llamacloud_service = None
    
    async def find_matching_candidates(
        self, 
        required_qualifications: str, 
        preferred_qualifications: str = "", 
        top_k: int = 10, 
        enable_reranking: bool = True
    ) -> str:
        """Find candidates matching job qualifications from LlamaCloud resume index.
        
        Args:
            required_qualifications: Comma-separated string of required qualifications
            preferred_qualifications: Comma-separated string of preferred qualifications (optional)
            top_k: Number of top candidates to retrieve (default: 10, max: 50)
            enable_reranking: Whether to enable reranking for better results (default: True)
        
        Returns:
            JSON string containing list of matching candidates with their scores and information
        """
        logger.info(f">>> Tool: 'find_matching_candidates' called with top_k={top_k}, reranking={enable_reranking}")
        
        # Validate service availability
        if not self.llamacloud_service:
            error_msg = "LlamaCloud service is not available. Check configuration and API key."
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
        
        # Validate input parameters
        if not required_qualifications or not required_qualifications.strip():
            return json.dumps({"error": "Required qualifications cannot be empty"})
        
        # Validate top_k parameter
        if not isinstance(top_k, int) or top_k < 1 or top_k > 50:
            return json.dumps({"error": "top_k must be an integer between 1 and 50"})
        
        try:
            # Parse qualifications into lists
            required_quals = [qual.strip() for qual in required_qualifications.split(',') if qual.strip()]
            preferred_quals = [qual.strip() for qual in preferred_qualifications.split(',') if qual.strip()] if preferred_qualifications else []
            
            logger.info(f"Required qualifications: {required_quals}")
            logger.info(f"Preferred qualifications: {preferred_quals}")
            
            # Retrieve candidates from LlamaCloud using the new method
            candidates = await self.llamacloud_service.retrieve_candidates_by_qualifications(
                required_qualifications=required_quals,
                preferred_qualifications=preferred_quals,
                top_k=top_k,
                enable_reranking=enable_reranking
            )
            
            # Convert candidates to dictionary format
            candidates_data = [candidate.to_dict() for candidate in candidates]
            
            # Create response
            result = {
                "search_type": "qualifications_based",
                "total_candidates": len(candidates_data),
                "search_parameters": {
                    "top_k": top_k,
                    "enable_reranking": enable_reranking,
                    "required_qualifications": required_quals,
                    "preferred_qualifications": preferred_quals
                },
                "candidates": candidates_data
            }
            
            logger.info(f"Successfully found {len(candidates_data)} matching candidates")
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error_msg = f"Failed to find matching candidates: {str(e)}"
            logger.error(f"Error in find_matching_candidates: {error_msg}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return json.dumps({"error": error_msg})
    
    async def search_candidates_by_skills(self, skills: str, top_k: int = 10) -> str:
        """Search candidates by specific skills or keywords.
        
        Args:
            skills: Comma-separated list of skills or keywords to search for
            top_k: Number of top candidates to retrieve (default: 10, max: 50)
        
        Returns:
            JSON string containing list of matching candidates
        """
        logger.info(f">>> Tool: 'search_candidates_by_skills' called with skills='{skills}', top_k={top_k}")
        
        # Validate service availability
        if not self.llamacloud_service:
            error_msg = "LlamaCloud service is not available. Check configuration and API key."
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
        
        # Validate input parameters
        if not skills or not skills.strip():
            return json.dumps({"error": "Skills parameter cannot be empty"})
        
        # Validate top_k parameter
        if not isinstance(top_k, int) or top_k < 1 or top_k > 50:
            return json.dumps({"error": "top_k must be an integer between 1 and 50"})
        
        try:
            # Create a simple job description focused on skills
            skills_list = [skill.strip() for skill in skills.split(",") if skill.strip()]
            
            job_description = JobDescriptionData(
                title="Skills-based Search",
                company="Search Query",
                location="Any",
                required_qualifications=skills_list,
                preferred_qualifications=[],
                description=f"Looking for candidates with skills: {skills}",
                experience_level="",
                employment_type=""
            )
            
            logger.info(f"Searching for candidates with skills: {skills_list}")
            
            # Retrieve candidates from LlamaCloud
            candidates = await self.llamacloud_service.retrieve_candidates(
                job_description=job_description,
                top_k=top_k,
                enable_reranking=True
            )
            
            # Convert candidates to dictionary format
            candidates_data = [candidate.to_dict() for candidate in candidates]
            
            # Create response
            result = {
                "search_skills": skills_list,
                "total_candidates": len(candidates_data),
                "search_parameters": {
                    "top_k": top_k
                },
                "candidates": candidates_data
            }
            
            logger.info(f"Successfully found {len(candidates_data)} candidates with matching skills")
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error_msg = f"Failed to search candidates by skills: {str(e)}"
            logger.error(f"Error in search_candidates_by_skills: {error_msg}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return json.dumps({"error": error_msg})
    
    async def score_candidate_qualifications(
        self,
        candidate_resume: str,
        required_qualifications: str,
        preferred_qualifications: str = "",
        job_title: str = "",
        job_description: str = ""
    ) -> str:
        """Score a candidate's resume against specific job qualifications using LLM evaluation.
        
        Args:
            candidate_resume: The candidate's resume text content
            required_qualifications: Comma-separated string of required qualifications
            preferred_qualifications: Comma-separated string of preferred qualifications (optional)
            job_title: Job title for context (optional)
            job_description: Job description for context (optional)
        
        Returns:
            JSON string containing detailed scoring results for each qualification
        """
        logger.info(f">>> Tool: 'score_candidate_qualifications' called")
        
        # Validate input parameters
        if not candidate_resume or not candidate_resume.strip():
            return json.dumps({"error": "Candidate resume cannot be empty"})
        
        if not required_qualifications or not required_qualifications.strip():
            return json.dumps({"error": "Required qualifications cannot be empty"})
        
        try:
            # Parse qualifications into lists
            required_quals = [qual.strip() for qual in required_qualifications.split(',') if qual.strip()]
            preferred_quals = [qual.strip() for qual in preferred_qualifications.split(',') if qual.strip()] if preferred_qualifications else []
            
            logger.info(f"Scoring candidate against {len(required_quals)} required and {len(preferred_quals)} preferred qualifications")
            
            # Import OpenAI service
            from services.openai_service import OpenAIService
            
            # Use OpenAI service for scoring
            openai_service = OpenAIService()
            scoring_result = await openai_service.score_candidate_qualifications(
                candidate_resume=candidate_resume,
                required_qualifications=required_quals,
                preferred_qualifications=preferred_quals,
                job_title=job_title,
                job_description=job_description
            )
            
            logger.info(f"Successfully scored candidate with total score {scoring_result.get('totalScore', 0)}/{scoring_result.get('maxPossibleScore', 0)}")
            return json.dumps(scoring_result, indent=2)
            
        except Exception as e:
            error_msg = f"Failed to score candidate qualifications: {str(e)}"
            logger.error(f"Error in score_candidate_qualifications: {error_msg}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return json.dumps({"error": error_msg})