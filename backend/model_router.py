import os, tiktoken
from langchain.llms import Ollama
from chromadb import PersistentClient
from sentence_transformers import HuggingFaceEmbeddings

# ------------------- CONFIG -------------------
MODELS = os.getenv("MODELS", "llama3:70b,mistral:7b,phi:2").split(",")
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "7500"))
# ---------------------------------------------

client = PersistentClient(path=CHROMA_PATH)
embeddings = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")
vector_store = client.get_collection(name="assistant_docs", embeddings_backend=embeddings)

def count_tokens(text: str, model_name: str) -> int:
    enc = tiktoken.encoding_for_model(model_name)
    return len(enc.encode(text))

async def choose_model(prompt: str) -> str:
    for idx, model in enumerate(MODELS):
        approx = count_tokens(prompt, model) + 1000   # margen para respuesta
        if approx <= MAX_TOKENS:
            return model
    return MODELS[-1]   # fallback al último modelo

async def call_llm(model_name: str, prompt: str) -> str:
    llm = Ollama(model=model_name, temperature=0.2)
    result = await llm.ainvoke(prompt)
    return result

# ------------------- VECTOR STORE -------------------
async def store_embeddings(history_id: str, text: str):
    # Simple splitter (500 chars por chunk)
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    ids = []
    for i, chunk in enumerate(chunks):
        embedding = embeddings.embed_query(chunk)
        ids.append(vector_store.add(
            documents=[chunk],
            embeddings=[embedding],
            ids=[f"{history_id}_{i}"]
        ))
    return ids

async def get_context(history_id: str) -> str:
    results = vector_store.get(history_id)
    return "\n".join(res["documents"][0] for res in results)

async def save_message(history_id: str, user_msg: str, assistant_msg: str):
    # Aquí guardamos la conversación en una tabla simple de la base de datos
    # (para este ejemplo usamos una colección de Chroma con un campo "conversation")
    await vector_store.add(
        documents=[user_msg, assistant_msg],
        ids=[f"{history_id}_u_{int(time.time())}", f"{history_id}_a_{int(time.time())}"],
        embeddings=[[0]*384, [0]*384]   # embeddings dummy; el flujo real no los usa
    )
