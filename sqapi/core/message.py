
class Message:
    # TODO:
    # Should wrapper object for Message be used?
    # pros/cons:
    # - Extra fields easier to use (eg. timestamps etc.)
    # - Standardized transportation within sqAPI

    def __init__(self, message: dict):
        self.message = message
