from datetime import datetime

from pydantic import BaseModel, Field

from phase03.search.schemas import SearchFilters


class QueryRequest(BaseModel):
    question: str = Field(min_length=1)
    filters: SearchFilters | None = None
    skip_llm_router: bool = False


class CitationItem(BaseModel):
    id: int
    document_id: str
    external_review_id: str | None = None
    rating: int | None = None
    thumbs_up: int | None = None
    device_type: str | None = None
    subscription_type: str | None = None
    primary_issue: str | None = None
    excerpt: str | None = None
    review_created_at: datetime | str | None = None


class QueryResponse(BaseModel):
    answer: str
    citations: list[CitationItem]
    confidence: float
    reviews_considered: int
    reviews_cited: int
    intent: str
    search_query: str
    took_ms: float
    citation_valid: bool
    warnings: list[str] = Field(default_factory=list)
