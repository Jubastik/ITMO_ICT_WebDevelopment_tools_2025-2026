import aiohttp
import asyncio
from bs4 import BeautifulSoup
from sqlmodel import Session
from app.database import engine
from app.models.scraped_page import ScrapedPage

async def async_parse_and_save(url: str) -> dict:
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=10) as response:
                response.raise_for_status()
                html = await response.text()
                soup = BeautifulSoup(html, 'lxml')
                title = soup.title.string if soup.title else "No Title"
                title = title.strip()
                
                with Session(engine) as db_session:
                    page = ScrapedPage(url=url, title=title)
                    db_session.add(page)
                    db_session.commit()
                    db_session.refresh(page)
                    
                return {"status": "success", "url": url, "title": title, "id": page.id}
    except Exception as e:
        return {"status": "error", "url": url, "detail": str(e)}

def sync_parse_and_save(url: str) -> dict:
    """Синхронная обертка для Celery."""
    return asyncio.run(async_parse_and_save(url))
