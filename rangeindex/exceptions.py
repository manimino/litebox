class InvalidFields(Exception):
    pass


class QueryMalformedError(Exception):
    pass


class QueryBadOperatorError(Exception):
    pass


class QueryTypeError(Exception):
    pass


class QueryUnknownFieldError(Exception):
    pass


class QueryBadNullComparator(Exception):
    pass


class InvalidEngineError(Exception):
    pass
