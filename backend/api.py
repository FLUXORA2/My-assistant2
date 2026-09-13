from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()                       # carga .env
from model_router import choose_model, call_llm, store_embeddings, get_context, save_message
from summarizer import call_summarizer

app = FastAPI()

# -------------------------------------------------
# 1️⃣  Chat endpoint
# -------------------------------------------------
class ChatRequest(BaseModel):
    messages: list[dict]          # [{role:"user",content:"..."}]
    history_id: str               # identificador de sesión

@app.post("/chat")
async def chat(req: ChatRequest):
    # 1️⃣ Contexto previo (si existe)
    context = await get_context(req.history_id)

    # 2️⃣ Prompt completo
    prompt = f"Context: {context}\n\nUser: {req.messages[-1]['content']}"
    # 3️⃣ Elegir modelo según tokens disponibles
    model_name = await choose_model(prompt)
    # 4️⃣ Llamar al LLM
    answer = await call_llm(model_name, prompt)

    # 5️⃣ Guardar intercambio
    await save_message(req.history_id, req.messages[-1]['content'], answer)

    return {"response": answer, "model": model_name}

# -------------------------------------------------
# 2️⃣  Document ingestion
# -------------------------------------------------
class UploadReq(BaseModel):
    file: bytes
    mime: str
    history_id: str

@app.post("/ingest")
async def ingest(req: UploadReq):
    text = extract_text(req.file, req.mime)
    ids = await store_embeddings(req.history_id, text)
    return {"ids": ids}

# -------------------------------------------------
# 3️⃣  Summarize endpoint
# -------------------------------------------------
class SummarizeReq(BaseModel):
    text: str
    max_words: int = 300

@app.post("/summarize")
async def summarize(req: SummarizeReq):
    summary = await call_summarizer(req.text)
    return {"summary": summary}

# -------------------------------------------------
# 4️⃣  Health check
# -------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "OK"}
