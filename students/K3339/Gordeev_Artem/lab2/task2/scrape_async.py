import aiohttp
import asyncio
from bs4 import BeautifulSoup
from models import ScrapedPage, get_session
import time

async def parse_and_save(session, url):
    try:
        async with session.get(url, timeout=10) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'lxml')
            title = soup.title.string if soup.title else "No Title"
            title = title.strip()
            
            # Сохранение в БД (блокирующая операция, выполняем в executor или просто так для лабы)
            with get_session() as db_session:
                page = ScrapedPage(url=url, title=title)
                db_session.add(page)
                db_session.commit()
                
            print(f"[Async] Спарсено: {url} -> {title}")
            return True
    except Exception as e:
        print(f"[Async] Ошибка {url}: {e}")
        return False

async def run_async(urls):
    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [parse_and_save(session, url) for url in urls]
        await asyncio.gather(*tasks)
    end_time = time.time()
    return end_time - start_time

if __name__ == "__main__":
    test_urls = ["https://www.python.org", "https://www.google.com"]
    duration = asyncio.run(run_async(test_urls))
    print(f"Async: Время парсинга: {duration:.4f}сек")
