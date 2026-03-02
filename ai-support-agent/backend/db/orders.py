"""
Orders database module for ShopNest AI Support Agent
Contains hardcoded order data and helper functions for order lookup
"""

ORDERS_DB = {
    "1001": {
        "order_id": "1001",
        "status": "Shipped",
        "eta": "2 days",
        "item": "Blue Wireless Headphones",
        "customer_name": "John Doe"
    },
    "1002": {
        "order_id": "1002",
        "status": "Processing",
        "eta": "5 days",
        "item": "Gaming Keyboard",
        "customer_name": "Jane Smith"
    },
    "1003": {
        "order_id": "1003",
        "status": "Delivered",
        "eta": "N/A",
        "item": "Running Shoes",
        "customer_name": "Ahmed Khan"
    },
    "1004": {
        "order_id": "1004",
        "status": "Out for Delivery",
        "eta": "Today",
        "item": "Smartphone Case",
        "customer_name": "Maria Garcia"
    },
    "1005": {
        "order_id": "1005",
        "status": "Cancelled",
        "eta": "N/A",
        "item": "Coffee Maker",
        "customer_name": "Robert Johnson"
    },
    "1006": {
        "order_id": "1006",
        "status": "Shipped",
        "eta": "3 days",
        "item": "USB-C Cable 3-Pack",
        "customer_name": "Lisa Chen"
    },
    "1007": {
        "order_id": "1007",
        "status": "Processing",
        "eta": "7 days",
        "item": "Yoga Mat and Blocks Set",
        "customer_name": "David Williams"
    },
    "1008": {
        "order_id": "1008",
        "status": "Delivered",
        "eta": "N/A",
        "item": "Stainless Steel Water Bottle",
        "customer_name": "Sarah Patel"
    }
}


def get_order(order_id: str) -> dict | None:
    """
    Look up an order by order_id

    Args:
        order_id: The order ID to search for (e.g., "1001")

    Returns:
        dict: Order details if found, None otherwise
    """
    return ORDERS_DB.get(order_id)


def list_orders() -> list:
    """
    Get all orders in the database

    Returns:
        list: List of all order dictionaries
    """
    return list(ORDERS_DB.values())
