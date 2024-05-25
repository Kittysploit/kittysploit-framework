from kittysploit.core.framework.option.option import Option
from kittysploit.core.base.exceptions import OptionValidationError


class OptPort(Option):
    """Option Port attribute"""

    def __set__(self, instance, value):
        try:
            value = int(value)

            if 0 < value <= 65535:
                self.display_value = str(value)
                self.value = value
            else:
                raise OptionValidationError(
                    "Invalid option. Port value should be between 0 and 65536."
                )
        except ValueError:
            raise OptionValidationError(
                "Invalid option. Cannot cast '{}' to integer.".format(value)
            )
