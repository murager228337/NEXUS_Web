class PriorityStrategy:

    def process(self):
        raise NotImplementedError


class LowPriorityStrategy(PriorityStrategy):

    def process(self):
        return "This ticket will be handled in normal order."


class MediumPriorityStrategy(PriorityStrategy):

    def process(self):
        return "This ticket will be handled with increased priority."


class HighPriorityStrategy(PriorityStrategy):

    def process(self):
        return "This ticket will be handled as urgent."


class PriorityStrategyFactory:

    @staticmethod
    def get_strategy(priority):

        if priority == "Low":
            return LowPriorityStrategy()

        elif priority == "Medium":
            return MediumPriorityStrategy()

        elif priority == "High":
            return HighPriorityStrategy()

        else:
            raise ValueError("Unknown priority")
