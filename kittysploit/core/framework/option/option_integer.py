from kittysploit.core.framework.option.option import Option
from kittysploit.core.base.exceptions import OptionValidationError


class OptInteger(Option):
    """Option Integer attribute"""

    def __set__(self, instance, value):
        try:
            self.display_value = str(value)
            self.value = int(value)
        except ValueError:
            try:
                self.value = int(value, 16)
            except ValueError:
                raise OptionValidationError(
                    "Invalid option. Cannot cast '{}' to integer.".format(value)
                )
