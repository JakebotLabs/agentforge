"""Persistent memory component."""

from pathlib import Path
from typing import Any, Dict, Optional


class MemoryComponent:
    """Manages the persistent memory system (ChromaDB + NetworkX)."""
    
    name: str = "persistent-memory"
    
    def __init__(self, path: Path):
        self.path = path
        self.chroma_path = path / "chroma_db"
        self.graph_path = path / "knowledge_graph.json"
    
    def is_installed(self) -> bool:
        """Check if memory system is installed."""
        return self.path.exists() and self.chroma_path.exists()
    
    def get_status(self) -> Dict[str, Any]:
        """Get memory system status."""
        status = {
            "installed": self.is_installed(),
            "path": str(self.path),
            "chroma_exists": self.chroma_path.exists(),
            "graph_exists": self.graph_path.exists(),
        }
        
        if self.chroma_path.exists():
            try:
                import chromadb
                client = chromadb.PersistentClient(path=str(self.chroma_path))
                collections = client.list_collections()
                status["collections"] = len(collections)
                status["total_chunks"] = sum(c.count() for c in collections)
            except Exception as e:
                status["error"] = str(e)
        
        return status
    
    def search(self, query: str, n_results: int = 5) -> list:
        """Search the memory system."""
        if not self.is_installed():
            return []
        
        try:
            import chromadb
            client = chromadb.PersistentClient(path=str(self.chroma_path))
            collections = client.list_collections()
            if not collections:
                return []
            
            # Search the first collection (usually 'memory')
            collection = collections[0]
            results = collection.query(query_texts=[query], n_results=n_results)
            return results.get("documents", [[]])[0]
        except Exception:
            return []
