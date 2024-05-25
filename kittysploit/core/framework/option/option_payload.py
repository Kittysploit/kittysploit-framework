from kittysploit.core.framework.option.option import Option
from kittysploit.core.base.exceptions import OptionValidationError
from kittysploit.core.utils.function_module import pythonize_path
import importlib


class OptPayload(Option):
    """Option Payload attribute"""

    def __set__(self, instance, value):
        payload = instance._add_payload_option(value)
        try:
            self.value = self.display_value = str(value)
        except ValueError:
            raise OptionValidationError(
                "Invalid option. Cannot cast '{}' to string.".format(value)
            )

    def __get__(self, instance, owner):
        payload_path = pythonize_path(self.display_value)
        module_payload = ".".join(("modules", payload_path))
        module_payload = getattr(importlib.import_module(module_payload), "Module")()
        _payload = module_payload.generate()
        if "encoder" in owner.exploit_attributes:
            if owner.exploit_attributes["encoder"][0]:
                encoder_path = pythonize_path(owner.exploit_attributes["encoder"][0])
                module_encoder = ".".join(("modules", encoder_path))
                module_encoder = getattr(
                    importlib.import_module(module_encoder), "Module"
                )()
                _payload = module_encoder.encode(_payload)
        return _payload
