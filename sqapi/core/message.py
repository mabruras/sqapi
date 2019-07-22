class Message:
    # TODO:
    # Should wrapper object for Message be used?
    # pros/cons:
    # - Extra fields easier to use (eg. timestamps etc.)
    # - Standardized transportation within sqAPI
    # - Is it necessary, or is it only container for message body?

    def __init__(self, body: dict):
        self.body = body
