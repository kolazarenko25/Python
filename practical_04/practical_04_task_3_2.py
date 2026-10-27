# practical_04_task_3_2.py

"""Producer-Consumer з queue.Queue та демонстрація дедлоку."""

import threading
import queue
import time
import random
from collections import Counter


class Task:
    """Завдання для обробки."""

    def __init__(self, task_id: int, data: str, priority: int = 0):
        self.task_id = task_id
        self.data = data
        self.priority = priority
        self.created_at = time.time()

    def __repr__(self):
        return f"Task(id={self.task_id}, data='{self.data}')"


class ProducerTracker:
    """Рахує, скільки виробників ще не надіслали sentinel (None).

    Кожен виробник наприкінці кладе в чергу свій None. Якби споживач
    завершувався після першого ж None, він міг би піти, поки інший
    виробник ще працює (і тоді той завис би на повній черзі). Тому
    споживачі завершуються лише після None від УСІХ виробників.
    """

    def __init__(self, num_producers: int):
        self._remaining = num_producers
        self._lock = threading.Lock()

    def producer_finished(self) -> bool:
        """Фіксує отриманий sentinel; True, якщо завершились усі виробники."""
        with self._lock:
            self._remaining -= 1
            return self._remaining <= 0


def producer(task_queue: queue.Queue, num_tasks: int,
             producer_id: int) -> None:
    """Виробник: генерує завдання та поміщає їх у чергу."""
    for i in range(num_tasks):
        task = Task(
            task_id=producer_id * 100 + i,
            data=f"Дані від виробника {producer_id}, пакет {i}",
            priority=random.randint(1, 5),
        )
        # put() блокується, якщо черга заповнена (maxsize) -- це і є
        # зворотний тиск: швидкий виробник чекає повільних споживачів
        started = time.perf_counter()
        task_queue.put(task)
        waited = time.perf_counter() - started

        message = (f"[Виробник-{producer_id}] Створено {task} "
                   f"(у черзі: {task_queue.qsize()})")
        if waited > 0.05:
            message += f"  <- черга була повна, чекав {waited:.2f} сек"
        print(message)
        time.sleep(random.uniform(0.1, 0.3))

    # Сигнал завершення для споживачів
    task_queue.put(None)
    print(f"[Виробник-{producer_id}] Завершив роботу, надіслано sentinel (None)")


def consumer(task_queue: queue.Queue, consumer_id: int,
             results: list, results_lock: threading.Lock,
             tracker: ProducerTracker) -> None:
    """Споживач: обробляє завдання з черги."""
    while True:
        try:
            # Тайм-аут захищає від вічного очікування, якщо виробників уже немає
            task = task_queue.get(timeout=2)
        except queue.Empty:
            print(f"  [Споживач-{consumer_id}] Черга порожня, завершення")
            break

        if task is None:
            task_queue.task_done()
            if tracker.producer_finished():
                # Усі виробники завершились: передаємо сигнал наступному
                # споживачу (інакше він чекав би до тайм-ауту) і виходимо
                task_queue.put(None)
                print(f"  [Споживач-{consumer_id}] Отримано sentinel "
                      f"від усіх виробників, завершення")
                break
            # Завершився лише один із виробників -- працюємо далі
            continue

        # Імітація обробки задачі
        started = time.perf_counter()
        time.sleep(random.uniform(0.5, 0.9))
        processing_time = time.perf_counter() - started

        # results -- спільний список, тому запис під захистом Lock
        with results_lock:
            results.append({
                "task_id": task.task_id,
                "consumer": consumer_id,
                "processing_time": processing_time,
                "latency": time.time() - task.created_at,
            })
        print(f"  [Споживач-{consumer_id}] Оброблено {task.task_id} "
              f"за {processing_time:.2f} сек")

        task_queue.task_done()


