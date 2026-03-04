"""
Helper utilities for ShopNest AI Support Agent
Common functions used across different modules
"""

import re
from typing import Optional


def extract_order_id(text: str) -> Optional[str]:
    """
    Extract a 4-digit order ID from text

    Args:
        text: Text to search for order ID

    Returns:
        str: Order ID if found, None otherwise
    """
    match = re.search(r'\b(\d{4})\b', text)
    return match.group(1) if match else None


def is_order_tracking_query(text: str) -> bool:
    """
    Check if the text is asking about order tracking/status

    Args:
        text: Text to check

    Returns:
        bool: True if text contains order tracking keywords
    """
    keywords = ["order", "track", "status", "where"]
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in keywords)


def format_error_message(error: Exception, context: str = "") -> str:
    """
    Format a consistent error message for the user

    Args:
        error: The exception that occurred
        context: Optional context about where the error occurred

    Returns:
        str: User-friendly error message
    """
    base_msg = "I apologize, but I'm having trouble processing your request. Please try again."
    if context:
        return f"{base_msg} ({context})"
    return base_msg
