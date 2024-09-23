

class BaseParameter:

    def __init__(self, name, param_type, required=False, description=None):
        self.name = name
        self.param_type = param_type
        self.required = required
        self.description = description
        self.destination = None


class HeaderParameter(BaseParameter):

    def __init__(self, name, param_type, required=False, description=None):
        super().__init__(name, param_type, required=required, description=description)
        self.destination = 'header'


class QueryParameter(BaseParameter):

    def __init__(self, name, param_type, required=False, description=None):
        super().__init__(name, param_type, required=required, description=description)
        self.destination = 'query'


class CookieParameter(BaseParameter):

    def __init__(self, name, param_type, required=False, description=None):
        super().__init__(name, param_type, required=required, description=description)
        self.destination = 'cookie'


class PathParameter(BaseParameter):

    def __init__(self, name, param_type, required=False, description=None):
        super().__init__(name, param_type, required=required, description=description)
        self.destination = 'path'


# HeaderParameter('prm_check', Numeric(), required=False, type=Numeric, help='', choices=None)
# FileParameter('prm_check', Numeric(), required=False, type=Numeric, help='', choices=None)
# BodyParameter('prm_check', Numeric(), required=False, type=Numeric, help='', choices=None)
# CookiesParameter('prm_check', Numeric(), required=False, type=Numeric, help='', choices=None)
# ArgParameter('prm_check', Numeric(), required=False, type=Numeric, help='', choices=None)
# FormParameter('prm_check', Numeric(), required=False, type=Numeric, help='', choices=None)
