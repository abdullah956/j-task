"""
LangGraph-based AI support agent for ShopNest
Combines RAG retrieval, tool usage, and conversational flow
"""

import sys
import traceback
from pathlib import Path
from typing_extensions import TypedDict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, FunctionMessage
from langchain_core.utils.function_calling import convert_to_openai_function
from groq import Groq

from config import Config
from agent.tools import TOOLS
from agent.rag import retrieve_relevant_chunks
from utils.helpers import extract_order_id, is_order_tracking_query, format_error_message


# Define the agent state
class AgentState(TypedDict):
    """State for the support agent graph"""
    messages: list
    session_id: str
    context: str
    _handled: bool  # Flag to skip agent node if already handled


# Initialize Groq client
groq_client = Groq(api_key=Config.GROQ_API_KEY)

# Initialize tool executor
tool_executor = ToolExecutor(TOOLS)

# Convert tools to function definitions
tool_definitions = [convert_to_openai_function(tool) for tool in TOOLS]


def retrieve_context_node(state: AgentState) -> AgentState:
    """
    Retrieve relevant FAQ context based on the last human message
    Also detects order tracking requests and handles them directly

    Args:
        state: Current agent state

    Returns:
        AgentState: Updated state with context field populated
    """
    # Get the last human message
    messages = state.get("messages", [])
    last_human_message = ""

    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            last_human_message = message.content
            break

    # Check if this is an order tracking request
    if last_human_message and is_order_tracking_query(last_human_message):
        order_id = extract_order_id(last_human_message)
        if order_id:
            # Execute the tool directly
            from agent.tools import get_order_status
            try:
                result = get_order_status(order_id)
                formatted_response = f"I found your order! Here are the details:\n\n{result}"

                # Add AI response with the order details
                state["messages"] = messages + [AIMessage(content=formatted_response)]
                state["context"] = ""  # No FAQ context needed

                # Mark that we handled this (skip agent node)
                state["_handled"] = True
                return state

            except Exception as e:
                error_msg = f"Sorry, I couldn't retrieve that order: {str(e)}"
                state["messages"] = messages + [AIMessage(content=error_msg)]
                state["_handled"] = True
                return state

    # Normal FAQ handling - retrieve relevant chunks
    if last_human_message:
        relevant_chunks = retrieve_relevant_chunks(last_human_message)
        context = "\n\n".join(relevant_chunks)
    else:
        context = ""

    # Update state with context
    state["context"] = context
    state["_handled"] = False

    return state


def build_groq_messages(context: str, messages: list) -> tuple[str, list]:
    """
    Build system prompt and Groq-formatted messages

    Args:
        context: FAQ context from RAG
        messages: LangChain message history

    Returns:
        tuple: (system_prompt, groq_messages)
    """
    system_prompt = f"""You are a helpful customer support agent for ShopNest, an e-commerce company.

CRITICAL RULE #1 - TOOL CALLING (HIGHEST PRIORITY):
If the user's message contains a specific ORDER ID (a 4-digit number like 1001, 1002, etc.) AND asks about order status/tracking/location, you MUST respond with EXACTLY:
TOOL_CALL: get_order_status XXXX

Replace XXXX with the order ID. DO NOT add anything else. Just that one line.

Examples:
- User: "track order 1001" → You: "TOOL_CALL: get_order_status 1001"
- User: "what's the status of 1003?" → You: "TOOL_CALL: get_order_status 1003"
- User: "where is my order 1005" → You: "TOOL_CALL: get_order_status 1005"

RULE #2 - FAQ QUESTIONS:
For general questions WITHOUT a specific order ID (like "how do I track orders?", "what's your return policy?"), use this FAQ context:
{context}

IMPORTANT: If there's an order ID in the message, IGNORE the FAQ context and use TOOL_CALL instead!

Be concise, friendly, and helpful."""

    # Convert LangChain messages to Groq format
    groq_messages = [{"role": "system", "content": system_prompt}]

    for msg in messages:
        if isinstance(msg, HumanMessage):
            groq_messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            groq_messages.append({"role": "assistant", "content": msg.content})

    return system_prompt, groq_messages


def agent_node(state: AgentState) -> AgentState:
    """
    Main agent reasoning node - builds prompt and calls LLM

    Args:
        state: Current agent state

    Returns:
        AgentState: Updated state with new AI message
    """
    # Get context and messages from state
    context = state.get("context", "")
    messages = state.get("messages", [])

    # Build prompt and messages
    _, groq_messages = build_groq_messages(context, messages)

    # Call Groq API (non-streaming for LangGraph compatibility)
    try:
        completion = groq_client.chat.completions.create(
            model=Config.GROQ_MODEL,
            messages=groq_messages,
            temperature=Config.GROQ_TEMPERATURE,
            max_tokens=Config.GROQ_MAX_TOKENS,
            stream=False,  # Non-streaming for LangGraph
        )

        response_content = completion.choices[0].message.content

        # Add AI response to messages
        state["messages"] = messages + [AIMessage(content=response_content)]

    except Exception as e:
        print(f"❌ Groq API Error: {e}")
        traceback.print_exc()
        error_msg = format_error_message(e, "Groq API")
        state["messages"] = messages + [AIMessage(content=error_msg)]

    return state


