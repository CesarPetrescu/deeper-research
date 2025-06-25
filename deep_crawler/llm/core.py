import toml
import hashlib
import functools
from pathlib import Path
from openai import OpenAI, OpenAIError

# Load config from root directory  
CFG = toml.load(Path(__file__).parents[2] / "config.toml")

client = OpenAI(
    base_url=CFG["llm"]["base_url"],
    api_key=CFG["llm"]["api_key"],
)

def chat(system, user, max_tokens=1024, model=None):
    model = model or CFG["llm"]["chat_model"]
    try:
        r = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            temperature=0.3,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}]
        )
        return r.choices[0].message.content.strip()
    except OpenAIError as e:
        raise RuntimeError(f"OpenAI chat error: {e}")

@functools.lru_cache(maxsize=1024)
def embed(text, model=None):
    model = model or CFG["api"]["embed_model"]
    r = client.embeddings.create(model=model, input=[text])
    return r.data[0].embedding, hashlib.md5(text.encode()).hexdigest()[:8]
