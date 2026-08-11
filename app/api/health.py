from fastapi import APIRouter

router = APIRouter(
    tags=["Health"],
)


@router.get("/health", include_in_schema=True)
def health():
    return {"ok": True}