async def stream_agent_response(context: str, messages: list):
    """
    Stream LLM response token by token (for WebSocket streaming)

    This bypasses LangGraph and calls Groq directly with streaming enabled.

    Args:
        context: FAQ context from RAG
        messages: LangChain message history

    Yields:
        str: Token chunks from the LLM
    """
    # Build prompt and messages
    _, groq_messages = build_groq_messages(context, messages)

    try:
        # Call Groq API with streaming enabled
        completion = groq_client.chat.completions.create(
            model=Config.GROQ_MODEL,
            messages=groq_messages,
            temperature=Config.GROQ_TEMPERATURE,
            max_tokens=Config.GROQ_MAX_TOKENS,
            stream=True,  # Enable streaming!
        )

        # Yield each token as it arrives
        for chunk in completion:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    except Exception as e:
        print(f"❌ Groq API Streaming Error: {e}")
        traceback.print_exc()
        yield format_error_message(e, "Groq API")


def tool_node(state: AgentState) -> AgentState:
    """
    Execute tools based on tool calls in the last AI message

    For this simplified version without bind_tools, we parse the AI response
    for tool invocations and execute them.

    Args:
        state: Current agent state

    Returns:
        AgentState: Updated state with tool results
    """
    messages = state.get("messages", [])
    last_message = messages[-1]

    # Check if the message content mentions using a tool
    if not isinstance(last_message, AIMessage):
        return state

    content = last_message.content

    # Look for explicit tool call pattern
    import re
    tool_call_pattern = r'TOOL_CALL:\s*get_order_status\s+(\d{4})'
    tool_call_match = re.search(tool_call_pattern, content)

    if tool_call_match:
        order_id = tool_call_match.group(1)

        # Execute get_order_status tool
        tool_invocation = ToolInvocation(
            tool="get_order_status",
            tool_input={"order_id": order_id}
        )

        try:
            result = tool_executor.invoke(tool_invocation)

            # Format the result nicely for the user
            formatted_response = f"I found your order! Here are the details:\n\n{result}"

            # Replace the last AI message (the TOOL_CALL) with the actual result
            # Remove the TOOL_CALL message and add the formatted result
            state["messages"] = messages[:-1] + [AIMessage(content=formatted_response)]

        except Exception as e:
            error_msg = f"Sorry, I couldn't retrieve that order: {str(e)}"
            state["messages"] = messages[:-1] + [AIMessage(content=error_msg)]

    return state


def should_continue(state: AgentState) -> str:
    """
    Determine if we should continue to tools or end

    Checks if we should execute tools based on message count to avoid loops.

    Args:
        state: Current agent state

    Returns:
        str: "tools" to execute tools, "end" to finish
    """
    messages = state.get("messages", [])
    if len(messages) < 2:
        return "end"

    # Count AI messages - if we have 2+, we've already done agent→tools→agent loop
    ai_count = sum(1 for msg in messages if isinstance(msg, AIMessage))

    # If we have 2+ AI messages, we've completed the tool loop, so end
    if ai_count >= 2:
        return "end"

    # Get last human message
    last_human = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_human = msg
            break

    if not last_human:
        return "end"

    # Check if user asks about an order with ID
    if is_order_tracking_query(last_human.content):
        if extract_order_id(last_human.content):
            # Only go to tools if this is the first AI response
            if ai_count == 1:
                return "tools"

    return "end"


# Build the graph
def create_support_agent_graph():
    """
    Create and compile the LangGraph support agent

    Returns:
        Compiled LangGraph application
    """
    # Initialize graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("retrieve_context", retrieve_context_node)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)

    # Helper function to check if order was handled in retrieve_context
    def check_if_handled(state: AgentState) -> str:
        return "end" if state.get("_handled", False) else "agent"

    # Define edges
    # Set entry point → retrieve_context_node
    workflow.set_entry_point("retrieve_context")

    # retrieve_context_node → check if already handled → agent or end
    workflow.add_conditional_edges(
        "retrieve_context",
        check_if_handled,
        {
            "agent": "agent",
            "end": END
        }
    )

    # agent_node → END (simplified - no tool loop in this version)
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )

    # tool_node → agent_node (loop back after tool execution)
    workflow.add_edge("tools", "agent")

    # Compile the graph
    compiled = workflow.compile()

    return compiled


# Export compiled graph
compiled_graph = create_support_agent_graph()
