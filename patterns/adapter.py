from patterns.observer import Observer


class FileLogger:

    def __init__(self, path):
        self.path = path

    def write_line(self, text):
        with open(self.path, "a", encoding="utf-8") as file:
            file.write(text + "\n")


class FileLoggerAdapter(Observer):

    def __init__(self, logger):
        self._logger = logger

    def update(self, message):
        self._logger.write_line(message)