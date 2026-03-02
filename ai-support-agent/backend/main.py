"""
FastAPI application for ShopNest AI Support Agent
Provides WebSocket streaming for real-time chat interactions
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage

from agent.graph import compiled_graph
from agent.memory import add_message, get_history
from agent import rag  # Import to trigger RAG initialization

# Initialize FastAPI app
app = FastAPI(title="ShopNest AI Support Agent API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

                # Build LangGraph input state
                input_state: Dict[str, Any] = {
                    "messages": history,
                    "session_id": session_id,
                    "context": ""
                }

                # Stream response from LangGraph
                full_response = ""

                try:
                    # Use astream_events for token streaming (v2)
                    async for event in compiled_graph.astream_events(
                        input_state,
                        version="v2"
                    ):
                        # Filter for chat model streaming events
                        event_type = event.get("event", "")

                        if event_type == "on_chat_model_stream":
                            # Extract token content
                            chunk = event.get("data", {}).get("chunk", {})

                            if hasattr(chunk, "content"):
                                token = chunk.content
                            elif isinstance(chunk, dict):
                                token = chunk.get("content", "")
                            else:
                                token = str(chunk)

                            if token:
                                # Send token to client
                                await websocket.send_text(token)
                                full_response += token

                except Exception as stream_error:
                    print(f"⚠️ Streaming error: {stream_error}")

                    # Fallback: run graph without streaming
                    result = compiled_graph.invoke(input_state)

                    # Extract AI response from result
                    messages = result.get("messages", [])
                    if messages:
                        last_message = messages[-1]
                        full_response = getattr(last_message, "content", str(last_message))

                        # Send full response
                        await websocket.send_text(full_response)

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
                import traceback
                traceback.print_exc()

                await websocket.send_text(json.dumps({
                    "error": f"Error processing message: {str(e)}"
                }))
                await websocket.send_text("__END__")

    except WebSocketDisconnect:
        print(f"🔌 WebSocket disconnected for session: {session_id}")
    except Exception as e:
        print(f"❌ WebSocket error for session {session_id}: {e}")
        import traceback
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
    print("📡 Server will be available at: http://localhost:8000")
    print("📡 WebSocket endpoint: ws://localhost:8000/ws/{session_id}")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("="*80 + "\n")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
