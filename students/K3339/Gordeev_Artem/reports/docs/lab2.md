# Лабораторная работа 2. Потоки. Процессы. Асинхронность.

**Студент:** Гордеев Артём  
**Группа:** K3339  
**Тема:** Изучение многопоточности, многопроцессорности и асинхронности в Python.

## Цель работы

Понять отличия между потоками и процессами, изучить работу Global Interpreter Lock и понять, как работает асинхронность в Python. Научиться выбирать подходящий инструмент для решения CPU-bound и I/O-bound задач.

---

## Задача 1. Параллельное вычисление суммы

Задача: Написать три программы для вычисления суммы чисел от 1 до 10^8, используя подходы `threading`, `multiprocessing` и `asyncio`.

### Реализация

#### Threading (Многопоточность)
Используется модуль `threading`. Диапазон чисел делится на равные части между потоками.

```python
def calculate_sum(start, end, result, index):
    total = 0
    for i in range(start, end + 1):
        total += i
    result[index] = total

def run_threading(n, num_threads=4):
    threads = []
    results = [0] * num_threads
    step = n // num_threads
    for i in range(num_threads):
        start = i * step + 1
        end = (i + 1) * step if i != num_threads - 1 else n
        thread = threading.Thread(target=calculate_sum, args=(start, end, results, i))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    return sum(results)
```

#### Multiprocessing (Многопроцессорность)
Используется модуль `multiprocessing.Pool`. Расчеты распределяются по ядрам процессора.

```python
def calculate_sum(range_tuple):
    start, end = range_tuple
    total = 0
    for i in range(start, end + 1):
        total += i
    return total

def run_multiprocessing(n, num_processes=4):
    step = n // num_processes
    ranges = [(i * step + 1, (i + 1) * step if i != num_processes - 1 else n) for i in range(num_processes)]
    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.map(calculate_sum, ranges)
    return sum(results)
```

#### AsyncIO (Асинхронность)
Используется `asyncio.gather`. Задача выполняется конкурентно в одном потоке.

```python
async def calculate_sum(start, end):
    total = 0
    for i in range(start, end + 1):
        total += i
        if i % 1_000_000 == 0:
            await asyncio.sleep(0) # Уступаем управление Event Loop
    return total
```

### Сравнение времени выполнения (CPU-bound)

| Подход | Время (сек) |
|---|---|
| **Multiprocessing** | **0.5985** |
| **Threading** | 1.8739 |
| **AsyncIO** | 3.1257 |

**Вывод:** В задачах на вычисления (CPU-bound) лучшим выбором является Multiprocessing, так как он позволяет использовать несколько ядер процессора одновременно, обходя ограничения GIL. Threading работает медленнее из-за переключений контекста и GIL, а AsyncIO в данном случае дает только накладные расходы.

---

## Задача 2. Параллельный парсинг веб-страниц

Задача: Спарсить заголовки нескольких веб-страниц и сохранить их в базу данных PostgreSQL, используя три подхода.

### Модель данных
Для хранения результатов создана таблица `scraped_pages` в базе данных из первой лабораторной работы.

```python
class ScrapedPage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    url: str = Field()
    title: str = Field()
```

### Реализация

#### Threading
Используется `ThreadPoolExecutor` и библиотека `requests`. Потоки эффективны здесь, так как большую часть времени они «спят», ожидая ответа от сервера.

```python
def parse_and_save(url):
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'lxml')
    title = soup.title.string.strip() if soup.title else "No Title"
    with get_session() as session:
        page = ScrapedPage(url=url, title=title)
        session.add(page)
        session.commit()
```

#### Multiprocessing
Использование процессов для парсинга также возможно, однако каждый процесс требует ресурсов на запуск и отдельного подключения к БД.

```python
def parse_and_save(url):
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'lxml')
    title = soup.title.string.strip() if soup.title else "No Title"
    with get_session() as session:
        page = ScrapedPage(url=url, title=title)
        session.add(page)
        session.commit()

def run_multiprocessing(urls):
    with multiprocessing.Pool(processes=4) as pool:
        pool.map(parse_and_save, urls)
```

#### AsyncIO
Используется `aiohttp` для асинхронных HTTP-запросов. Это самый современный и легкий способ обработки множества сетевых соединений.

```python
async def parse_and_save(session, url):
    async with session.get(url) as response:
        html = await response.text()
        soup = BeautifulSoup(html, 'lxml')
        title = soup.title.string.strip() if soup.title else "No Title"
        with get_session() as db_session:
            page = ScrapedPage(url=url, title=title)
            db_session.add(page)
            db_session.commit()
```

### Сравнение времени выполнения (I/O-bound)

| Подход | Время (сек) |
|---|---|
| **AsyncIO** | **0.7399** |
| **Multiprocessing** | 1.2850 |
| **Threading** | 1.3236 |

**Вывод:** В задачах ввода-вывода (I/O-bound), таких как сетевые запросы, наиболее эффективным оказался AsyncIO. Он потребляет меньше ресурсов, чем процессы или потоки, и обеспечивает высокую производительность за счет неблокирующего ожидания.

## Влияние Global Interpreter Lock (GIL)

GIL - это механизм, который гарантирует, что в любой момент времени только один поток может выполнять байт-код Python. Это необходимо для обеспечения потокобезопасности при работе с памятью (управление ссылками).

### Как GIL проявил себя в работе:

**В задаче 1 (CPU-bound):**

   - **Threading** показал результат в 3 раза хуже, чем Multiprocessing. Это произошло потому, что потоки постоянно боролись за владение GIL. Несмотря на наличие 4-х потоков, вычисления велись фактически в один поток, но с дополнительными затратами на переключение контекста.
   - **Multiprocessing** успешно обошел это ограничение, так как каждый процесс имеет свой собственный интерпретатор и свой собственный GIL. Это позволило выполнять вычисления параллельно на разных ядрах CPU.

**В задаче 2 (I/O-bound):**

   - В этой задаче влияние GIL было минимальным. Когда поток вызывает `requests.get()`, он переходит в режим ожидания ответа от сети. В этот момент Python **освобождает GIL**, позволяя другим потокам начать работу. Именно поэтому `threading` в задачах ввода-вывода работает почти так же быстро, как и `multiprocessing`.

---

## Выбор инструмента для CPU-bound и I/O-bound задач

В ходе выполнения работы были выявлены четкие критерии выбора инструментов:

### 1. CPU-bound
**Что это:** Математические расчеты, обработка изображений, архивация, работа с Big Data.
**Выбор:** `multiprocessing`.
**Почему:** Только процессы позволяют использовать несколько физических ядер процессора. Потоки в Python ограничены GIL и выполняются по очереди на одном ядре.

### 2. I/O-bound
**Что это:** Работа с БД, сетевые запросы (парсинг, API), чтение/запись файлов.
**Выбор:** `asyncio` (предпочтительно) или `threading`.
**Почему:** Большую часть времени программа ждет ответа от внешнего ресурса. Асинхронность позволяет Event Loop переключаться на другие задачи во время этого ожидания, не создавая тяжелые системные ресурсы (процессы/потоки).

---

## Итоговый вывод

1. **Multiprocessing** незаменим для тяжелых вычислений, так как задействует все ядра CPU.
2. **AsyncIO** является лучшим выбором для работы с сетью и микросервисами благодаря легковесности.
3. **Threading** остается универсальным средством для простых I/O задач, но уступает AsyncIO при большом количестве соединений.
