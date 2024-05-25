from kittysploit.core.framework.option.option import Option
from kittysploit.core.base.exceptions import OptionValidationError


class OptBool(Option):
    """Option Bool attribute"""

    def __init__(self, default, description="", required=False, advanced=False):
        self.description = description

        if default:
            self.display_value = "true"
        else:
            self.display_value = "false"

        self.value = default
        try:
            self.required = bool(required)
        except:
            raise OptionValidationError(
                "Invalid value. Cannot cast '{}' to boolean.".format(required)
            )
        try:
            self.advanced = bool(advanced)
        except ValueError:
            raise OptionValidationError(
                "Invalid value. Cannot cast '{}' to boolean.".format(advanced)
            )

    def __set__(self, instance, value):
        if value == "true":
            self.value = True
            self.display_value = value
        elif value == "false":
            self.value = False
            self.display_value = value
        else:
            raise OptionValidationError("Invalid value. It should be true or false.")
