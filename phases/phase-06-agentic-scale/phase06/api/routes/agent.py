from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from phase02.shared.llm_gemini import GeminiProvider
from phase06.agent.orchestrator import AgentOrchestrator
from phase06.api.dependencies import require_api_key
from phase06.api.schemas import AgentCitation, AgentQueryRequest, AgentQueryResponse
from phase06.database.repositories import AgentQueryRepository
from phase06.database.session import get_db_session
from phase06.rag.cache import QueryCache
from phase06.shared.config import settings

router = APIRouter(prefix="/api/v1", tags=["agent"])
_cache = QueryCache(prefix="agent")


def get_session():
    with get_db_session() as session:
        yield session


@router.post("/agent/query", response_model=AgentQueryResponse, dependencies=[Depends(require_api_key)])
def agent_query(request: AgentQueryRequest, session: Session = Depends(get_session)) -> AgentQueryResponse:
    cache_key = {"question": request.question, "debug": request.debug}
    if request.use_cache:
        cached = _cache.get("agent_query", cache_key)
        if cached:
            return AgentQueryResponse(**cached)

    try:
        llm = GeminiProvider(model_name=settings.gemini_model_rag) if settings.gemini_api_key else None
        orchestrator = AgentOrchestrator(session, llm)
        result = orchestrator.run(request.question, debug=request.debug)
        AgentQueryRepository(session).log(request.question, result, include_trace=request.debug)
        session.commit()

        payload = result.to_dict(include_trace=request.debug)
        citations = [AgentCitation(**c) if isinstance(c, dict) else AgentCitation(quote=str(c)) for c in payload["citations"]]
        response = AgentQueryResponse(
            answer=payload["answer"],
            citations=citations,
            confidence=payload["confidence"],
            steps=payload["steps"],
            took_ms=payload["took_ms"],
            tool_trace=payload.get("tool_trace"),
        )
        if request.use_cache:
            _cache.set("agent_query", cache_key, response.model_dump())
        return response
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Agent unavailable: {exc}") from exc
