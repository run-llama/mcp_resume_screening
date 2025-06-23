"""Data models for the MCP server."""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class JobDescriptionData:
    """Data structure for job description information matching reference implementation."""
    
    def __init__(
        self, 
        title: str, 
        company: str, 
        location: str, 
        required_qualifications: List[str], 
        preferred_qualifications: List[str],
        description: str, 
        experience_level: str, 
        employment_type: str
    ):
        """Initialize JobDescriptionData object.
        
        Args:
            title: The job title
            company: The company name
            location: The job location
            required_qualifications: List of required qualifications
            preferred_qualifications: List of preferred qualifications
            description: Job description summary
            experience_level: Experience level (entry, mid, senior, etc.)
            employment_type: Employment type (full-time, part-time, etc.)
        """
        logger.info(f"Creating JobDescriptionData with title: {title}")
        self.title = title
        self.company = company
        self.location = location
        self.required_qualifications = required_qualifications
        self.preferred_qualifications = preferred_qualifications
        self.description = description
        self.experience_level = experience_level
        self.employment_type = employment_type
        logger.info("JobDescriptionData object created successfully")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the object to a dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the job description data
        """
        logger.info("Converting JobDescriptionData to dict")
        result = {
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "required_qualifications": self.required_qualifications,
            "preferred_qualifications": self.preferred_qualifications,
            "description": self.description,
            "experience_level": self.experience_level,
            "employment_type": self.employment_type
        }
        logger.info("Successfully converted to dict")
        return result
    
    def __repr__(self) -> str:
        """String representation of the object."""
        return f"JobDescriptionData(title='{self.title}', company='{self.company}')" 