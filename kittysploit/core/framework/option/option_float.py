from kittysploit.core.framework.option.option import Option
from kittysploit.core.base.exceptions import OptionValidationError


class OptFloat(Option):
    """Option Float attribute"""

    def __set__(self, instance, value):
        try:
            self.display_value = str(value)
            self.value = float(value)
        except ValueError:
            raise OptionValidationError(
                "Invalid option. Cannot cast '{}' to float.".format(value)
            )
