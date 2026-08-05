from app.services.retrieval_debug_service import (
    RetrievalDebugService,
)

service = RetrievalDebugService()

response = service.search(
    "Spring Boot",
)

print(response.model_dump())
