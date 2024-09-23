

class MuscularError(Exception):

    def __init__(self, status=500, reason=None, body=None):
        self.status = status
        self.reason = reason
        self.body = body
        super().__init__(self.reason)


class ResponseErrorHandler(Exception):

    def __init__(self, status=500, reason=None, body=None):
        self.status = status
        self.reason = reason
        self.body = body
        super().__init__(self.reason)


class ApplicationException(Exception):
    def __init__(self, status=500, reason=None, body=None):
        self.status = status
        self.reason = reason
        self.body = body
        super().__init__(self.reason)


class ErrorsException(Exception):
    def __init__(self, status=500, reason=None, body=None):
        self.status = status
        self.reason = reason
        self.body = body
        super().__init__(self.reason)


class NotFoundException(ApplicationException):
    def __init__(self, status=404, reason="Not Found", body=None):
        self.status = status
        self.reason = reason
        self.body = body or "Indicates that the origin server did not find a current representation " \
                            "for the target resource or is not willing to disclose that one exists."
        super().__init__(self.status, self.reason)


class ForbiddenException(ApplicationException):
    def __init__(self, status=403, reason="Forbidden", body=None):
        self.status = status
        self.reason = reason
        self.body = body or "Indicates that the server understood the request but refuses to authorize it."
        super().__init__(self.status, self.reason)


class NotTeapotException(ApplicationException):
    def __init__(self, status=418, reason="I'm a teapot", body=None):
        self.status = status
        self.reason = reason
        self.body = body or "Any attempt to brew coffee with a teapot should result in the error code 418 I'm a teapot."
        super().__init__(self.status, self.reason)


class AttributeException(ApplicationException):
    def __init__(self, status=418, reason="Attribute error", body=None):
        self.status = status
        self.reason = reason
        self.body = body or "Attribute error."
        super().__init__(self.status, self.reason)

