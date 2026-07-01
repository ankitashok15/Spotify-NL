from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from phase04.api.schemas import QueryRequest, QueryResponse
from phase04.database.repositories import QueryLogRepository
from phase04.database.session import get_db_session
from phase04.rag.pipeline import RAGPipeline

router = APIRouter(prefix="/api/v1", tags=["rag"])


def get_session():
    with get_db_session() as session:
        yield session


@router.post("/query", response_model=QueryResponse)
def query_reviews(request: QueryRequest, session: Session = Depends(get_session)) -> QueryResponse:
    try:
        pipeline = RAGPipeline(session)
        result = pipeline.query(
            request.question,
            filters=request.filters,
            skip_llm_router=request.skip_llm_router,
        )
        QueryLogRepository(session).log(
            request.question,
            result,
            filters=request.filters.model_dump(exclude_none=True) if request.filters else None,
        )
        session.commit()
        return QueryResponse(**result.to_dict())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"RAG unavailable: {exc}") from exc
