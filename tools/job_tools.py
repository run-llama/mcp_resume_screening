"""Job description related MCP tools."""

import json
import logging
import traceback
from typing import Dict, Any

from services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class JobTools:
    """Container class for job description related MCP tools."""
    
    def __init__(self):
        """Initialize JobTools with OpenAI service."""
        self.openai_service = OpenAIService()
    
    async def extract_job_requirements(self, jd_text: str) -> str:
        """Extract structured job requirements from job description text.
        
        Args:
            jd_text: The job description text to analyze
        
        Returns:
            JSON string containing structured job requirements including title, company, 
            location, required_qualifications, preferred_qualifications, description, 
            experience_level, and employment_type.
        """
        logger.info(f">>> Tool: 'extract_job_requirements' called with JD text length: {len(jd_text)}")
        
        # Input validation
        if not jd_text or not jd_text.strip():
            return json.dumps({"error": "Job description text cannot be empty"})
        
        if len(jd_text.strip()) < 10:
            return json.dumps({"error": "Job description text is too short to be meaningful"})
        
        try:
            logger.info("Starting job description extraction process...")
            
            # Use the OpenAI service for extraction
            extraction_result = await self.openai_service.extract_job_description_from_text(jd_text)
            
            # Check that the extraction result is valid
            if not extraction_result:
                logger.error("JD extraction result is undefined")
                return json.dumps({"error": "Failed to extract data from job description text"})
            
            logger.info("JD extraction completed successfully")
            result_dict = extraction_result.to_dict()
            logger.info(f"Structured JD extraction result: {json.dumps(result_dict, indent=2)}")
            
            return json.dumps(result_dict)
                
        except ValueError as e:
            logger.error(f"ValueError in extract_job_requirements: {e}")
            return json.dumps({"error": f"Configuration error: {str(e)}"})
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in extract_job_requirements: {e}")
            return json.dumps({"error": f"JSON parsing error: {str(e)}"})
        except Exception as e:
            logger.error(f"Unexpected error extracting job requirements: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error args: {e.args}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return json.dumps({"error": f"Failed to extract job requirements: {str(e)}"}) 