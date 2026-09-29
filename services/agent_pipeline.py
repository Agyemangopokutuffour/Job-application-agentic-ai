import json
import os

import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = """You are a job application analysis assistant. Follow these steps in order:

1. Extract structured job requirements from the job description as JSON with keys: title, required_skills (list), nice_to_have_skills (list), seniority (string).

2. Extract structured resume data from the resume as JSON with keys: name, skills (list), projects (list), experience_summary (string).

3. Compare the two and decide a match_level: "strong" (most required skills present, seniority matches), "partial" (some key skills present but gaps exist), or "weak" (few relevant skills, major mismatch). Provide a brief reasoning.

4. If match_level is "strong" or "partial", generate:
   - cover_letter: a tailored cover letter (2-3 paragraphs) grounded in the actual resume content that highlights relevant experience for the job.
   - rewritten_bullets: 3-5 rewritten resume bullet points that use keywords from the job description while staying true to the candidate's actual experience. Return as a list of strings.
   - gap_advice: null.
   
   If match_level is "weak", generate:
   - cover_letter: null
   - rewritten_bullets: null
   - gap_advice: an honest explanation of the skill/experience gap and what skills to build first before applying.

Return ONLY valid JSON with these top-level keys: match_level, reasoning, cover_letter, rewritten_bullets, gap_advice."""


def _call_llm(system: str, user: str) -> str:
    response = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def analyze_application(job_text: str, resume_text: str) -> dict:
    raw = _call_llm(
        SYSTEM_PROMPT,
        f"--- JOB DESCRIPTION ---\n{job_text}\n\n--- RESUME ---\n{resume_text}",
    )

    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
        cleaned = cleaned.rsplit("```", 1)[0]

    result = json.loads(cleaned.strip())

    for key in ("match_level", "reasoning", "cover_letter", "rewritten_bullets", "gap_advice"):
        result.setdefault(key, None)

    return result
