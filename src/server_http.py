import os
import sys
import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import dotenv

# Ensure project root is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.engine.router import SemanticRouter
from src.utils.prompt_loader import load_agent_prompt, get_agent_metadata
# Reuse logic from server.py where possible, or reimplement lightweight version
from src.server import get_dynamic_context_string, enrich_agent_prompt

# Load env
env_path = os.path.join(os.path.dirname(__file__), "../.env")
dotenv.load_dotenv(env_path)

app = FastAPI()
logger = logging.getLogger("http-bridge")
logging.basicConfig(level=logging.INFO)

# Initialize Core Components
router = SemanticRouter()

# LLM Client (Simple OpenAI wrapper for demo)
from openai import OpenAI, AsyncOpenAI
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatRequest(BaseModel):
    query: str
    history: List[str] = []

class ChatResponse(BaseModel):
    agent: str
    response: str
    reasoning: Optional[str] = None

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    query = request.query
    logger.info(f"Received query: {query}")

    try:
        # 1. Route
        # We use a simplified routing flow here
        decision = await router.lookup_cache(query, {"history_text": "\n".join(request.history)})

        target_agent = "universal_agent"
        reasoning = "Default fallback"

        if decision:
            target_agent = decision.target_agent
            reasoning = decision.reasoning
        else:
            # Simple keyword fallback or meta-query check could go here
            pass

        # 2. Load Context
        base_prompt = load_agent_prompt(target_agent)
        metadata = get_agent_metadata(target_agent)
        preferred_skills = metadata.get("preferred_skills", [])

        final_system_prompt = await enrich_agent_prompt(
            target_agent,
            base_prompt,
            query,
            request.history,
            preferred_skills
        )

        # 3. Call LLM
        # We append the system prompt and the user query
        messages = [
            {"role": "system", "content": final_system_prompt},
        ]

        # Add history if needed (simplified)
        for msg in request.history[-5:]: # last 5 messages
            messages.append({"role": "user", "content": msg}) # Assuming all history is user for now

        messages.append({"role": "user", "content": query})

        logger.info(f"Calling LLM with agent: {target_agent}")
        completion = await client.chat.completions.create(
            model="gpt-4o", # Or gpt-3.5-turbo
            messages=messages,
            temperature=0.7
        )

        response_text = completion.choices[0].message.content

        return ChatResponse(
            agent=target_agent,
            response=response_text,
            reasoning=reasoning
        )

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
