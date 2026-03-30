import chromadb
from chromadb.utils import embedding_functions
import uuid
from datetime import datetime

class Memory:
    def __init__(self, path: str = "./memory_store"):
        self.client = chromadb.PersistentClient(path=path)
        self.ef = embedding_functions.DefaultEmbeddingFunction()

        # Two separate collections
        self.facts = self.client.get_or_create_collection(
            name="facts",
            embedding_function=self.ef
        )
        self.history = self.client.get_or_create_collection(
            name="history",
            embedding_function=self.ef
        )

    # ── Facts (persistent things about the user) ──────────────────────────

    def save_fact(self, fact: str) -> None:
        """Store a fact about the user e.g. 'User prefers dark mode'"""
        self.facts.add(
            documents=[fact],
            ids=[str(uuid.uuid4())],
            metadatas=[{"timestamp": datetime.now().isoformat()}]
        )
        print(f"  [Memory] Saved fact: {fact}")

    def search_facts(self, query: str, n: int = 3) -> list[str]:
        """Find relevant facts for a given query"""
        if self.facts.count() == 0:
            return []
        results = self.facts.query(query_texts=[query], n_results=min(n, self.facts.count()))
        return results["documents"][0] if results["documents"] else []

    def list_all_facts(self) -> list[str]:
        """Return every stored fact"""
        if self.facts.count() == 0:
            return []
        return self.facts.get()["documents"]

    def delete_fact(self, fact: str) -> bool:
        """Delete a fact by matching its content"""
        results = self.facts.query(query_texts=[fact], n_results=1)
        if not results["ids"][0]:
            return False
        self.facts.delete(ids=[results["ids"][0][0]])
        return True

    # ── Conversation history (long-term) ──────────────────────────────────

    def save_exchange(self, user_msg: str, assistant_msg: str) -> None:
        """Save a conversation turn for long-term recall"""
        doc = f"User: {user_msg}\nAssistant: {assistant_msg}"
        self.history.add(
            documents=[doc],
            ids=[str(uuid.uuid4())],
            metadatas=[{"timestamp": datetime.now().isoformat()}]
        )

    def search_history(self, query: str, n: int = 3) -> list[str]:
        """Find relevant past exchanges"""
        if self.history.count() == 0:
            return []
        results = self.history.query(query_texts=[query], n_results=min(n, self.history.count()))
        return results["documents"][0] if results["documents"] else []