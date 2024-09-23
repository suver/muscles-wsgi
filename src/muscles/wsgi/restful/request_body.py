

class RequestBody:

    def __init__(self, content_type=None, description=None, model=None):
        self.content_type = content_type
        self.description = description
        self.model = model


class JsonRequestBody(RequestBody):

    def __init__(self, description=None, model=None):
        content_type = 'application/json'
        super().__init__(content_type=content_type, description=description, model=model)


class XmlRequestBody(RequestBody):

    def __init__(self, description=None, model=None):
        content_type = 'application/xml'
        super().__init__(content_type=content_type, description=description, model=model)


class FormRequestBody(RequestBody):

    def __init__(self, description=None, model=None):
        content_type = 'application/x-www-form-urlencoded'
        super().__init__(content_type=content_type, description=description, model=model)


class MultipartRequestBody(RequestBody):

    def __init__(self, description=None, model=None):
        content_type = 'multipart/form-data'
        super().__init__(content_type=content_type, description=description, model=model)


class FileRequestBody(RequestBody):

    def __init__(self, content_type=None, description=None, model=None):
        super().__init__(content_type=content_type, description=description, model=model)


class PayloadRequestBody(RequestBody):

    def __init__(self, description=None, model=None):
        content_type = 'text/plain'
        super().__init__(content_type=content_type, description=description, model=model)


class TextRequestBody(RequestBody):

    def __init__(self, description=None, model=None):
        content_type = 'text/plain'
        super().__init__(content_type=content_type, description=description, model=model)


