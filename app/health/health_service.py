from sqlalchemy import text

from app.database.session import SessionLocal
from app.ai.llm.groq_client import get_llm
from app.ai.retrieval.dependencies import get_chroma_service


class HealthService:
    def check_database(self):
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
        finally:
            db.close()

    def check_vectorstore(self):
        try:
            vectorstore = get_chroma_service()
            vectorstore.similarity_search("health", k=1)
            return True
        except Exception:
            return False

    def check_llm(self):
        try:
            get_llm()
            return True
        except Exception:
            return False

    def status(self):
        return {
            "status": "healthy",
            "database": self.check_database(),
            "vectorstore": self.check_vectorstore(),
            "llm": self.check_llm(),
        }
