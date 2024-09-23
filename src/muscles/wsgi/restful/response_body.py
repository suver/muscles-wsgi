

class ResponseBody:

    def __init__(self, content_type=None, description=None, http_code=None, model=None):
        self.content_type = content_type
        self.description = description
        self.http_code = http_code
        self.model = model


class EmptyResponseBody(ResponseBody):

    def __init__(self, description=None, http_code=None, model=None):
        content_type = None
        super().__init__(content_type=content_type, description=description, http_code=http_code, model=model)


class JsonResponseBody(ResponseBody):

    def __init__(self, description=None, http_code=None, model=None):
        content_type = 'application/json'
        super().__init__(content_type=content_type, description=description, http_code=http_code, model=model)


class XmlResponseBody(ResponseBody):

    def __init__(self, description=None, http_code=None, model=None):
        content_type = 'application/xml'
        super().__init__(content_type=content_type, description=description, http_code=http_code, model=model)


class TextResponseBody(ResponseBody):

    def __init__(self, description=None, http_code=None, model=None):
        content_type = 'text/plain'
        super().__init__(content_type=content_type, description=description, http_code=http_code, model=model)


