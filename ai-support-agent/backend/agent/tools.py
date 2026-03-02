"""
Tools module for ShopNest AI Support Agent
Contains LangChain tools for order lookup and other functions
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langchain.tools import tool
from db.orders import get_order


@tool
def get_order_status(order_id: str) -> str:
    """
    Look up the status of a customer's order by order ID.

    Use this tool when a customer asks about their order status, delivery time,
    tracking information, or any question related to a specific order number.
    The order_id should be a numeric string (e.g., "1001", "1002").

    Args:
        order_id: The order ID to look up (e.g., "1001")

    Returns:
        str: Formatted order details including item, status, ETA, and customer name,
             or an error message if the order is not found
    """
    # Look up the order in the database
    order = get_order(order_id)

    # If order not found, return error message
    if order is None:
        return f"No order found with ID {order_id}. Please check the order number."

    # Format and return order details
    formatted_response = (
        f"Order #{order['order_id']} | "
        f"Item: {order['item']} | "
        f"Status: {order['status']} | "
        f"ETA: {order['eta']} | "
        f"Customer: {order['customer_name']}"
    )

    return formatted_response


# List of all available tools for easy import
TOOLS = [get_order_status]
