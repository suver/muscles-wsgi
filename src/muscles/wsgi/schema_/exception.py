

class ValidationColumnException(Exception):
    def __init__(self, field, message):
        self.field = field
        self.message = message
        super().__init__(message)

