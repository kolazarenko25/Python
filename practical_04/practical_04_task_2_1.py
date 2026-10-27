# practical_04_task_2_1.py

"""Демонстрація race condition та захист через Lock."""

import threading
import time
import random


class BankAccount:
    """Банківський рахунок без синхронізації (небезпечний)."""

    def __init__(self, balance: float = 0.0):
        self.balance = balance
        self.transaction_count = 0

    def deposit(self, amount: float) -> None:
        """Поповнення рахунку."""
        # Імітація неатомарної операції: read -> (пауза) -> write
        current = self.balance
        time.sleep(random.uniform(0.0001, 0.001))
        self.balance = current + amount
        self.transaction_count += 1

    def withdraw(self, amount: float) -> bool:
        """Зняття коштів. Повертає True, якщо операція успішна."""
        current = self.balance
        time.sleep(random.uniform(0.0001, 0.001))
        if current >= amount:
            self.balance = current - amount
            self.transaction_count += 1
            return True
        return False


class SafeBankAccount:
    """Банківський рахунок із синхронізацією через Lock."""

    def __init__(self, balance: float = 0.0):
        self.balance = balance
        self.transaction_count = 0
        self._lock = threading.Lock()

    def deposit(self, amount: float) -> None:
        # Уся критична секція (read -> write) виконується під замком,
        # тому інші потоки не можуть "втрутитися" між читанням і записом
        with self._lock:
            current = self.balance
            time.sleep(random.uniform(0.0001, 0.001))
            self.balance = current + amount
            self.transaction_count += 1

    def withdraw(self, amount: float) -> bool:
        with self._lock:
            current = self.balance
            time.sleep(random.uniform(0.0001, 0.001))
            if current >= amount:
                self.balance = current - amount
                self.transaction_count += 1
                return True
            return False


def run_transactions(account, num_deposits: int, num_withdrawals: int,
                     deposit_amount: float = 50.0,
                     withdraw_amount: float = 50.0,
                     num_threads: int = 10) -> int:
    """Запускає потоки для виконання транзакцій.

    Створює num_threads потоків поповнення та num_threads потоків зняття
    (разом 2 * num_threads потоків). Загальна кількість операцій
    розподіляється порівну між потоками.

    Returns:
        Кількість відхилених зняттів (коли на рахунку не вистачало коштів).
    """
    deposits_per_thread = num_deposits // num_threads
    withdrawals_per_thread = num_withdrawals // num_threads
    # Кожен потік зняття пише у власну комірку, тому гонки тут немає
    rejected_per_thread = [0] * num_threads

    def deposit_worker() -> None:
        for _ in range(deposits_per_thread):
            account.deposit(deposit_amount)

    def withdraw_worker(index: int) -> None:
        for _ in range(withdrawals_per_thread):
            if not account.withdraw(withdraw_amount):
                rejected_per_thread[index] += 1

    threads = []
    for i in range(num_threads):
        threads.append(threading.Thread(target=deposit_worker,
                                        name=f"Deposit-{i}"))
        threads.append(threading.Thread(target=withdraw_worker, args=(i,),
                                        name=f"Withdraw-{i}"))

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    return sum(rejected_per_thread)


def print_report(account, expected_balance: float, expected_transactions: int,
                 rejected: int, withdraw_amount: float) -> bool:
    """Виводить звіт і повертає True, якщо баланс збігається з очікуваним."""
    # Відхилене зняття не змінює баланс, тому коригуємо очікування
    expected = expected_balance + rejected * withdraw_amount
    expected_tx = expected_transactions - rejected
    matches = abs(account.balance - expected) < 1e-9

    print(f"  Очікуваний баланс : {expected:.2f}")
    print(f"  Фактичний баланс  : {account.balance:.2f}")
    print(f"  Баланси збігаються: {'ТАК' if matches else 'НІ'}")
    print(f"  Транзакцій виконано: {account.transaction_count} "
          f"(очікувалось {expected_tx})")
    if rejected:
        print(f"  Відхилено зняттів (брак коштів): {rejected}")
    return matches


def main():
    initial_balance = 1000.0
    num_deposits = 100
    deposit_amount = 50.0
    num_withdrawals = 100
    withdraw_amount = 50.0
    num_threads = 10  # потоків на кожен тип операції (разом 20)

    expected_balance = (
        initial_balance
        + num_deposits * deposit_amount
        - num_withdrawals * withdraw_amount
    )
    expected_transactions = num_deposits + num_withdrawals

    # === Тест 1: Без синхронізації ===
    print("=== Тест без синхронізації ===")
    print(f"Початковий баланс: {initial_balance:.2f}, потоків: "
          f"{2 * num_threads}")
    # Гонка недетермінована: у рідкісному випадку втрати можуть
    # взаємно скомпенсуватися, тому за потреби повторюємо (до 3 спроб)
    for attempt in range(1, 4):
        unsafe_account = BankAccount(initial_balance)
        rejected = run_transactions(unsafe_account, num_deposits,
                                    num_withdrawals, deposit_amount,
                                    withdraw_amount, num_threads)
        print(f"Спроба {attempt}:")
        matches = print_report(unsafe_account, expected_balance,
                               expected_transactions, rejected,
                               withdraw_amount)
        if not matches:
            print("  >>> RACE CONDITION: частина оновлень втрачена!")
            break

    # === Тест 2: З синхронізацією (Lock) ===
    print("\n=== Тест із синхронізацією (Lock) ===")
    print(f"Початковий баланс: {initial_balance:.2f}, потоків: "
          f"{2 * num_threads}")
    safe_account = SafeBankAccount(initial_balance)
    rejected = run_transactions(safe_account, num_deposits, num_withdrawals,
                                deposit_amount, withdraw_amount, num_threads)
    matches = print_report(safe_account, expected_balance,
                           expected_transactions, rejected, withdraw_amount)
    if matches:
        print("  >>> Синхронізація працює: втрат оновлень немає.")

    print(f"\nОчікуваний баланс: {expected_balance:.2f}")


if __name__ == "__main__":
    main()
