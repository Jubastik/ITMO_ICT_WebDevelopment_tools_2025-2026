import aiohttp
import asyncio
from bs4 import BeautifulSoup
from models import ScrapedPage, AsyncSessionLocal
import time

async def parse_and_save(session, url):
    try:
        async with session.get(url, timeout=10) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'lxml')
            title = soup.title.string if soup.title else "No Title"
            title = title.strip()
            
            async with AsyncSessionLocal() as db_session:
                page = ScrapedPage(url=url, title=title)
                db_session.add(page)
                await db_session.commit()
                
            print(f"[AsyncDB] Спарсено: {url} -> {title}")
            return True
    except Exception as e:
        print(f"[AsyncDB] Ошибка {url}: {e}")
        return False

async def run_async_db(urls):
    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [parse_and_save(session, url) for url in urls]
        await asyncio.gather(*tasks)
    end_time = time.time()
    return end_time - start_time

if __name__ == "__main__":
    test_urls = ["https://www.python.org", "https://www.google.com"]
    duration = asyncio.run(run_async_db(test_urls))
    print(f"Async DB Scrape Time: {duration:.4f}сек")
