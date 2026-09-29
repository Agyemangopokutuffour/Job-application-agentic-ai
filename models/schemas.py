from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass


class HealthResponse(schemas.BaseModel):
    status: str


class FetchJobRequest(schemas.BaseModel):
    url: str = ""
    manual_text: str = ""


class FetchJobResponse(schemas.BaseModel):
    url: str
    content: str


class ParseResumeResponse(schemas.BaseModel):
    filename: str
    content: str


class AnalyzeRequest(schemas.BaseModel):
    job_text: str
    resume_text: str


class AnalyzeResponse(schemas.BaseModel):
    match_level: str
    reasoning: str
    cover_letter: str | None = None
    rewritten_bullets: list[str] | None = None
    gap_advice: str | None = None
