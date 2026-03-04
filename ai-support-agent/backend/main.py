"""
FastAPI application for ShopNest AI Support Agent
Provides WebSocket streaming for real-time chat interactions
"""

import sys
import json
import traceback
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage

from config import Config
from agent.graph import compiled_graph, stream_agent_response
from agent.memory import add_message, get_history
from agent.rag import retrieve_relevant_chunks
from agent import rag  # Import to trigger RAG initialization
from utils.helpers import is_order_tracking_query, extract_order_id

# Initialize FastAPI app
app = FastAPI(title="ShopNest AI Support Agent API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=Config.CORS_ALLOW_CREDENTIALS,
    allow_methods=Config.CORS_ALLOW_METHODS,
    allow_headers=Config.CORS_ALLOW_HEADERS,
)


@app.on_event("startup")
async def startup_event():
    """
    Initialize the application on startup
    """
    print("\n" + "="*80)
    print("🚀 Starting ShopNest AI Support Agent API")
    print("="*80)
    print("✅ RAG system initialized (loaded on import)")
    print("✅ LangGraph agent compiled and ready")
    print("✅ WebSocket endpoint available at: /ws/{session_id}")
    print("="*80 + "\n")


@app.get("/health")
async def health_check():
    """
    Health check endpoint

    Returns:
        dict: Status information
    """
    return {
        "status": "ok",
        "service": "ShopNest AI Support Agent",
        "rag_initialized": rag.vector_store is not None,
        "graph_ready": compiled_graph is not None
    }


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time chat streaming

    Args:
        websocket: WebSocket connection
        session_id: Unique session identifier for the conversation
    """
    await websocket.accept()
    print(f"🔌 WebSocket connected for session: {session_id}")

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            try:
                # Parse JSON message
                message_data = json.loads(data)
                user_message = message_data.get("message", "")

                if not user_message:
                    await websocket.send_text(json.dumps({
                        "error": "Empty message received"
                    }))
                    continue

                print(f"📨 Received from {session_id}: {user_message[:50]}...")

                # Add user message to memory
                add_message(session_id, "human", user_message)

                # Get full conversation history
                history = get_history(session_id)

                # Check if this is an order tracking request (handle directly)
                if is_order_tracking_query(user_message):
                    order_id = extract_order_id(user_message)
                    if order_id:
                        # Direct tool call - no streaming needed
                        from agent.tools import get_order_status
                        try:
                            result = get_order_status(order_id)
                            full_response = f"I found your order! Here are the details:\n\n{result}"
                            await websocket.send_text(full_response)
                        except Exception as e:
                            full_response = f"Sorry, I couldn't retrieve that order: {str(e)}"
                            await websocket.send_text(full_response)

                        # Save and send end marker
                        add_message(session_id, "ai", full_response)
                        await websocket.send_text("__END__")
                        continue

                # Regular FAQ question - use streaming!
                full_response = ""

                try:
                    # Get RAG context
                    context = ""
                    if user_message:
                        relevant_chunks = retrieve_relevant_chunks(user_message)
                        context = "\n\n".join(relevant_chunks)

                    # Stream the response token by token
                    async for token in stream_agent_response(context, history):
                        full_response += token
                        await websocket.send_text(token)

                except Exception as error:
                    print(f"❌ Streaming error: {error}")
                    traceback.print_exc()

                    error_msg = "I apologize, but I'm having trouble processing your request. Please try again."
                    await websocket.send_text(error_msg)
                    full_response = error_msg

                # Save AI response to memory
                if full_response:
                    add_message(session_id, "ai", full_response)
                    print(f"💬 Response sent to {session_id}: {full_response[:50]}...")

                # Send end-of-stream sentinel
                await websocket.send_text("__END__")

            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "error": "Invalid JSON format"
                }))
            except Exception as e:
                print(f"❌ Error processing message: {e}")
                traceback.print_exc()

                await websocket.send_text(json.dumps({
                    "error": f"Error processing message: {str(e)}"
                }))
                await websocket.send_text("__END__")

    except WebSocketDisconnect:
        print(f"🔌 WebSocket disconnected for session: {session_id}")
    except Exception as e:
        print(f"❌ WebSocket error for session {session_id}: {e}")
        traceback.print_exc()
    finally:
        print(f"🔒 WebSocket closed for session: {session_id}")


@app.get("/")
async def root():
    """
    Root endpoint with API information

    Returns:
        dict: API information
    """
    return {
        "service": "ShopNest AI Support Agent API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "websocket": "/ws/{session_id}"
        },
        "documentation": "/docs"
    }


if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*80)
    print("🚀 Starting ShopNest AI Support Agent Server")
    print("="*80)
    print(f"📡 Server will be available at: http://localhost:{Config.BACKEND_PORT}")
    print(f"📡 WebSocket endpoint: ws://localhost:{Config.BACKEND_PORT}/ws/{{session_id}}")
    print(f"📚 API Documentation: http://localhost:{Config.BACKEND_PORT}/docs")
    print("="*80 + "\n")

    uvicorn.run(
        "main:app",
        **Config.get_uvicorn_config()
    )
