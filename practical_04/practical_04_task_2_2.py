# practical_04_task_2_2.py

"""Семафори та Event для управління конкурентним доступом."""

import threading
import time
import random


class ConnectionPool:
    """Пул з'єднань з обмеженням через Semaphore."""

    def __init__(self, max_connections: int = 3):
        self._semaphore = threading.Semaphore(max_connections)
        self._lock = threading.Lock()
        self.max_connections = max_connections
        self.active_connections = 0
        self.total_served = 0
        self.peak_connections = 0
        self.violations = 0  # скільки разів active перевищив max (має бути 0)

    def acquire_connection(self, client_name: str) -> None:
        """Отримання з'єднання (блокується, якщо пул вичерпано)."""
        print(f"[{client_name}] Запит на з'єднання...")
        # Семафор пропускає не більше max_connections потоків одночасно;
        # решта блокується тут, поки хтось не викличе release()
        self._semaphore.acquire()

        # Лічильники змінюються кількома потоками, тому захищаємо їх Lock
        with self._lock:
            self.active_connections += 1
            self.peak_connections = max(self.peak_connections,
                                        self.active_connections)
            if self.active_connections > self.max_connections:
                self.violations += 1
            active = self.active_connections
        print(f"[{client_name}] З'єднання отримано (активних: {active})")

    def release_connection(self, client_name: str) -> None:
        """Повернення з'єднання до пулу."""
        with self._lock:
            self.active_connections -= 1
            self.total_served += 1
        # Семафор звільняємо ПІСЛЯ зменшення лічильника, інакше інший потік
        # міг би встигнути отримати місце, і active тимчасово перевищив би max
        self._semaphore.release()
        print(f"[{client_name}] З'єднання повернено")

    def get_stats(self) -> dict:
        """Повертає статистику використання пулу."""
        return {
            "max": self.max_connections,
            "active": self.active_connections,
            "total_served": self.total_served,
            "peak": self.peak_connections,
            "violations": self.violations,
        }


def client_task(pool: ConnectionPool, client_name: str,
                ready_event: threading.Event) -> None:
    """Клієнт, що чекає сигналу готовності та використовує з'єднання."""
    # Усі клієнти блокуються тут, доки головний потік не викличе set()
    ready_event.wait()

    pool.acquire_connection(client_name)
    try:
        work_time = random.uniform(0.5, 2.0)
        print(f"  [{client_name}] Працює {work_time:.1f} сек "
              f"(активних: {pool.active_connections})")
        time.sleep(work_time)
    finally:
        # Повертаємо з'єднання навіть якщо під час роботи сталася помилка
        pool.release_connection(client_name)


def main():
    pool = ConnectionPool(max_connections=3)
    ready_event = threading.Event()
    num_clients = 10

    # Створюємо та запускаємо потоки клієнтів
    threads = []
    for i in range(num_clients):
        t = threading.Thread(
            target=client_task,
            args=(pool, f"Client-{i:02d}", ready_event),
        )
        threads.append(t)
        t.start()

    # Даємо всім потокам час стартувати, потім подаємо сигнал на старт
    time.sleep(0.5)
    print(">>> Сервер готовий! Усі клієнти починають роботу.\n")
    ready_event.set()

    # Чекаємо завершення всіх потоків
    for t in threads:
        t.join()

    # Статистика пулу
    stats = pool.get_stats()
    print(f"\n=== Статистика пулу ===")
    print(f"Макс. з'єднань: {stats['max']}")
    print(f"Обслуговано клієнтів: {stats['total_served']}")
    print(f"Пікове навантаження: {stats['peak']}")
    print(f"Активних з'єднань наприкінці: {stats['active']}")
    print(f"Перевищень ліміту: {stats['violations']}")
    ok = stats["peak"] <= stats["max"] and stats["violations"] == 0
    print(f"Ліміт з'єднань ніколи не перевищувався: {'ТАК' if ok else 'НІ'}")


if __name__ == "__main__":
    main()
