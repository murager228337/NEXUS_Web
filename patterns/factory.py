from patterns.prototype import Prototype

class Ticket(Prototype):
    category = None

    def __init__(self, title, description, priority, user_id):
        self.title = title
        self.description = description
        self.priority = priority
        self.user_id = user_id


class NetworkTicket(Ticket):
    category = "Network"


class HardwareTicket(Ticket):
    category = "Hardware"


class SoftwareTicket(Ticket):
    category = "Software"


class TicketFactory:

    @staticmethod
    def create_ticket(category, title, description, priority, user_id):

        if category == "Network":
            return NetworkTicket(
                title, description, priority, user_id
            )

        elif category == "Hardware":
            return HardwareTicket(
                title, description, priority, user_id
            )

        elif category == "Software":
            return SoftwareTicket(
                title, description, priority, user_id
            )

        else:
            raise ValueError("Unknown ticket category")
