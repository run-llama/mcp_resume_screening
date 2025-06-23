"""LlamaCloud service for candidate retrieval from resume index."""

import json
import logging
from typing import List, Dict, Any, Optional
import asyncio

from config import (
    LLAMA_CLOUD_API_KEY, 
    LLAMA_CLOUD_INDEX_NAME, 
    LLAMA_CLOUD_PROJECT_NAME,
    LLAMA_CLOUD_ORGANIZATION_ID
)
from models import JobDescriptionData

logger = logging.getLogger(__name__)

try:
    from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
    LLAMA_INDEX_AVAILABLE = True
except ImportError:
    logger.error("llama-index package is required for LlamaCloud functionality. Please install it with: pip install llama-index")
    LLAMA_INDEX_AVAILABLE = False


class CandidateMatch:
    """Data structure for candidate match results."""
    
    def __init__(
        self,
        node_id: str,
        score: float,
        content: str,
        metadata: Dict[str, Any],
        candidate_name: Optional[str] = None,
        file_name: Optional[str] = None
    ):
        self.node_id = node_id
        self.score = score
        self.content = content
        self.metadata = metadata
        self.candidate_name = candidate_name or "Unknown Candidate"
        self.file_name = file_name or ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "node_id": self.node_id,
            "score": self.score,
            "content": self.content,
            "metadata": self.metadata,
            "candidate_name": self.candidate_name,
            "file_name": self.file_name
        }


