"""Configuration settings for the MCP server."""

import os

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")  # Replace with your actual API key or set OPENAI_API_KEY env var
DEFAULT_MODEL = "gpt-4o-mini"

# LlamaCloud Configuration - Public Resumes Index 
LLAMA_CLOUD_API_KEY = os.getenv("LLAMA_CLOUD_API_KEY", "your-llamacloud-api-key-here")  # Replace with your actual API key or set LLAMA_CLOUD_API_KEY env var
LLAMA_CLOUD_PROJECT_NAME = os.getenv("LLAMA_CLOUD_PROJECT_NAME", "Default")  # Replace with your project name or set env var
LLAMA_CLOUD_ORGANIZATION_ID = os.getenv("LLAMA_CLOUD_ORGANIZATION_ID", "your-org-id-here")  # Replace with your organization ID or set env var
LLAMA_CLOUD_INDEX_NAME = os.getenv("LLAMA_CLOUD_INDEX_NAME", "resume_public")  # Replace with your index name or set env var

# Server Configuration
DEFAULT_PORT = int(os.getenv("PORT", "8080"))
DEFAULT_HOST = os.getenv("HOST", "0.0.0.0")

# API Configuration
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "30.0"))
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.1")) 