def producer_consumer_demo():
    """Демонстрація паттерну Producer-Consumer."""
    task_queue = queue.Queue(maxsize=5)
    results = []
    results_lock = threading.Lock()
    num_producers = 2
    num_consumers = 3
    tasks_per_producer = 8
    tracker = ProducerTracker(num_producers)

    producers = [
        threading.Thread(target=producer,
                         args=(task_queue, tasks_per_producer, pid),
                         name=f"Producer-{pid}")
        for pid in range(1, num_producers + 1)
    ]
    consumers = [
        threading.Thread(target=consumer,
                         args=(task_queue, cid, results, results_lock,
                               tracker),
                         name=f"Consumer-{cid}")
        for cid in range(1, num_consumers + 1)
    ]

    start = time.perf_counter()
    for t in consumers + producers:
        t.start()
    for t in producers + consumers:
        t.join()
    total_time = time.perf_counter() - start

    # Підсумки
    expected = num_producers * tasks_per_producer
    print(f"\nОброблено задач: {len(results)} з {expected}")
    if results:
        avg_proc = sum(r["processing_time"] for r in results) / len(results)
        avg_latency = sum(r["latency"] for r in results) / len(results)
        print(f"Середній час обробки задачі: {avg_proc:.2f} сек")
        print(f"Середній час від створення до завершення: "
              f"{avg_latency:.2f} сек")
    print(f"Загальний час: {total_time:.2f} сек")
    per_consumer = Counter(r["consumer"] for r in results)
    for cid in sorted(per_consumer):
        print(f"  Споживач-{cid}: {per_consumer[cid]} задач")


def deadlock_demo():
    """Демонстрація та виявлення потенційного дедлоку."""
    lock_a = threading.Lock()
    lock_b = threading.Lock()
    deadlock_detected = threading.Event()

    def worker_1():
        """Захоплює lock_a, потім lock_b."""
        lock_a.acquire()
        print("[Worker-1] Захопив Lock A")
        time.sleep(0.1)
        acquired = lock_b.acquire(timeout=2)
        if not acquired:
            print("[Worker-1] ДЕДЛОК: не вдалося захопити Lock B!")
            deadlock_detected.set()
            lock_a.release()
            return
        print("[Worker-1] Захопив Lock B")
        lock_b.release()
        lock_a.release()

    def worker_2():
        """Захоплює lock_b, потім lock_a -- зворотний порядок!"""
        lock_b.acquire()
        print("[Worker-2] Захопив Lock B")
        time.sleep(0.1)
        acquired = lock_a.acquire(timeout=2)
        if not acquired:
            print("[Worker-2] ДЕДЛОК: не вдалося захопити Lock A!")
            deadlock_detected.set()
            lock_b.release()
            return
        print("[Worker-2] Захопив Lock A")
        lock_a.release()
        lock_b.release()

    safe_done = []  # list.append потокобезпечний у CPython

    def safe_worker_1():
        """Безпечна версія: завжди захоплює A -> B."""
        with lock_a:
            print("[Safe-1] Захопив Lock A")
            time.sleep(0.1)
            with lock_b:
                print("[Safe-1] Захопив Lock B")
                safe_done.append("Safe-1")

    def safe_worker_2():
        """Безпечна версія: той самий порядок A -> B."""
        with lock_a:
            print("[Safe-2] Захопив Lock A")
            time.sleep(0.1)
            with lock_b:
                print("[Safe-2] Захопив Lock B")
                safe_done.append("Safe-2")

    # === Демонстрація дедлоку ===
    print("=== Спроба з потенційним дедлоком ===")
    started = time.perf_counter()
    t1 = threading.Thread(target=worker_1)
    t2 = threading.Thread(target=worker_2)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    elapsed = time.perf_counter() - started

    if deadlock_detected.is_set():
        print(f">>> Дедлок виявлено через {elapsed:.1f} сек! "
              f"Використовуємо timeout для запобігання зависанню.\n")
    else:
        print(">>> Дедлок не виник цього разу (залежить від планувальника).\n")

    # === Безпечна версія ===
    print("=== Безпечна версія (однаковий порядок замків) ===")
    s1 = threading.Thread(target=safe_worker_1)
    s2 = threading.Thread(target=safe_worker_2)
    started = time.perf_counter()
    s1.start()
    s2.start()
    # join з тайм-аутом: якщо потік завис, is_alive() залишиться True
    s1.join(timeout=5)
    s2.join(timeout=5)
    elapsed = time.perf_counter() - started

    if s1.is_alive() or s2.is_alive():
        print(">>> Потоки зависли -- дедлок!")
    else:
        print(f">>> Дедлоку не виникло: обидва потоки завершились "
              f"за {elapsed:.2f} сек ({', '.join(sorted(safe_done))}).")


def main():
    print("=" * 60)
    print("=== Паттерн Producer-Consumer ===")
    print("=" * 60)
    producer_consumer_demo()

    print(f"\n{'=' * 60}")
    print("=== Демонстрація дедлоку ===")
    print("=" * 60)
    deadlock_demo()


if __name__ == "__main__":
    main()
