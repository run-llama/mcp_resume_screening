# MCP Server - Clean Modular Structure

This document explains the refactored, modular structure of the MCP server that follows Python best practices.

## 📁 Project Structure

```
mcp-on-cloudrun/
├── config.py              # Configuration constants and settings
├── models.py               # Data models and structures
├── services/               # Business logic services
│   ├── __init__.py
│   ├── openai_service.py  # OpenAI API interactions
│   └── llamacloud_service.py # LlamaCloud resume index interactions
├── tools/                  # MCP tool definitions
│   ├── __init__.py
│   ├── job_tools.py       # Job description related tools
│   ├── math_tools.py      # Mathematical operation tools
│   └── candidate_tools.py # Candidate retrieval tools
├── server_clean.py         # Clean main server entry point
├── test_server_clean.py    # Test script for clean server
├── server.py              # Original monolithic server (backup)
└── test_server.py         # Original test script (backup)
```

## 🏗️ Architecture Overview

### Separation of Concerns

The refactored structure follows the **Single Responsibility Principle** by separating different concerns into dedicated modules:

1. **Configuration** (`config.py`): All constants, API keys, and configuration settings
2. **Models** (`models.py`): Data structures and models like `JobDescriptionData`
3. **Services** (`services/`): Business logic and external API interactions
4. **Tools** (`tools/`): MCP tool definitions organized by functionality
5. **Server** (`server_clean.py`): FastMCP setup and tool registration only

### Benefits of This Structure

✅ **Maintainability**: Each module has a clear purpose and can be modified independently
✅ **Testability**: Individual components can be unit tested in isolation
✅ **Reusability**: Services and models can be reused across different tools
✅ **Scalability**: Easy to add new tools, services, or models
✅ **Readability**: Clean, focused code that's easy to understand
✅ **Best Practices**: Follows Python packaging and project structure conventions

## 📋 Module Details

### `config.py`
- Contains all configuration constants
- Environment variables and API keys
- Server settings (host, port, timeouts)
- Easy to modify without touching business logic

### `models.py`
- Defines data structures like `JobDescriptionData`
- Includes validation and serialization methods
- Type hints for better IDE support and documentation

### `services/openai_service.py`
- Encapsulates all OpenAI API interactions
- Handles HTTP requests, error handling, and response parsing
- Can be easily mocked for testing
- Configurable through the config module

### `tools/job_tools.py`
- Contains job description related MCP tools
- Uses the OpenAI service for processing
- Handles input validation and error responses
- Clean separation between tool interface and business logic

### `tools/math_tools.py`
- Simple mathematical operation tools
- Demonstrates how to organize related tools
- Static methods for stateless operations

### `server_clean.py`
- Minimal server setup code
- Imports and registers tools from their respective modules
- Clean main function with proper error handling
- Easy to understand and modify

## 🚀 Running the Clean Server

```bash
# Start the clean server
uv run server_clean.py

# Test the clean server (in another terminal)
uv run test_server_clean.py
```

## 🔧 Adding New Tools

To add a new tool:

1. **Create the tool class** in the appropriate `tools/` module
2. **Add any required services** in the `services/` directory
3. **Register the tool** in `server_clean.py` with the `@mcp.tool()` decorator
4. **Add tests** to verify functionality

Example:
```python
# In tools/new_tools.py
class NewTools:
    def my_new_tool(self, param: str) -> str:
        return f"Processed: {param}"

# In server_clean.py
from tools.new_tools import NewTools
new_tools = NewTools()

@mcp.tool()
def my_new_tool(param: str) -> str:
    return new_tools.my_new_tool(param)
```

## 📊 Comparison: Before vs After

| Aspect | Before (server.py) | After (Clean Structure) |
|--------|-------------------|-------------------------|
| Lines of code | 275 lines | ~100 lines in main server |
| Concerns mixed | ✗ All in one file | ✅ Separated by purpose |
| Testability | ✗ Hard to test parts | ✅ Easy to unit test |
| Maintainability | ✗ Changes affect everything | ✅ Isolated changes |
| Readability | ✗ Long, complex file | ✅ Short, focused files |
| Scalability | ✗ Gets worse over time | ✅ Easy to extend |

## 🛠️ Available MCP Tools

### Mathematical Operations
- `add(a: int, b: int)` - Add two numbers
- `subtract(a: int, b: int)` - Subtract two numbers  
- `multiply(a: int, b: int)` - Multiply two numbers

### Job Description Processing
- `extract_job_requirements(jd_text: str)` - Extract structured data from job description text

### Candidate Retrieval (LlamaCloud)
- `find_matching_candidates(required_qualifications: str, preferred_qualifications: str, top_k: int, enable_reranking: bool)` - Find candidates matching job qualifications from LlamaCloud resume index
- `search_candidates_by_skills(skills: str, top_k: int)` - Search candidates by specific skills or keywords
- `score_candidate_qualifications(candidate_resume: str, required_qualifications: str, preferred_qualifications: str, job_title: str, job_description: str)` - Score a candidate's resume against specific job qualifications using LLM evaluation

## 🎯 Next Steps

1. **Configure LlamaCloud**: Set your API key and index details in `config.py`
2. **Add more tools**: Follow the established patterns
3. **Add unit tests**: Test individual components
4. **Add type checking**: Use `mypy` for static type checking
5. **Add documentation**: Use docstrings and type hints throughout 