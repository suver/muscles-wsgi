from .schema import Schema


class BaseCollection(Schema):
    pass


class Collection(BaseCollection):

    def __init__(self, collection_name, *columns, **kwargs):
        kwargs['collection_name'] = collection_name
        super().__init__(*columns, **kwargs)
        self.collection_name = collection_name
        self.columns = columns

