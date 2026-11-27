class Observer:
    def update(self, message):
        pass


class TicketNotification(Observer):

    def update(self, message):
        print(f"NOTIFICATION: {message}")


class TicketManager:

    def __init__(self):
        self.observers = []

    # Добавление наблюдателя
    def attach(self, observer):
        self.observers.append(observer)

    # Удаление наблюдателя
    def detach(self, observer):
        self.observers.remove(observer)

    # Отправка уведомлений
    def notify(self, message):
        for observer in self.observers:
            observer.update(message)

    # Изменение статуса заявки
    def change_status(self, ticket_id, status):
        message = (
            f"Ticket #{ticket_id} status changed to {status}"
        )
        self.notify(message)
