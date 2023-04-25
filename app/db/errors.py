class BaseDBError(Exception):
    _message = ''

    def __init__(self, *args):
        super().__init__(*args)

    def __str__(self):
        return self._message.format(**getattr(self, 'attrs', {}))


class NotFoundInDBError(BaseDBError):
    _message = 'Not found {entity} in db'

    def __init__(self, entity, *args):
        super().__init__(*args)
        self.attrs = {
            'entity': entity,
        }


class IntegrityDBError(BaseDBError):
    _message = 'Integrity error with params {params}'

    def __init__(self, params, *args):
        super().__init__(*args)
        self.attrs = {
            'params': params,
        }
