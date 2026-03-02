"""
LangGraph-based AI support agent for ShopNest
Combines RAG retrieval, tool usage, and conversational flow
"""

import os
import sys
from pathlib import Path
from typing_extensions import TypedDict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, FunctionMessage
from langchain_community.chat_models import ChatOllama
from langchain_core.utils.function_calling import convert_to_openai_function

from agent.tools import TOOLS
from agent.rag import retrieve_relevant_chunks


# Define the agent state
class AgentState(TypedDict):
    """State for the support agent graph"""
    messages: list
    session_id: str
    context: str


# Initialize LLM with local Ollama
llm = ChatOllama(
    model="mistral",
    temperature=0.7,
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
)

# Initialize tool executor
tool_executor = ToolExecutor(TOOLS)

# Convert tools to function definitions
tool_definitions = [convert_to_openai_function(tool) for tool in TOOLS]


def retrieve_context_node(state: AgentState) -> AgentState:
    """
    Retrieve relevant FAQ context based on the last human message

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

    # Retrieve relevant chunks from FAQ
    if last_human_message:
        relevant_chunks = retrieve_relevant_chunks(last_human_message, k=3)
        context = "\n\n".join(relevant_chunks)
    else:
        context = ""

    # Update state with context
    state["context"] = context

    return state


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

    # Build system prompt with tool information
    tools_desc = "\n".join([
        f"- {tool.name}: {tool.description}" for tool in TOOLS
    ])

    system_prompt = f"""You are a helpful customer support agent for ShopNest, an e-commerce company.

Use the following FAQ context to answer policy questions:
{context}

Available tools:
{tools_desc}

If the user asks about an order, use the get_order_status tool.
Be concise, friendly, and helpful."""

    # Prepare messages for LLM (include system message)
    llm_messages = [SystemMessage(content=system_prompt)] + messages

    # Call LLM
    response = llm.invoke(llm_messages)

    # Add AI response to messages
    state["messages"] = messages + [response]

    return state


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

    content = last_message.content.lower()

    # Simple tool detection - look for order IDs in format like "1001", "1002", etc.
    if "order" in content or "track" in content or "status" in content:
        # Extract order ID from content (simple regex-like extraction)
        import re
        order_match = re.search(r'\b(\d{4})\b', last_message.content)

        if order_match:
            order_id = order_match.group(1)

            # Execute get_order_status tool
            tool_invocation = ToolInvocation(
                tool="get_order_status",
                tool_input={"order_id": order_id}
            )

            try:
                result = tool_executor.invoke(tool_invocation)

                # Create function message with result
                function_message = FunctionMessage(
                    name="get_order_status",
                    content=str(result)
                )

                # Add tool result to messages
                state["messages"] = messages + [function_message]

                # Add an AI message acknowledging the tool result
                ai_followup = AIMessage(content=str(result))
                state["messages"] = state["messages"] + [ai_followup]

            except Exception as e:
                error_msg = AIMessage(content=f"Error executing tool: {str(e)}")
                state["messages"] = messages + [error_msg]

    return state


def should_continue(_state: AgentState) -> str:
    """
    Determine if we should continue to tools or end

    For this simplified version, we always end after agent response
    since we don't have proper tool call detection in older LangChain versions.

    Args:
        _state: Current agent state (unused in this simplified version)

    Returns:
        str: "end" to finish the conversation turn
    """
    # In a more advanced version with tool support, we would check for tool calls here
    # For now, we always end after the agent responds
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

    # Define edges
    # Set entry point → retrieve_context_node
    workflow.set_entry_point("retrieve_context")

    # retrieve_context_node → agent_node
    workflow.add_edge("retrieve_context", "agent")

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
