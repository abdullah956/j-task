"""
Memory module for ShopNest AI Support Agent
Manages per-session chat history in memory using a simple dict
"""

from typing import List
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

# In-memory storage for chat histories
# Format: {session_id: [HumanMessage, AIMessage, ...]}
_chat_histories: dict[str, List[BaseMessage]] = {}


def get_history(session_id: str) -> List[BaseMessage]:
    """
    Get the message history for a given session

    Args:
        session_id: Unique identifier for the chat session

    Returns:
        list: List of LangChain message objects (HumanMessage, AIMessage)
              Returns empty list if session doesn't exist
    """
    return _chat_histories.get(session_id, [])


def add_message(session_id: str, role: str, content: str) -> None:
    """
    Add a message to the session history

    Args:
        session_id: Unique identifier for the chat session
        role: Either "human" or "ai" to indicate message type
        content: The message content/text

    Raises:
        ValueError: If role is not "human" or "ai"
    """
    # Create session if it doesn't exist
    if session_id not in _chat_histories:
        _chat_histories[session_id] = []

    # Create appropriate message type based on role
    if role.lower() == "human":
        message = HumanMessage(content=content)
    elif role.lower() == "ai":
        message = AIMessage(content=content)
    else:
        raise ValueError(f"Invalid role: {role}. Must be 'human' or 'ai'")

    # Append message to session history
    _chat_histories[session_id].append(message)


def clear_history(session_id: str) -> None:
    """
    Clear the message history for a given session

    Args:
        session_id: Unique identifier for the chat session
    """
    if session_id in _chat_histories:
        _chat_histories[session_id] = []


def get_history_as_string(session_id: str, max_messages: int = 10) -> str:
    """
    Get the last N messages as a formatted string for prompt injection

    Args:
        session_id: Unique identifier for the chat session
        max_messages: Maximum number of recent messages to include (default: 10)

    Returns:
        str: Formatted conversation history string
             Format: "Human: <message>\nAI: <message>\n..."
             Returns empty string if no history exists
    """
    history = get_history(session_id)

    if not history:
        return ""

    # Get last N messages
    recent_messages = history[-max_messages:]

    # Format messages as string
    formatted_lines = []
    for message in recent_messages:
        if isinstance(message, HumanMessage):
            formatted_lines.append(f"Human: {message.content}")
        elif isinstance(message, AIMessage):
            formatted_lines.append(f"AI: {message.content}")

    return "\n".join(formatted_lines)


def get_all_sessions() -> List[str]:
    """
    Get list of all active session IDs

    Returns:
        list: List of session ID strings
    """
    return list(_chat_histories.keys())


def get_session_message_count(session_id: str) -> int:
    """
    Get the number of messages in a session

    Args:
        session_id: Unique identifier for the chat session

    Returns:
        int: Number of messages in the session
    """
    return len(get_history(session_id))
