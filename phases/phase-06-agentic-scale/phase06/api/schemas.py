from pydantic import BaseModel, Field


class AgentQueryRequest(BaseModel):
    question: str = Field(min_length=3)
    debug: bool = False
    use_cache: bool = True


class AgentCitation(BaseModel):
    review_id: str | None = None
    quote: str | None = None
    rating: int | None = None


class AgentQueryResponse(BaseModel):
    answer: str
    citations: list[AgentCitation] = Field(default_factory=list)
    confidence: float
    steps: int
    took_ms: float
    tool_trace: list[dict] | None = None
