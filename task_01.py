import random
import time
from collections import deque
from typing import Dict

class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        self.messages = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        if user_id in self.messages:
            while self.messages[user_id] and current_time - self.messages[user_id][0] > self.window_size:
                self.messages[user_id].popleft()
            if not self.messages[user_id]:
                del self.messages[user_id]

    def can_send_message(self, user_id: str) -> bool:
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        return len(self.messages.get(user_id, deque())) < self.max_requests

    def record_message(self, user_id: str) -> bool:
        if self.can_send_message(user_id):
            if user_id not in self.messages:
                self.messages[user_id] = deque()
            self.messages[user_id].append(time.time())
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        if user_id in self.messages and len(self.messages[user_id]) == self.max_requests:
            next_allowed_time = self.messages[user_id][0] + self.window_size
            return max(0, next_allowed_time - time.time())
        return 0.0

def test_rate_limiter():
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)
    print("\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | {'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        time.sleep(random.uniform(0.1, 1.0))

    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | {'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    test_rate_limiter()
