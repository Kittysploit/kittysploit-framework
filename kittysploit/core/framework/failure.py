from kittysploit.core.base.io import print_error, print_status
from kittysploit.core.base.storage import LocalStorage


class ProcedureError(Exception):
    def __init__(self, message) -> None:
        super().__init__(message)
        job_id = LocalStorage().get("exploit_job")
        if job_id != None:
            listener = job_id["listener"]
            thread = job_id["thread"]
            if listener:
                try:
                    listener.shutdown()
                    listener.stop()
                except:
                    pass


class ErrorDescription:
    """
    Error description.
    """

    def __init__(self, message) -> None:
        """
        Initializes a new instance of the ErrorDescription class.
        """
        self.message = message

    def __get__(self, instance, owner):

        print_error(self.message)
        raise ProcedureError(self.message)


class fail:

    BadConfig = ErrorDescription("Bad config file")
    Disconnect = ErrorDescription("Disconnected")
    NotAccess = ErrorDescription("No access")
    NoTarget = ErrorDescription("Target not compatible")
    NotFound = ErrorDescription("Not found")
    NotVulnerable = ErrorDescription("The application response indicated it was not vulnerable")
    PayloadFailed = ErrorDescription("The payload was delivered but no session was opened")
    TimeoutExpired = ErrorDescription("The exploit triggered some form of timeout")
    Unknown = ErrorDescription("Unknown error")
    UnReachable = ErrorDescription("The network service was unreachable")
    UserInterrupt = ErrorDescription("The exploit was interrupted by the user")
    NoSession = ErrorDescription("Exploit completed but no session was opened")
    PortBusy = ErrorDescription("Port is already busy")
    KeyboardInterrupt = ErrorDescription("Keyboard interrupt")
