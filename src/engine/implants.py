import logging
import os
import glob
import yaml
import chromadb
from chromadb.utils import embedding_functions
from langfuse import observe
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Configuration
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "../../chroma_db")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
IMPLANTS_DIR = os.path.join(os.path.dirname(__file__), "../../.cursor/implants")
RELEVANCE_THRESHOLD = 0.73  # Cosine distance threshold

class ImplantRetriever:
    def __init__(self):
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

        # Use Sentence Transformers for embeddings
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )

        self.collection = self.chroma_client.get_or_create_collection(
            name="implants_store",
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )

        # Determine if we need to index (simple check: if empty)
        if self.collection.count() == 0:
            logger.info("Implant store is empty. Indexing implants...")
            self.index_implants()

    def index_implants(self):
        """
        Reads all .mdc files in IMPLANTS_DIR and indexes them.
        """
        implant_files = glob.glob(os.path.join(IMPLANTS_DIR, "*.mdc"))

        if not implant_files:
            logger.warning(f"No implant files found in {IMPLANTS_DIR}")
            return

        documents = []
        metadatas = []
        ids = []

        for file_path in implant_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Parse frontmatter
                frontmatter = {}
                body = content

                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        try:
                            frontmatter = yaml.safe_load(parts[1])
                            body = parts[2].strip()
                        except Exception as e:
                            logger.error(f"Failed to parse frontmatter for {file_path}: {e}")

                # Prepare for indexing
                description = frontmatter.get("description", "")
                full_text = f"{description}\n\n{body}"

                filename = os.path.basename(file_path)

                documents.append(full_text)
                metadatas.append({
                    "filename": filename,
                    "description": description,
                    "path": file_path,
                    "body": body  # Store clean body for injection
                })
                ids.append(filename)

                logger.info(f"Indexed implant: {filename}")

            except Exception as e:
                logger.error(f"Error processing implant file {file_path}: {e}")

        if documents:
            self.collection.upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Successfully indexed {len(documents)} implants.")

    @observe(name="retrieve_implants")
    def retrieve(self, query: str, n_results: int = 3, context: Dict[str, Any] = None, role: Optional[str] = None, agent_context: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves relevant implants for a given query.
        """
        if self.collection.count() == 0:
            return []

        # Handle legacy agent_context param (treat as role)
        if agent_context and not role:
            role = agent_context

        search_parts = [f"Query: {query}"]

        if role:
            search_parts.append(f"Role: {role}")

        if context:
            history_text = context.get("history_text", "")
            if history_text:
                # Truncate history to avoid too long query
                search_parts.append(f"Context: {history_text[-300:]}")

        search_query = "\n".join(search_parts)
        logger.info(f"Retrieving implants with query: {search_query}")

        results = self.collection.query(
            query_texts=[search_query],
            n_results=n_results
        )

        implants = []

        if results['ids'] and results['distances']:
            for i, distance in enumerate(results['distances'][0]):
                if distance < RELEVANCE_THRESHOLD:
                    meta = results['metadatas'][0][i] or {}
                    # Prefer body from metadata (clean injection), fallback to document
                    content = meta.get('body', results['documents'][0][i])

                    implants.append({
                        "filename": results['ids'][0][i],
                        "content": content,
                        "metadata": meta,
                        "distance": distance
                    })

        return implants

    def format_implants_for_prompt(self, implants: List[Dict[str, Any]]) -> str:
        """
        Formats retrieved implants into a markdown string for the system prompt.
        """
        if not implants:
            return ""

        formatted = "## Dynamic Implants (Contextually Loaded)\n"
        formatted += "The following cognitive implants have been loaded to augment reasoning:\n\n"

        for implant in implants:
            meta = implant.get("metadata", {})
            desc = meta.get("description", "No description")
            content = implant.get("content", "")

            formatted += f"### Implant: {meta.get('filename')}\n"
            formatted += f"**Description**: {desc}\n"
            formatted += f"{content}\n\n"

        return formatted
