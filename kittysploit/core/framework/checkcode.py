from kittysploit.core.base.io import print_success


class SuccessDescription:

    def __init__(self, message="") -> None:

        self.message = message

    def __get__(self, instance, owner):
        print_success(self.message)


class vulnerable:

    SUCCESS = SuccessDescription("The target is vulnerable")
    APPEARS = SuccessDescription("The target appears to be vulnerable")
    VULNERABLE = SuccessDescription("The target is vulnerable")

    def __init__(self, message="") -> None:
        SuccessDescription(message)
