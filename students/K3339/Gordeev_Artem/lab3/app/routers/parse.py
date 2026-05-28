import os
import httpx
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from celery.result import AsyncResult
from app.celery_worker import celery_app
from app.celery_worker import parse_url_task
from pydantic import BaseModel

router = APIRouter(prefix="/parse", tags=["Parsing"])

class ParseRequest(BaseModel):
    url: str

PARSER_API_URL = os.getenv("PARSER_API_URL", "http://parser_api:8001/parse_sync")

@router.post("/http")
async def parse_via_http(request: ParseRequest):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(PARSER_API_URL, json={"url": request.url}, timeout=15.0)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            try:
                error_detail = e.response.json().get("detail", e.response.text)
            except Exception:
                pass
            raise HTTPException(status_code=e.response.status_code, detail=f"Parser API error: {error_detail}")

@router.post("/celery")
async def parse_via_celery(request: ParseRequest):
    task = parse_url_task.delay(request.url)
    return {"message": "Parsing task submitted", "task_id": task.id}

@router.get("/celery/{task_id}")
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    result = {
        "task_id": task_id,
        "status": task_result.status,
    }
    if task_result.status == "SUCCESS":
        result["result"] = task_result.result
    elif task_result.status == "FAILURE":
        result["error"] = str(task_result.result)
    return result
