from transformers import pipeline
import os

summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn",
    device=0 if os.getenv("USE_GPU","0") == "1" else -1
)

async def call_summarizer(text: str) -> str:
    # Limita a 1024 tokens (~ 750 palabras) para evitar overflow
    truncated = text[:1000]
    out = summarizer(truncated, max_length=150, min_length=30, do_sample=False)
    return out[0]["summary_text"]
