from datetime import datetime
from patterns.observer import Observer


class NotificationDecorator(Observer):
    def __init__(self, wrapped):
        self._wrapped = wrapped

    def update(self, message):
        self._wrapped.update(message)


class TimestampDecorator(NotificationDecorator):
    def update(self, message):
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._wrapped.update(f"[{stamp}] {message}")