from sqlalchemy import text

from app.database.session import SessionLocal

from app.ai.vectorstore.chroma_service import ChromaService

from app.ai.llm.groq_client import get_llm


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
            vectorstore = ChromaService()

            vectorstore.similarity_search(
                "health",
                k=1,
            )

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

        database = self.check_database()

        vectorstore = self.check_vectorstore()

        llm = self.check_llm()

        healthy = all(
            [
                database,
                vectorstore,
                llm,
            ]
        )

        return {
            "status": "healthy" if healthy else "unhealthy",
            "database": database,
            "vectorstore": vectorstore,
            "llm": llm,
        }
