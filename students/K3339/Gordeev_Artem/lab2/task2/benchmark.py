import asyncio
from scrape_threading import run_threading
from scrape_multiprocessing import run_multiprocessing
from scrape_async import run_async
from scrape_async_db import run_async_db
from models import init_db

def main():
    urls = [
        "https://www.python.org",
        "https://www.github.com",
        "https://www.stackoverflow.com",
        "https://www.google.com",
        "https://www.reddit.com",
        "https://www.medium.com",
        "https://www.digitalocean.com"
    ]
    
    print("Инициализация базы данных...")
    init_db()
    
    print(f"Запуск бенчмарка задачи 2 (Парсинг {len(urls)} URL)...\n")
    
    print("Запуск через потоки...")
    time_t = run_threading(urls)
    print(f"Время: {time_t:.4f}сек\n")
    
    print("Запуск через процессы...")
    time_m = run_multiprocessing(urls)
    print(f"Время: {time_m:.4f}сек\n")
    
    print("Запуск через асинхронность (Sync DB)...")
    time_a = asyncio.run(run_async(urls))
    print(f"Время: {time_a:.4f}сек\n")

    print("Запуск через асинхронность (Async DB)...")
    time_adb = asyncio.run(run_async_db(urls))
    print(f"Время: {time_adb:.4f}сек\n")
    
    print("-" * 55)
    print(f"{'Метод':<30} | {'Время (сек)':<15}")
    print("-" * 55)
    print(f"{'Потоки':<30} | {time_t:<15.4f}")
    print(f"{'Процессы':<30} | {time_m:<15.4f}")
    print(f"{'Асинхронность (Sync DB)':<30} | {time_a:<15.4f}")
    print(f"{'Асинхронность (Async DB)':<30} | {time_adb:<15.4f}")
    print("-" * 55)

if __name__ == "__main__":
    main()
