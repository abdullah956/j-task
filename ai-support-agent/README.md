# ShopNest AI Support Agent

An AI-powered customer support chatbot with RAG (Retrieval Augmented Generation), function calling, conversation memory, and real-time streaming responses.

## 🎯 Features

### 1. **Knowledge Base / RAG**
- FAISS vector store with company policies (FAQ)
- Semantic search using sentence-transformers
- 40 chunks from 10 policy paragraphs
- Retrieves top-3 relevant chunks per query

### 2. **Function Calling / Tools**
- `get_order_status()` function for order tracking
- Mock database with 8 dummy orders
- Autonomous tool execution by LLM
- Natural language responses from tool results

### 3. **Chat History (Memory)**
- Per-session conversation context
- References previous messages
- In-memory storage per browser tab

### 4. **Streaming Responses**
- WebSocket-based real-time streaming
- Token-by-token display (ChatGPT-style)
- React frontend with streaming cursor

---

## 🏗️ Architecture

```
React Frontend (Port 5173)
    ↓ WebSocket
FastAPI Backend (Port 8000)
    ↓
LangGraph Agent
    ├─► RAG System (FAISS)
    ├─► Tools (get_order_status)
    └─► Memory (Session-based)
    ↓
Ollama (Port 11434) → Mistral LLM
```

---

## 🚀 Quick Start (Docker - Recommended)

