import logging
import os
import glob
import yaml
import chromadb
from chromadb.utils import embedding_functions
from langfuse import observe
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Configuration
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "../../chroma_db")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
SKILLS_DIR = os.path.join(os.path.dirname(__file__), "../../.cursor/skills")
RELEVANCE_THRESHOLD = 0.45  # Cosine distance threshold (lower is better)

class SkillRetriever:
    def __init__(self):
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

        # Use Sentence Transformers for embeddings
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )

        self.collection = self.chroma_client.get_or_create_collection(
            name="skills_store",
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )

        # Determine if we need to index (simple check: if empty)
        # In a production system, we'd check for file changes.
        if self.collection.count() == 0:
            logger.info("Skill store is empty. Indexing skills...")
            self.index_skills()

    def index_skills(self):
        """
        Reads all .mdc files in SKILLS_DIR and indexes them.
        """
        skill_files = glob.glob(os.path.join(SKILLS_DIR, "*.mdc"))

        if not skill_files:
            logger.warning(f"No skill files found in {SKILLS_DIR}")
            return

        documents = []
        metadatas = []
        ids = []

        for file_path in skill_files:
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
                # We index the full content (description + body) for better retrieval
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

                logger.info(f"Indexed skill: {filename}")

            except Exception as e:
                logger.error(f"Error processing skill file {file_path}: {e}")

        if documents:
            self.collection.upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Successfully indexed {len(documents)} skills.")

    @observe(name="retrieve_skills")
    def retrieve(self, query: str, n_results: int = 2, preferred_skills: List[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves relevant skills for a given query.
        If preferred_skills are provided, loads them instead of vector search.
        """
        if self.collection.count() == 0:
            return []

        skills = []

        if preferred_skills:
            # Normalize filenames (ensure .mdc extension)
            target_ids = []
            for ps in preferred_skills:
                if not ps.endswith(".mdc"):
                    target_ids.append(f"{ps}.mdc")
                else:
                    target_ids.append(ps)

            try:
                # Use collection.get to fetch specific IDs
                results = self.collection.get(ids=target_ids)
                if results['ids']:
                    for i, id in enumerate(results['ids']):
                        # Prefer body from metadata (clean injection), fallback to document
                        meta = results['metadatas'][i] or {}
                        content = meta.get('body', results['documents'][i])
                        
                        skills.append({
                            "filename": id,
                            "content": content,
                            "metadata": meta,
                            "distance": 0.0  # Exact match
                        })
                logger.info(f"Loaded {len(skills)} preferred skills: {target_ids}")
                return skills
            except Exception as e:
                logger.warning(f"Failed to retrieve preferred skills {target_ids}: {e}")
                # Fallback to vector search handled below if skills is empty
                pass

        if skills: # If we found some but not all, or if we want to return what we found
             return skills

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )

        skills = []

        if results['ids'] and results['distances']:
            for i, distance in enumerate(results['distances'][0]):
                if distance < RELEVANCE_THRESHOLD:
                    meta = results['metadatas'][0][i] or {}
                    # Prefer body from metadata (clean injection), fallback to document
                    content = meta.get('body', results['documents'][0][i])
                    
                    skills.append({
                        "filename": results['ids'][0][i],
                        "content": content,
                        "metadata": meta,
                        "distance": distance
                    })

        return skills

    def format_skills_for_prompt(self, skills: List[Dict[str, Any]]) -> str:
        """
        Formats retrieved skills into a markdown string for the system prompt.
        """
        if not skills:
            return ""

        formatted = "## Dynamic Skills (Contextually Loaded)\n"
        formatted += "The following specialized skills have been loaded to help with the request:\n\n"

        for skill in skills:
            meta = skill.get("metadata", {})
            desc = meta.get("description", "No description")
            content = skill.get("content", "")
            # We clean up the content slightly if it contains the full text we indexed
            # Ideally we might want to just inject the 'body' part, but 'content' in search result is what we indexed.
            # Let's rely on the indexed document being readable.

            formatted += f"### Skill: {meta.get('filename')}\n"
            formatted += f"**Description**: {desc}\n"
            formatted += f"{content}\n\n"

        return formatted
