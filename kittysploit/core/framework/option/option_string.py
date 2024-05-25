from kittysploit.core.framework.option.option import Option
from kittysploit.core.base.exceptions import OptionValidationError


class OptString(Option):
    """Option String attribute"""

    def __set__(self, instance, value):
        try:
            self.value = self.display_value = str(value)
        except ValueError:
            raise OptionValidationError(
                "Invalid option. Cannot cast '{}' to string.".format(value)
            )