### Prerequisites
- Docker & Docker Compose installed
- Ollama installed locally ([Download](https://ollama.ai/download))
- Mistral model downloaded

### Steps

**1. Install Ollama & Download Mistral**

```bash
# Install Ollama
# macOS:
brew install ollama

# Linux:
curl -fsSL https://ollama.ai/install.sh | sh

# Windows: Download from https://ollama.ai/download

# Download Mistral model (one-time, ~4GB)
ollama pull mistral

# Start Ollama server
ollama serve
```

**2. Clone & Start Application**

```bash
# Clone the repository
git clone <your-repo-url>
cd ai-support-agent

# Start with Docker
docker-compose up --build
```

**3. Open in browser**
```
http://localhost:5173
```

---

## 🛠️ Manual Setup (Without Docker)

### Prerequisites
- Python 3.11+
- Node.js 18+
- Ollama with Mistral model

### Backend Setup

```bash
# Make sure Ollama is running
ollama serve

# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the backend
python main.py
```

Backend will start on http://localhost:8000

### Frontend Setup

```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run the frontend
npm run dev
```

Frontend will start on http://localhost:5173

---

## 📁 Project Structure

```
ai-support-agent/
├── backend/
│   ├── agent/
│   │   ├── graph.py           # LangGraph agent (3 nodes)
│   │   ├── rag.py             # FAISS vector store
│   │   ├── tools.py           # get_order_status function
│   │   └── memory.py          # Conversation memory
│   ├── db/
│   │   └── orders.py          # Mock orders database (8 orders)
│   ├── data/
│   │   └── faq.txt            # Company policies (10 paragraphs)
│   ├── faiss_index/           # Vector embeddings (auto-generated)
│   ├── main.py                # FastAPI + WebSocket server
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── ChatWidget.jsx # Chat UI component
│   │   ├── hooks/
│   │   │   └── useWebSocket.js # WebSocket connection
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 💬 Usage Examples

### Example 1: Policy Question (RAG)
**User**: "What is your return policy?"

**Response**: The AI retrieves relevant chunks from `faq.txt` using FAISS and answers:
> "ShopNest offers a 30-day return policy for most items. Items must be unused, in original packaging, with proof of purchase. Refunds are processed within 5-7 business days..."

### Example 2: Order Tracking (Function Calling)
**User**: "Where is order 1001?"

**Response**: The AI calls `get_order_status("1001")` and responds:
> "Your order #1001 for Blue Wireless Headphones is currently Shipped and will arrive in approximately 2 days."

### Example 3: Conversation Memory
**User**: "My order number is 1001"
**AI**: "Got it! How can I help with order #1001?"
**User**: "What's its status?"
**AI**: "Order #1001 for Blue Wireless Headphones is Shipped and will arrive in 2 days."

---

## 🧠 How It Works

### LangGraph Agent (3 Nodes)

#### 1. **retrieve_context_node**
- Extracts last user message
- Queries FAISS vector store
- Returns top-3 relevant FAQ chunks

#### 2. **agent_node**
- Receives conversation history + FAQ context
- Calls Ollama Mistral LLM
- Decides: answer directly OR use tool

#### 3. **tool_node**
- Detects if order tracking is needed
- Executes `get_order_status()` function
- Returns result to agent for formatting

### Data Flow

```
User: "What is your return policy?"
   ↓
WebSocket → Backend
   ↓
retrieve_context_node → FAISS search → Returns 3 FAQ chunks
   ↓
agent_node → Ollama Mistral with context → Generates answer
   ↓
Stream tokens back → Frontend displays
   ↓
User sees: "ShopNest offers a 30-day return policy..."
```

---

## 🗄️ Data Locations

### FAQ Data
- **File**: `backend/data/faq.txt`
- **Size**: 7,739 characters
- **Content**: 10 policy paragraphs (returns, shipping, warranty, etc.)

### Vector Store (FAISS)
- **Location**: `backend/faiss_index/`
- **Files**:
  - `index.faiss` (61 KB) - Vector embeddings
  - `index.pkl` (13 KB) - Original text chunks
- **Chunks**: 40 chunks (300 chars each, 50 char overlap)
- **Embeddings**: 384-dimensional vectors (all-MiniLM-L6-v2)

### Orders Database
- **File**: `backend/db/orders.py`
- **Type**: Python dictionary (in-memory)
- **Orders**: 8 dummy orders (IDs: 1001-1008)

### Conversation Memory
- **File**: `backend/agent/memory.py`
- **Type**: In-memory dict `{session_id: [messages]}`
- **Scope**: Per browser tab
- **Persistence**: Lost on backend restart

---

## ⚙️ Configuration

### Environment Variables

```env
# .env file

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=mistral

# Backend Config
BACKEND_PORT=8000
BACKEND_HOST=0.0.0.0

# Frontend Config
FRONTEND_PORT=5173
VITE_API_URL=http://localhost:8000
```

---

## 🐛 Troubleshooting

### "Connection refused to Ollama"
**Solution**: Make sure Ollama is running:
```bash
ollama serve
```

### "Model 'mistral' not found"
**Solution**: Download the Mistral model:
```bash
ollama pull mistral
```

### "Port 8000 already in use"
**Solution**:
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use port 8001 instead
```

### "FAISS index not found"
**Solution**: The index is auto-generated on first run. If deleted, restart backend:
```bash
docker-compose restart backend
```

### "WebSocket connection failed"
**Solution**:
1. Check backend is running: http://localhost:8000/health
2. Check browser console for errors
3. Ensure CORS is configured (already done in `main.py`)

### Docker can't connect to Ollama
**Solution**: Make sure Ollama is running on host machine (not in Docker):
```bash
# On host machine (not in Docker)
ollama serve
```

The Docker backend connects via `host.docker.internal:11434`

---

## 🧪 Testing the Agent

### Test 1: Policy Questions (RAG)
```
Q: "What is your return policy?"
Q: "Do you offer free shipping?"
Q: "What payment methods do you accept?"
```

### Test 2: Order Tracking (Tools)
```
Q: "Track order 1001"
Q: "Where is my order 1005?"
Q: "What's the status of order #1003?"
```

### Test 3: Memory
```
User: "My order is 1001"
AI: "How can I help with order #1001?"
User: "What's its status?"  ← AI remembers "its" = order 1001
```

---

## 🔧 Technology Stack

### Backend
- **Framework**: FastAPI
- **Agent**: LangGraph + LangChain
- **LLM**: Ollama with Mistral model
- **Vector DB**: FAISS
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **WebSocket**: FastAPI WebSockets

### Frontend
- **Framework**: React 18 + Vite
- **WebSocket**: Native WebSocket API
- **Styling**: Inline CSS (teal theme)

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Python**: 3.11
- **Node.js**: 18

---

## 📊 API Endpoints

### WebSocket
```
ws://localhost:8000/ws/{session_id}
```
**Send**:
```json
{"message": "What is your return policy?"}
```
**Receive**: Streaming tokens + `__END__` sentinel

### HTTP
```
GET /health
GET /
GET /docs  (FastAPI auto-generated docs)
```

---

## 🎥 Demo Video

> **Note**: A Loom video demonstration is included showing:
> 1. Application running
> 2. Policy question (RAG)
> 3. Order tracking (Function calling)
> 4. Conversation memory
> 5. Architecture explanation

[Link to Loom video]

---

## 📝 Setup Notes for Reviewers

### Important: Ollama Requirement

This project uses **Ollama with Mistral** as the LLM provider for a completely free, local setup.

**To run this project, reviewers must**:
1. Install Ollama: https://ollama.ai/download
2. Download Mistral model: `ollama pull mistral` (~4GB, one-time)
3. Run Ollama server: `ollama serve`
4. Then run: `docker-compose up --build`

**Why Ollama?**
- ✅ 100% free (no API costs)
- ✅ Runs completely locally (no external API keys)
- ✅ Privacy-friendly (no data sent to cloud)
- ✅ Works offline once model is downloaded

**Alternative**: If you prefer cloud-based LLM, the code can be easily switched to OpenAI/Anthropic by changing `backend/agent/graph.py` to use `ChatOpenAI` instead of `ChatOllama`.

---

## 📝 Development Notes

### Adding New Policies
1. Edit `backend/data/faq.txt`
2. Delete `backend/faiss_index/` folder
3. Restart backend (auto-rebuilds index)

### Adding New Orders
Edit `backend/db/orders.py`:
```python
ORDERS_DB = {
    "1009": {
        "order_id": "1009",
        "status": "Delivered",
        "item": "New Product",
        ...
    }
}
```

### Changing LLM Model
Update `.env`:
```env
MODEL_NAME=llama2  # or any other Ollama model
```

Then pull the model:
```bash
ollama pull llama2
```

---

## 📄 License

MIT License - Free to use for educational and commercial purposes.

---

## 👤 Author

Created for University of South Asia Technical Assessment

**Submission Date**: [Your submission date]

---

## 🙋 Support

For issues or questions about this project:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review error messages in Docker logs: `docker-compose logs`
3. Ensure Ollama is running: `ollama serve`

---

**Built with ❤️ using FastAPI, LangChain, LangGraph, React, and Ollama (Mistral)**
