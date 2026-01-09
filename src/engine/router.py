import logging
import sys
import os
import json
import asyncio
from langfuse import observe

logger = logging.getLogger(__name__)
from typing import List, Optional, Dict, Any
import chromadb
from chromadb.utils import embedding_functions
from openai import AsyncOpenAI
from pydantic import ValidationError

from src.schemas.protocol import RouterDecision, AgentRequest
# Import REPO_ROOT to locate agents
from src.utils.prompt_loader import REPO_ROOT

# Configuration
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "../../chroma_db")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
SIMILARITY_THRESHOLD = 0.95

class SemanticRouter:
    def __init__(self):
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

        # Use Sentence Transformers for embeddings
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )

        self.collection = self.chroma_client.get_or_create_collection(
            name="router_cache",
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )

        # Initialize OpenAI (lazy load)
        self.openai_client = None

        self.available_agents = self._scan_agents()

    def _scan_agents(self) -> List[str]:
        """
        Dynamically scans the .cursor/agents directory for available agents.
        """
        agents_dir = os.path.join(REPO_ROOT, ".cursor", "agents")
        if not os.path.exists(agents_dir):
            logger.warning(f"Agents directory not found at {agents_dir}. Fallback to empty list.")
            return []

        agents = []
        try:
            for entry in os.scandir(agents_dir):
                if entry.is_dir() and not entry.name.startswith(".") and entry.name != "common":
                    # Check if it has a system_prompt.mdc
                    if os.path.exists(os.path.join(entry.path, "system_prompt.mdc")):
                        agents.append(entry.name)
        except Exception as e:
            logger.error(f"Error scanning agents: {e}")

        # Ensure common agents are present if scan fails or directory is structured differently
        if not agents:
            # Fallback to minimal agent if scan completely fails
            logger.warning("Agent scan returned empty. Falling back to universal_agent only.")
            return ["universal_agent"]

        return sorted(agents)

    async def lookup_cache(self, query: str, context: Dict[str, Any] = None) -> Optional[RouterDecision]:
        """
        Only checks the cache. Returns None if miss.
        """
        history_text = context.get("history_text", "") if context else ""

        if history_text:
             # Create a context-aware query for semantic search
             semantic_query = f"{history_text[-200:]}\n{query}" # Last 200 chars of context
        else:
             semantic_query = query

        # ChromaDB query is blocking, run in executor
        loop = asyncio.get_running_loop()
        try:
            results = await loop.run_in_executor(
                None,
                lambda: self.collection.query(
                    query_texts=[semantic_query],
                    n_results=1
                )
            )
        except Exception as e:
            logger.error(f"ChromaDB lookup failed: {e}")
            return None

        if results['ids'] and results['distances'] and len(results['distances'][0]) > 0:
            distance = results['distances'][0][0]
            if distance < (1 - SIMILARITY_THRESHOLD):
                metadata = results['metadatas'][0][0]
                return RouterDecision(
                    target_agent=metadata['target_agent'],
                    confidence=1.0,
                    reasoning=f"Cached result (distance: {distance:.4f})",
                    is_cached=True
                )
        return None

    async def update_cache(self, query: str, agent_name: str, reasoning: str, request_id: str):
        """
        Manually adds an entry to the cache.
        """
        loop = asyncio.get_running_loop()
        try:
            await loop.run_in_executor(
                None,
                lambda: self.collection.add(
                    documents=[query],
                    metadatas=[{
                        "target_agent": agent_name,
                        "reasoning": reasoning,
                        "timestamp": str(1.0)
                    }],
                    ids=[request_id]
                )
            )
        except Exception as e:
            logger.error(f"Failed to update cache: {e}")

    @observe(name="router_llm_decision")
    async def _get_llm_decision(self, query: str, context: Dict[str, Any] = None) -> RouterDecision:
        """
        Fallback to LLM if no cache hit.
        """
        if not self.openai_client:
            try:
                self.openai_client = AsyncOpenAI()
            except Exception as e:
                logger.error(f"Failed to init OpenAI: {e}")
                return RouterDecision(
                    target_agent="universal_agent",
                    confidence=0.0,
                    reasoning="OpenAI API Key missing or invalid",
                    is_cached=False
                )

        system_prompt = f"""
        You are the Master Router for the Agents system.
        Your job is to classify the user's request into one of the following agent profiles:
        {json.dumps(self.available_agents)}

        Analyze the intent and complexity.
        Return a JSON object with the following fields:
        - "target_agent": (string) One of the available agents.
        - "confidence": (float) 0.0 to 1.0.
        - "reasoning": (string) Explanation for the choice.

        Example:
        {{
            "target_agent": "security_expert",
            "confidence": 0.95,
            "reasoning": "User is asking about SQL injection prevention."
        }}
        """

        messages = [{"role": "system", "content": system_prompt}]

        if context:
            history_text = context.get("history_text", "")
            if history_text:
                 messages.append({"role": "user", "content": f"Context/History:\n{history_text}"})

        messages.append({"role": "user", "content": query})

        try:
            completion = await self.openai_client.chat.completions.create(
                model="gpt-5-mini",
                messages=messages,
                response_format={"type": "json_object"}
            )

            response_content = completion.choices[0].message.content
            decision_data = json.loads(response_content)

            # Ensure it matches schema
            return RouterDecision(**decision_data)

        except Exception as e:
            logger.error(f"Routing Error: {e}")
            return RouterDecision(
                target_agent="universal_agent",
                confidence=0.0,
                reasoning=f"Error in routing: {str(e)}",
                is_cached=False
            )

    @observe(name="route_request")
    async def route(self, request: AgentRequest) -> RouterDecision:
        """
        Full routing logic: Cache -> LLM -> Cache Update
        """
        query_text = request.query
        context = request.context

        # 1. Search Cache
        cached = await self.lookup_cache(query_text, context)
        if cached:
            return cached

        # 2. LLM Fallback
        decision = await self._get_llm_decision(query_text, context)

        # 3. Update Cache
        if decision.confidence > 0.8:
            await self.update_cache(query_text, decision.target_agent, decision.reasoning, request.request_id)

        return decision
