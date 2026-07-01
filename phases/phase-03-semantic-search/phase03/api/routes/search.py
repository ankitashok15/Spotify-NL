from fastapi import APIRouter, HTTPException

from phase03.search.schemas import SearchRequest, SearchResponse
from phase03.search.semantic_search import SemanticSearchService

router = APIRouter(prefix="/api/v1", tags=["search"])

_search_service: SemanticSearchService | None = None


def get_search_service() -> SemanticSearchService:
    global _search_service
    if _search_service is None:
        _search_service = SemanticSearchService()
    return _search_service


@router.post("/search", response_model=SearchResponse)
def search_reviews(request: SearchRequest) -> SearchResponse:
    try:
        service = get_search_service()
        return service.search(
            request.query,
            filters=request.filters,
            top_k=request.top_k,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Search unavailable: {exc}") from exc
