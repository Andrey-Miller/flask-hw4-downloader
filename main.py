import os
import time
import argparse
import asyncio
import aiohttp
import requests
import threading
from multiprocessing import Process


def_images = [
    'https://img.freepik.com/premium-photo/portrait-smiling-young-man-standing-outdoors_1048944-29813224.jpg',
    'https://img.freepik.com/free-photo/medium-shot-latin-people-training-outdoors_23-2151039433.jpg',
    'https://img.freepik.com/premium-photo/full-length-woman-exercising-field_1048944-30351094.jpg',
    'https://img.freepik.com/free-photo/water-polo-player-pool-with-swimming-equipment_23-2150893950.jpg',
    'https://img.freepik.com/premium-photo/full-length-man-playing-with-arms-raised_1048944-29793390.jpg'
        ]


def download(url, folder, start_time):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            filename = os.path.join(folder, os.path.basename(url))
            with open(filename, 'wb') as file:
                for chunk in response.iter_content():
                    file.write(chunk)
            print(f"Загружено: {url} -> {filename}, Время загрузки: {time.time() - start_time:.2f}")
        else:
            print(f"Ошибка при загрузке {url}")
    except Exception as e:
        print(f"Ошибка: {e}")


def threading_download(urls, folder):
    print("Многопоточный подход")
    start_time = time.time()
    os.makedirs(folder, exist_ok=True)
    threads = []
    for url in urls:
        thread = threading.Thread(target=download, args=(url, folder, start_time))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    end_time = time.time()
    total_time = end_time - start_time
    print(f"\nВремя выполнения: {total_time}\n")


def multiprocessing_download(urls, folder):
    print("Многопроцессорный подход")
    start_time = time.time()
    os.makedirs(folder, exist_ok=True)
    processes = []
    for url in urls:
        process = Process(target=download, args=(url, folder, start_time))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    end_time = time.time()
    total_time = end_time - start_time
    print(f"\nВремя выполнения: {total_time}\n")


async def async_download(urls, folder):
    print("Асинхронный подход")
    start_time = time.time()
    os.makedirs(folder, exist_ok=True)

    async with aiohttp.ClientSession() as session:
        tasks = [async_process(session, url, folder, start_time) for url in urls]
        await asyncio.gather(*tasks)

    end_time = time.time()
    total_time = end_time - start_time
    print(f"\nВремя выполнения: {total_time}\n")


async def async_process(session, url, folder, start_time):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                filename = os.path.join(folder, os.path.basename(url))
                with open(filename, 'wb') as file:
                    while True:
                        chunk = await response.content.read()
                        if not chunk:
                            break
                        file.write(chunk)
                print(f"Загружено: {url} -> {filename}, Время загрузки: {time.time() - start_time:.2f}")
            else:
                print(f"Ошибка при загрузке {url}")
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Загрузка изображений:')
    parser.add_argument('urls', nargs='?', default=def_images)
    args = parser.parse_args()

    threading_folder = "threading_downloaded"
    threading_download(args.urls, threading_folder)

    multiprocessing_folder = "multiprocessing_downloaded"
    multiprocessing_download(args.urls, multiprocessing_folder)

    async_folder = "async_downloaded"
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_download(args.urls, async_folder))
