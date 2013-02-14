class GooBaseException(Exception):
    """
    All Goo exceptions inherit from this exception.
    """


class HttpBaseException(GooBaseException):
    """
    All Goo HTTP Exceptions inherit from this exception.
    """

    def __init__(self, *args, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
        super(HttpBaseException, self).__init__(*args)


class HttpClientError(HttpBaseException):
    """
    Called when the server tells us there was a client error (4xx).
    """


class HttpServerError(HttpBaseException):
    """
    Called when the server tells us there was a server error (5xx).
    """


class SerializerNoAvailable(GooBaseException):
    """
    There are no available Serializers.
    """


class SerializerNotAvailable(GooBaseException):
    """
    The chosen Serializer is not available.
    """
