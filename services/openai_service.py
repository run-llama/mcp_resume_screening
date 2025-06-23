"""OpenAI API service for job description extraction."""

import json
import logging
import httpx
from typing import Dict, List, Any

from config import OPENAI_API_KEY, DEFAULT_MODEL, REQUEST_TIMEOUT, OPENAI_TEMPERATURE
from models import JobDescriptionData

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service class for handling OpenAI API interactions."""
    
    def __init__(self):
        """Initialize the OpenAI service."""
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        self.api_key = OPENAI_API_KEY
        self.model = DEFAULT_MODEL
        self.timeout = REQUEST_TIMEOUT
        self.temperature = OPENAI_TEMPERATURE
    
    async def extract_job_description_from_text(self, text: str) -> JobDescriptionData:
        """Extract job description data from text using OpenAI.
        
        Args:
            text: The job description text to analyze
            
        Returns:
            JobDescriptionData object with extracted information
            
        Raises:
            Exception: If the API call fails or response parsing fails
        """
        logger.info(f"Starting extraction with text length: {len(text)}")
        logger.info("API key is available, proceeding with extraction")
        
        # Create the extraction prompt based on reference implementation
        prompt = self._create_extraction_prompt(text)
        
        try:
            logger.info("Creating HTTP client and making API request")
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                request_data = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that extracts structured data from job descriptions."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": self.temperature,
                    "response_format": {"type": "json_object"}
                }
                
                logger.info(f"Making request to OpenAI with model: {self.model}")
                
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    json=request_data
                )
                
                logger.info(f"OpenAI API response status: {response.status_code}")
                
                if response.status_code != 200:
                    error_text = response.text
                    logger.error(f"OpenAI API error response: {error_text}")
                    try:
                        error_data = response.json()
                        logger.error(f"OpenAI API error JSON: {error_data}")
                        raise Exception(f"OpenAI API error ({response.status_code}): {error_data}")
                    except json.JSONDecodeError:
                        raise Exception(f"OpenAI API error ({response.status_code}): {error_text}")
                
                data = response.json()
                logger.info("Successfully parsed OpenAI response JSON")
                
                content = data["choices"][0]["message"]["content"]
                logger.info(f"Extracted content from OpenAI response, length: {len(content) if content else 0}")
                
                if not content:
                    logger.error("OpenAI returned empty content")
                    raise Exception("Failed to extract job description data: Empty response")
                
                logger.info(f"OpenAI response content sample: {content[:200]}...")
                
                return self._parse_response_to_job_data(content)
                    
        except httpx.TimeoutException as e:
            logger.error(f"HTTP timeout error: {e}")
            raise Exception(f"Request timeout: {str(e)}")
        except httpx.RequestError as e:
            logger.error(f"HTTP request error: {e}")
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in extract_job_description_from_text: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            raise
    
    def _create_extraction_prompt(self, text: str) -> str:
        """Create the prompt for job description extraction.
        
        Args:
            text: The job description text
            
        Returns:
            Formatted prompt string
        """
        return f"""
Extract the following information from this job description text. 
Format the response as a valid JSON object with these fields:
- title: The job title
- company: The company name (use "Unknown" if not found)
- location: The job location (use "Not specified" if not found)
- required_qualifications: An array of strings, each one representing a required qualification
- preferred_qualifications: An array of strings, each one representing a preferred/nice-to-have qualification
- description: A summary of the job description
- experience_level: The experience level (entry-level, mid-level, senior, etc.)
- employment_type: The employment type (full-time, part-time, contract, etc.)

