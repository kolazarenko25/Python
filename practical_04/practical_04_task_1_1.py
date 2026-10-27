# practical_04_task_1_1.py

"""Створення та керування потоками в Python."""

import threading
import time

# Коефіцієнт імітації: скільки секунд триває "завантаження" 1 МБ
SECONDS_PER_MB = 0.4


def download_simulation(file_name: str, size_mb: float) -> dict:
    """Імітація завантаження файлу (I/O-bound задача).

    Args:
        file_name: назва файлу.
        size_mb: розмір файлу в мегабайтах.

    Returns:
        Словник з інформацією про завантажений файл.
    """
    thread_name = threading.current_thread().name
    print(f"[{thread_name}] Початок завантаження '{file_name}' ({size_mb} MB)...")
    # time.sleep() імітує очікування мережі: на цей час потік вивільняє GIL,
    # тому інші потоки можуть працювати паралельно
    time.sleep(size_mb * SECONDS_PER_MB)
    print(f"[{thread_name}] Готово: '{file_name}'")
    return {"file": file_name, "size": size_mb, "thread": thread_name}


class MonitorThread(threading.Thread):
    """Потік-монітор, що періодично виводить стан системи."""

    def __init__(self, interval: float = 1.0):
        # daemon=True: потік не заважатиме завершенню програми
        super().__init__(name="Monitor", daemon=True)
        self.interval = interval
        self.active_downloads = 0
        self._stop_event = threading.Event()
        self._counter_lock = threading.Lock()

    def download_started(self) -> None:
        """Збільшує лічильник активних завантажень (потокобезпечно)."""
        with self._counter_lock:
            self.active_downloads += 1

    def download_finished(self) -> None:
        """Зменшує лічильник активних завантажень (потокобезпечно)."""
        with self._counter_lock:
            self.active_downloads -= 1

    def run(self):
        """Виводить кількість активних потоків кожні `interval` секунд."""
        # Event.wait(timeout) чекає `interval` секунд і повертає True,
        # якщо подію встановлено (тобто потрібно зупинитися)
        while not self._stop_event.wait(self.interval):
            print(
                f"[{self.name}] Активних потоків: {threading.active_count()}, "
                f"завантажень у процесі: {self.active_downloads}"
            )
        print(f"[{self.name}] Зупинено")

    def stop(self):
        self._stop_event.set()


def download_worker(file_name: str, size_mb: float, results: list,
                    results_lock: threading.Lock,
                    monitor: MonitorThread) -> None:
    """Обгортка для потоку: виконує завантаження та зберігає результат.

    Thread не повертає значення з target, тому результат кладемо у
    спільний список (під захистом Lock).
    """
    monitor.download_started()
    try:
        info = download_simulation(file_name, size_mb)
        with results_lock:
            results.append(info)
    finally:
        monitor.download_finished()


def main():
    files = [
        ("data.csv", 2.5),
        ("report.pdf", 1.0),
        ("image.png", 0.5),
        ("archive.zip", 4.0),
        ("log.txt", 0.3),
    ]

    print(f"Головний потік: {threading.current_thread().name}")

    # Створюємо та запускаємо демон-потік монітора
    monitor = MonitorThread(interval=0.5)
    monitor.start()
    print(f"Монітор запущено (daemon={monitor.daemon}), "
          f"активних потоків: {threading.active_count()}\n")

    # === Паралельне виконання ===
    results: list = []
    results_lock = threading.Lock()

    # Окремий потік на кожен файл
    threads = [
        threading.Thread(
            target=download_worker,
            args=(name, size, results, results_lock, monitor),
            name=f"Downloader-{i}",
        )
        for i, (name, size) in enumerate(files, start=1)
    ]

    start = time.perf_counter()

    for t in threads:
        t.start()
    print(f"Запущено потоків завантаження: {len(threads)}, "
          f"усього активних потоків: {threading.active_count()}\n")

    for t in threads:
        t.join()

    elapsed = time.perf_counter() - start
    print(f"\nУсі файли завантажено за {elapsed:.2f} сек")

    print("\nРезультати завантаження:")
    for info in results:
        print(f"  {info['file']:<12} {info['size']:>4} MB  "
              f"потік: {info['thread']}")

    # === Послідовне виконання (для порівняння) ===
    print("\n--- Послідовне завантаження для порівняння ---")
    start = time.perf_counter()
    for name, size in files:
        download_simulation(name, size)
    seq_elapsed = time.perf_counter() - start

    print(f"\nПаралельно (потоки): {elapsed:.2f} сек")
    print(f"Послідовно:          {seq_elapsed:.2f} сек")
    print(f"Прискорення:         {seq_elapsed / elapsed:.2f}x")

    # Зупиняємо демон-потік через Event
    monitor.stop()
    monitor.join(timeout=1)


if __name__ == "__main__":
    main()
