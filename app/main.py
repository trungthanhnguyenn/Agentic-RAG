from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import ChatRequest, ChatResponse
from graph.graph import build_graph


app = FastAPI(title="Agentic RAG Chatbot")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


graph_runnable = build_graph()


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    init_state = {"question": req.question, "user_id": req.user_id}
    final_state = graph_runnable.invoke(init_state)
    return ChatResponse(final_answer=final_state.get("final_answer", ""), trace=final_state)


