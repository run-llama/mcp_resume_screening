"""Mathematical operation MCP tools."""

import logging
from typing import Union

logger = logging.getLogger(__name__)


class MathTools:
    """Container class for mathematical operation MCP tools."""
    
    @staticmethod
    def add(a: int, b: int) -> int:
        """Add two numbers together.
        
        Args:
            a: The first number
            b: The second number
        
        Returns:
            The sum of the two numbers
        """
        logger.info(f">>> Tool: 'add' called with numbers '{a}' and '{b}'")
        return a + b
    
    @staticmethod
    def subtract(a: int, b: int) -> int:
        """Subtract two numbers.
        
        Args:
            a: The first number
            b: The second number
        
        Returns:
            The difference of the two numbers
        """
        logger.info(f">>> Tool: 'subtract' called with numbers '{a}' and '{b}'")
        return a - b
    
    @staticmethod
    def multiply(a: int, b: int) -> int:
        """Multiply two numbers.
        
        Args:
            a: The first number
            b: The second number
        
        Returns:
            The product of the two numbers
        """
        logger.info(f">>> Tool: 'multiply' called with numbers '{a}' and '{b}'")
        return a * b 