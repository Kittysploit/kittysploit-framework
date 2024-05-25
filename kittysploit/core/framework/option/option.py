from kittysploit.core.base.exceptions import OptionValidationError


class Option:

    def __init__(self, default, description="", required=False, advanced=False):

        self.description = description

        if default or default == 0:
            self.__set__("", default)
        else:
            self.display_value = ""
            self.value = ""
        try:
            self.required = bool(required)
        except:
            raise OptionValidationError(
                "Invalid value. Cannot cast '{}' to boolean.".format(required)
            )

        try:
            self.advanced = bool(advanced)
        except:
            raise OptionValidationError(
                "Invalid value. Cannot cast '{}' to boolean.".format(advanced)
            )

    def __get__(self, instance, owner):
        return self.value
