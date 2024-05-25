class KittyException(Exception):
    def __init__(self, msg: str = ""):
        super(KittyException, self).__init__(msg)


class OptionValidationError(KittyException):
    pass


class StopThreadPoolExecutor(KittyException):
    pass


class WasNotFoundException(KittyException):
    pass


class MaxLengthException(KittyException):
    pass
