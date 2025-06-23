import asyncio

from fastmcp import Client

async def test_server():
    # Test the MCP server using streamable-http transport.
    # Use "/sse" endpoint if using sse transport.
    async with Client("http://localhost:8080/mcp") as client:
        # List available tools
        tools = await client.list_tools()
        for tool in tools:
            print(f">>> Tool found: {tool.name}")
        
        # Call add tool
        print(">>>  Calling add tool for 1 + 2")
        result = await client.call_tool("add", {"a": 1, "b": 2})
        print(f"<<<  Result: {result[0].text}")
        # Call subtract tool
        print(">>>  Calling subtract tool for 10 - 3")
        result = await client.call_tool("subtract", {"a": 10, "b": 3})
        print(f"<<< Result: {result[0].text}")
        # Call multiply tool
        print(">>>  Calling multiply tool for 4 * 5")
        result = await client.call_tool("multiply", {"a": 4, "b": 5})
        print(f"<<< Result: {result[0].text}")
        
        # Call extract_job_requirements tool
        sample_jd = """
        Software Engineer - Full Stack
        TechCorp Inc.
        San Francisco, CA
        
        We are seeking a talented Full Stack Software Engineer to join our growing team. 
        
        Need to have:
        - Bachelor's degree in Computer Science or related field
        - 3+ years of experience in web development
        - Proficiency in JavaScript, Python, SQL
        - Experience with React and Node.js
        
        Plus if you have:
        - Experience with cloud platforms (AWS, GCP)
        - Knowledge of Docker and Kubernetes
        - Previous startup experience
        
        This is a full-time position offering competitive salary and benefits.
        """
        print(">>>  Calling extract_job_requirements tool")
        jd_result = await client.call_tool("extract_job_requirements", {"jd_text": sample_jd})
        print(f"<<< Result: {jd_result[0].text}")
        
        # Call find_matching_candidates tool with qualifications
        print(">>>  Calling find_matching_candidates tool")
        result = await client.call_tool("find_matching_candidates", {
            "required_qualifications": "Python, JavaScript, React, Node.js, 3+ years experience",
            "preferred_qualifications": "AWS, Docker, Kubernetes, CI/CD",
            "top_k": 5,
            "enable_reranking": True
        })
        print(f"<<< Result: {result[0].text}")
        
        # Call search_candidates_by_skills tool
        print(">>>  Calling search_candidates_by_skills tool")
        result = await client.call_tool("search_candidates_by_skills", {
            "skills": "Python, JavaScript, React, Node.js",
            "top_k": 3
        })
        print(f"<<< Result: {result[0].text}")
        
        # Test score_candidate_qualifications tool
        print(">>>  Calling score_candidate_qualifications tool")
        sample_resume = """
        John Doe
        Software Engineer
        
        Experience:
        - 5 years of Python development
        - 3 years of JavaScript and React
        - 2 years working with AWS and Docker
        - Experience with machine learning projects
        - Bachelor's degree in Computer Science
        
        Skills: Python, JavaScript, React, Node.js, AWS, Docker, Machine Learning, SQL
        """
        
        result = await client.call_tool("score_candidate_qualifications", {
            "candidate_resume": sample_resume,
            "required_qualifications": "Python, JavaScript, React, 3+ years experience",
            "preferred_qualifications": "AWS, Docker, Machine Learning",
            "job_title": "Senior Software Engineer",
            "job_description": "We are looking for a senior software engineer to join our team"
        })
        print(f"<<< Result: {result[0].text}")
        
        print(">>> All tests completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_server()) 