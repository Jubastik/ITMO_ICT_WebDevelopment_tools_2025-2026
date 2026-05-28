from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.parser import async_parse_and_save

app = FastAPI(title="Parser API", description="Внутренний сервис для синхронного вызова парсера")

class ParseRequest(BaseModel):
    url: str

@app.post("/parse_sync")
async def parse_sync(request: ParseRequest):
    result = await async_parse_and_save(request.url)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["detail"])
    return result