class LlamaCloudService:
    """Service class for interacting with LlamaCloud resume index using LlamaIndex."""
    
    def __init__(self):
        """Initialize the LlamaCloud service."""
        if not LLAMA_INDEX_AVAILABLE:
            raise ImportError("llama-index package is required for LlamaCloud functionality. Please install it with: pip install llama-index")
        
        if not LLAMA_CLOUD_API_KEY or LLAMA_CLOUD_API_KEY == "llx-your-api-key-here":
            raise ValueError("LLAMA_CLOUD_API_KEY is required and must be set to a valid API key")
        
        if not LLAMA_CLOUD_INDEX_NAME:
            raise ValueError("LLAMA_CLOUD_INDEX_NAME is required")
        
        self.api_key = LLAMA_CLOUD_API_KEY
        self.index_name = LLAMA_CLOUD_INDEX_NAME
        self.project_name = LLAMA_CLOUD_PROJECT_NAME
        self.organization_id = LLAMA_CLOUD_ORGANIZATION_ID
        
        # Initialize LlamaCloud index (will be created lazily)
        self._index = None
        
        logger.info(f"LlamaCloudService initialized with index: {self.index_name}")
    
    def _get_index(self):
        """Get or create the LlamaCloud index instance."""
        if self._index is None:
            try:
                # Set the API key in environment if not already set
                import os
                if not os.environ.get("LLAMA_CLOUD_API_KEY"):
                    os.environ["LLAMA_CLOUD_API_KEY"] = self.api_key
                
                logger.info(f"Connecting to LlamaCloud index: {self.index_name}")
                
                # Connect to existing index as per the documentation
                self._index = LlamaCloudIndex(
                    name=self.index_name,
                    project_name=self.project_name
                )
                
                logger.info("Successfully connected to LlamaCloud index")
                
            except Exception as e:
                logger.error(f"Failed to connect to LlamaCloud index: {e}")
                raise
        
        return self._index
    
    def _build_search_query(self, job_description: JobDescriptionData) -> str:
        """Build a search query from job description data."""
        query_parts = []
        
        if job_description.title:
            query_parts.append(f"Job Title: {job_description.title}")
        
        if job_description.required_qualifications:
            query_parts.append(f"Required Qualifications: {' '.join(job_description.required_qualifications)}")
        
        if job_description.preferred_qualifications:
            query_parts.append(f"Preferred Qualifications: {' '.join(job_description.preferred_qualifications)}")
        
        if job_description.experience_level:
            query_parts.append(f"Experience Level: {job_description.experience_level}")
        
        query = " ".join(query_parts)
        logger.info(f"Built search query: {query}")
        return query
    
    def _build_qualifications_query(self, required_qualifications: List[str], preferred_qualifications: List[str]) -> str:
        """Build a search query from qualification lists."""
        query_parts = []
        
        if required_qualifications:
            query_parts.append(f"Required skills and qualifications: {', '.join(required_qualifications)}")
        
        if preferred_qualifications:
            query_parts.append(f"Preferred skills and experience: {', '.join(preferred_qualifications)}")
        
        # Combine all qualifications for a comprehensive search
        all_qualifications = required_qualifications + preferred_qualifications
        if all_qualifications:
            query_parts.append(f"Relevant experience with: {', '.join(all_qualifications)}")
        
        query = " ".join(query_parts)
        logger.info(f"Built qualifications query: {query}")
        return query
    
    def _extract_candidate_info(self, node) -> CandidateMatch:
        """Extract candidate information from a retrieved node."""
        try:
            # Extract basic information from the node
            node_id = getattr(node, 'id_', '') or getattr(node, 'node_id', '')
            score = getattr(node, 'score', 0.0)
            
            # Extract content from different possible locations
            content = ""
            metadata = {}
            
            # Handle different node structures
            if hasattr(node, 'node'):
                # Node with nested structure
                inner_node = node.node
                node_id = node_id or getattr(inner_node, 'id_', '')
                content = getattr(inner_node, 'text', '') or getattr(inner_node, 'content', '')
                metadata = getattr(inner_node, 'metadata', {}) or getattr(inner_node, 'extra_info', {})
            else:
                # Direct node structure
                content = getattr(node, 'text', '') or getattr(node, 'content', '')
                metadata = getattr(node, 'metadata', {}) or getattr(node, 'extra_info', {})
            
            # Extract candidate name and file name from metadata
            candidate_name = "Unknown Candidate"
            file_name = metadata.get('file_name', '') or metadata.get('filename', '') or metadata.get('file_path', '')
            
            # Try to extract candidate name from file name
            if file_name:
                # Remove file extension and replace underscores with spaces
                import os
                base_name = os.path.basename(file_name)
                name_part = base_name.split('.')[0].replace('_', ' ').replace('-', ' ')
                if name_part and not name_part.lower().startswith('resume'):
                    candidate_name = name_part.title()
            
            # Try to extract name from content if not found in metadata
            if candidate_name == "Unknown Candidate" and content:
                # Simple pattern matching for names in resume content
                import re
                name_patterns = [
                    r'^([A-Z][a-z]+ [A-Z][a-z]+)',  # First line with Name format
                    r'Name:?\s*([A-Z][a-z]+ [A-Z][a-z]+)',  # Name: John Doe
                    r'([A-Z][a-z]+ [A-Z][a-z]+)\s*\n',  # Name followed by newline
                ]
                
                for pattern in name_patterns:
                    match = re.search(pattern, content[:200])  # Search in first 200 chars
                    if match:
                        candidate_name = match.group(1)
                        break
            
            return CandidateMatch(
                node_id=node_id,
                score=score,
                content=content,
                metadata=metadata,
                candidate_name=candidate_name,
                file_name=file_name
            )
            
        except Exception as e:
            logger.error(f"Error extracting candidate info from node: {e}")
            # Return a basic match with available information
            return CandidateMatch(
                node_id=str(getattr(node, 'id_', 'unknown')),
                score=getattr(node, 'score', 0.0),
                content=str(getattr(node, 'text', getattr(node, 'content', ''))),
                metadata=getattr(node, 'metadata', {})
            )
    
    async def retrieve_candidates(
        self,
        job_description: JobDescriptionData,
        top_k: int = 20,
        enable_reranking: bool = True
    ) -> List[CandidateMatch]:
        """Retrieve top candidates matching the job description."""
        try:
            logger.info(f"Starting candidate retrieval for job: {job_description.title}")
            
            # Build search query from job description
            query = self._build_search_query(job_description)
            
            # Get the index and configure retriever
            index = self._get_index()
            
            # Configure retriever as per the documentation
            # alpha=1.0 restricts it to vector search
            retriever_config = {
                "dense_similarity_top_k": top_k,
                "alpha": 1.0,  # Restricts to vector search
                "enable_reranking": enable_reranking,
            }
            
            logger.info(f"Configuring retriever with: {retriever_config}")
            retriever = index.as_retriever(**retriever_config)
            
            # Perform retrieval
            logger.info(f"Retrieving candidates with query: {query}")
            
            # Run the retrieval in a thread pool to avoid blocking the async loop
            import asyncio
            loop = asyncio.get_event_loop()
            nodes = await loop.run_in_executor(
                None,
                lambda: retriever.retrieve(query)
            )
            
            logger.info(f"Retrieved {len(nodes)} nodes from LlamaCloud")
            
            # Convert nodes to CandidateMatch objects
            candidates = []
            seen_files = set()  # Track files to avoid duplicates
            
            for i, node in enumerate(nodes):
                try:
                    candidate = self._extract_candidate_info(node)
                    
                    # Deduplicate by file name if available
                    if candidate.file_name:
                        if candidate.file_name in seen_files:
                            logger.info(f"Skipping duplicate file: {candidate.file_name}")
                            continue
                        seen_files.add(candidate.file_name)
                    
                    candidates.append(candidate)
                    logger.info(f"Processed candidate {i+1}: {candidate.candidate_name} (score: {candidate.score:.3f})")
                    
                except Exception as e:
                    logger.error(f"Error processing node {i}: {e}")
                    continue
            
            # Sort by score (descending)
            candidates.sort(key=lambda x: x.score, reverse=True)
            
            logger.info(f"Successfully retrieved {len(candidates)} unique candidates")
            return candidates
            
        except Exception as e:
            logger.error(f"Error retrieving candidates: {e}")
            raise
    
    async def retrieve_candidates_by_qualifications(
        self,
        required_qualifications: List[str],
        preferred_qualifications: List[str],
        top_k: int = 20,
        enable_reranking: bool = True
    ) -> List[CandidateMatch]:
        """Retrieve candidates matching specific qualifications."""
        try:
            logger.info(f"Starting candidate retrieval by qualifications")
            logger.info(f"Required: {required_qualifications}")
            logger.info(f"Preferred: {preferred_qualifications}")
            
            # Build search query from qualifications
            query = self._build_qualifications_query(required_qualifications, preferred_qualifications)
            
            # Get the index and configure retriever
            index = self._get_index()
            
            # Configure retriever as per the documentation
            retriever_config = {
                "dense_similarity_top_k": top_k,
                "alpha": 1.0,  # Restricts to vector search
                "enable_reranking": enable_reranking,
            }
            
            logger.info(f"Configuring retriever with: {retriever_config}")
            retriever = index.as_retriever(**retriever_config)
            
            # Perform retrieval
            logger.info(f"Retrieving candidates with qualifications query: {query}")
            
            # Run the retrieval in a thread pool to avoid blocking the async loop
            import asyncio
            loop = asyncio.get_event_loop()
            nodes = await loop.run_in_executor(
                None,
                lambda: retriever.retrieve(query)
            )
            
            logger.info(f"Retrieved {len(nodes)} nodes from LlamaCloud")
            
            # Convert nodes to CandidateMatch objects
            candidates = []
            seen_files = set()  # Track files to avoid duplicates
            
            for i, node in enumerate(nodes):
                try:
                    candidate = self._extract_candidate_info(node)
                    
                    # Deduplicate by file name if available
                    if candidate.file_name:
                        if candidate.file_name in seen_files:
                            logger.info(f"Skipping duplicate file: {candidate.file_name}")
                            continue
                        seen_files.add(candidate.file_name)
                    
                    candidates.append(candidate)
                    logger.info(f"Processed candidate {i+1}: {candidate.candidate_name} (score: {candidate.score:.3f})")
                    
                except Exception as e:
                    logger.error(f"Error processing node {i}: {e}")
                    continue
            
            # Sort by score (descending)
            candidates.sort(key=lambda x: x.score, reverse=True)
            
            logger.info(f"Successfully retrieved {len(candidates)} unique candidates by qualifications")
            return candidates
            
        except Exception as e:
            logger.error(f"Error retrieving candidates by qualifications: {e}")
            raise
    
    async def search_by_skills(
        self,
        skills: str,
        top_k: int = 20
    ) -> List[CandidateMatch]:
        """Search candidates by specific skills."""
        try:
            logger.info(f"Starting skill-based search for: {skills}")
            
            # Get the index and configure retriever
            index = self._get_index()
            
            # Configure retriever for skill search (no reranking for simplicity)
            retriever_config = {
                "dense_similarity_top_k": top_k,
                "alpha": 1.0,  # Restricts to vector search
                "enable_reranking": False,  # Disable reranking for skill search
            }
            
            logger.info(f"Configuring retriever for skill search with: {retriever_config}")
            retriever = index.as_retriever(**retriever_config)
            
            # Build query from skills
            query = f"Skills and experience in: {skills}"
            
            # Perform retrieval
            logger.info(f"Searching candidates with skills query: {query}")
            
            # Run the retrieval in a thread pool to avoid blocking the async loop
            import asyncio
            loop = asyncio.get_event_loop()
            nodes = await loop.run_in_executor(
                None,
                lambda: retriever.retrieve(query)
            )
            
            logger.info(f"Retrieved {len(nodes)} nodes from LlamaCloud for skills search")
            
            # Convert nodes to CandidateMatch objects
            candidates = []
            seen_files = set()  # Track files to avoid duplicates
            
            for i, node in enumerate(nodes):
                try:
                    candidate = self._extract_candidate_info(node)
                    
                    # Deduplicate by file name if available
                    if candidate.file_name:
                        if candidate.file_name in seen_files:
                            logger.info(f"Skipping duplicate file: {candidate.file_name}")
                            continue
                        seen_files.add(candidate.file_name)
                    
                    candidates.append(candidate)
                    logger.info(f"Processed candidate {i+1}: {candidate.candidate_name} (score: {candidate.score:.3f})")
                    
                except Exception as e:
                    logger.error(f"Error processing node {i}: {e}")
                    continue
            
            # Sort by score (descending)
            candidates.sort(key=lambda x: x.score, reverse=True)
            
            logger.info(f"Successfully retrieved {len(candidates)} unique candidates for skills: {skills}")
            return candidates
            
        except Exception as e:
            logger.error(f"Error searching candidates by skills: {e}")
            raise 