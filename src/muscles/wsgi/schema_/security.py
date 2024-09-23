from .schema import Schema


class BaseSecurity(Schema):

    schema = {}
    securitySchema = ""

    def __init__(self, *args, securitySchema=None, securityType=None, **kwargs):
        self.securitySchema = securitySchema
        self.schema = {
            "type": securityType,
        }
        for key, val in kwargs.items():
            self.schema.update({key: val})
        kwargs["securitySchema"] = securitySchema
        kwargs["securityType"] = securityType
        super().__init__(*args, **kwargs)

    def dump(self) -> dict:
        return {self.securitySchema: self.schema}


class BasicAuthSecurity(BaseSecurity):
    securitySchema = "BasicAuth"

    def __init__(self, *args, securityType='http', scheme='basic', **kwargs):
        kwargs["securitySchema"] = self.securitySchema
        kwargs["type"] = securityType
        kwargs["scheme"] = scheme
        super().__init__(*args, **kwargs)


class ApiKeyAuthSecurity(BaseSecurity):
    securitySchema = "ApiKeyAuth"

    def __init__(self, *args, securityType='apiKey', location='header', name='X-Api-Token', **kwargs):
        kwargs["securitySchema"] = self.securitySchema
        kwargs["type"] = securityType
        kwargs["in"] = location
        kwargs["name"] = name
        super().__init__(*args, **kwargs)


class BearerAuthSecurity(BaseSecurity):
    securitySchema = "BearerAuth"

    def __init__(self, *args, securityType='http', scheme='basic', **kwargs):
        kwargs["securitySchema"] = self.securitySchema
        kwargs["type"] = securityType
        kwargs["scheme"] = scheme
        super().__init__(*args, **kwargs)
