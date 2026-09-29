from fastapi import APIRouter, Depends, HTTPException, UploadFile

from models.schemas import AnalyzeRequest, AnalyzeResponse, FetchJobRequest, FetchJobResponse, ParseResumeResponse
from models.user import User
from routes.auth import current_active_user
from services.agent_pipeline import analyze_application
from services.job_fetcher import fetch_job_post
from services.resume_parser import extract_text_from_pdf

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/fetch-job", response_model=FetchJobResponse)
def fetch_job(
    body: FetchJobRequest,
    user: User = Depends(current_active_user),
):
    if body.manual_text and body.manual_text.strip():
        return FetchJobResponse(url=body.url, content=body.manual_text)

    if not body.url:
        raise HTTPException(status_code=400, detail="Either 'url' or 'manual_text' is required")

    try:
        content = fetch_job_post(body.url)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if len(content) < 200:
        raise HTTPException(
            status_code=400,
            detail="Could not extract meaningful content from the URL (likely a JS-rendered page). "
                   "Please paste the job description manually using the 'manual_text' field instead.",
        )

    return FetchJobResponse(url=body.url, content=content)


@router.post("/parse-resume", response_model=ParseResumeResponse)
def parse_resume(
    file: UploadFile,
    user: User = Depends(current_active_user),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        content = extract_text_from_pdf(file.file.read())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if not content:
        raise HTTPException(status_code=400, detail="Could not extract any text from the PDF")

    return ParseResumeResponse(filename=file.filename, content=content)


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(
    body: AnalyzeRequest,
    user: User = Depends(current_active_user),
):
    if not body.job_text.strip():
        raise HTTPException(status_code=400, detail="job_text is required")
    if not body.resume_text.strip():
        raise HTTPException(status_code=400, detail="resume_text is required")

    try:
        result = analyze_application(body.job_text, body.resume_text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}")

    return AnalyzeResponse(**result)