Job Description Text:
{text}
"""
    
    def _parse_response_to_job_data(self, content: str) -> JobDescriptionData:
        """Parse OpenAI response content to JobDescriptionData object.
        
        Args:
            content: The JSON content from OpenAI response
            
        Returns:
            JobDescriptionData object
            
        Raises:
            Exception: If JSON parsing fails
        """
        try:
            parsed_data = json.loads(content)
            logger.info("Successfully parsed JSON from OpenAI response")
            logger.info(f"Parsed data keys: {list(parsed_data.keys())}")
            
            # Validate and create JobDescriptionData object
            result = JobDescriptionData(
                title=parsed_data.get("title", "Unknown Position"),
                company=parsed_data.get("company", "Unknown"),
                location=parsed_data.get("location", "Not specified"),
                required_qualifications=parsed_data.get("required_qualifications", []),
                preferred_qualifications=parsed_data.get("preferred_qualifications", []),
                description=parsed_data.get("description", ""),
                experience_level=parsed_data.get("experience_level", "Not specified"),
                employment_type=parsed_data.get("employment_type", "Not specified")
            )
            logger.info("Successfully created JobDescriptionData object")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw content: {content}")
            raise Exception(f"Failed to parse response from OpenAI: {str(e)}")
    
    async def score_candidate_qualifications(
        self,
        candidate_resume: str,
        required_qualifications: List[str],
        preferred_qualifications: List[str],
        job_title: str = "",
        job_description: str = ""
    ) -> Dict[str, Any]:
        """Score a candidate's resume against job qualifications using OpenAI.
        
        Args:
            candidate_resume: The candidate's resume text content
            required_qualifications: List of required qualifications
            preferred_qualifications: List of preferred qualifications
            job_title: Job title for context (optional)
            job_description: Job description for context (optional)
        
        Returns:
            Dictionary containing detailed scoring results
        """
        try:
            logger.info("Starting candidate qualification scoring with OpenAI")
            
            # Build the prompt for scoring
            prompt_parts = [
                "You are a professional recruiter tasked with evaluating how well a candidate's resume matches the qualifications for a job.",
                ""
            ]
            
            if job_title:
                prompt_parts.append(f"JOB TITLE: {job_title}")
            
            if job_description:
                prompt_parts.append(f"JOB DESCRIPTION: {job_description}")
            
            prompt_parts.extend([
                "",
                "CANDIDATE'S RESUME:",
                candidate_resume,
                "",
                "Please evaluate the candidate against each qualification using the following scale:",
                "0 - Not Met: The candidate's resume shows no evidence of meeting this qualification",
                "1 - Somewhat Met: The candidate's resume shows some evidence of meeting this qualification but may lack depth or completeness",
                "2 - Strongly Met: The candidate's resume clearly demonstrates they meet or exceed this qualification",
                "",
                "Please evaluate ONLY the following qualifications, and return your response in JSON format with explanations for each score:",
                ""
            ])
            
            if required_qualifications:
                prompt_parts.append("REQUIRED QUALIFICATIONS:")
                for i, qual in enumerate(required_qualifications, 1):
                    prompt_parts.append(f"{i}. {qual}")
                prompt_parts.append("")
            
            if preferred_qualifications:
                prompt_parts.append("PREFERRED QUALIFICATIONS:")
                for i, qual in enumerate(preferred_qualifications, 1):
                    prompt_parts.append(f"{i}. {qual}")
                prompt_parts.append("")
            
            prompt_parts.extend([
                'Format your response as valid JSON with this structure:',
                '{',
                '  "requiredScores": [',
                '    {',
                '      "qualification": "qualification text",',
                '      "score": 0/1/2,',
                '      "explanation": "brief explanation for the score"',
                '    },',
                '    ...',
                '  ],',
                '  "preferredScores": [',
                '    {',
                '      "qualification": "qualification text",',
                '      "score": 0/1/2,',
                '      "explanation": "brief explanation for the score"',
                '    },',
                '    ...',
                '  ],',
                '  "overallFeedback": "brief overall assessment of the candidate"',
                '}'
            ])
            
            prompt = "\n".join(prompt_parts)
            
            logger.info("Sending scoring request to OpenAI")
            
            # Call OpenAI API
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                request_data = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a professional recruiter who evaluates how well candidate resumes match job qualifications."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.1,
                    "response_format": {"type": "json_object"}
                }
                
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    json=request_data
                )
                
                if response.status_code != 200:
                    error_text = response.text
                    logger.error(f"OpenAI API error response: {error_text}")
                    try:
                        error_data = response.json()
                        raise Exception(f"OpenAI API error ({response.status_code}): {error_data}")
                    except json.JSONDecodeError:
                        raise Exception(f"OpenAI API error ({response.status_code}): {error_text}")
                
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                if not content:
                    raise ValueError("No content in OpenAI response")
                
                logger.info("Received response from OpenAI, parsing JSON")
                
                try:
                    # Parse the JSON response
                    scoring_data = json.loads(content)
                    
                    # Calculate the total score
                    required_scores = scoring_data.get("requiredScores", [])
                    preferred_scores = scoring_data.get("preferredScores", [])
                    
                    required_total = sum(item.get("score", 0) for item in required_scores)
                    preferred_total = sum(item.get("score", 0) for item in preferred_scores)
                    
                    total_score = required_total + preferred_total
                    max_possible_score = (len(required_qualifications) + len(preferred_qualifications)) * 2
                    
                    # Calculate match percentage
                    match_percentage = (total_score / max_possible_score * 100) if max_possible_score > 0 else 0
                    
                    result = {
                        "requiredScores": required_scores,
                        "preferredScores": preferred_scores,
                        "totalScore": total_score,
                        "maxPossibleScore": max_possible_score,
                        "matchPercentage": round(match_percentage, 1),
                        "overallFeedback": scoring_data.get("overallFeedback", ""),
                        "scoringBreakdown": {
                            "requiredTotal": required_total,
                            "preferredTotal": preferred_total,
                            "requiredCount": len(required_qualifications),
                            "preferredCount": len(preferred_qualifications)
                        }
                    }
                    
                    logger.info(f"Successfully scored candidate: {total_score}/{max_possible_score} ({match_percentage:.1f}%)")
                    return result
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response: {e}")
                    logger.error(f"Raw content: {content}")
                    raise ValueError("Failed to parse scoring data from LLM response")
                    
        except Exception as e:
            logger.error(f"Error scoring candidate qualifications: {e}")
            raise