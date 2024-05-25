from itertools import chain
from future.utils import with_metaclass, iteritems
from kittysploit.core.framework.option import Option
from typing import List
from kittysploit.core.base.io import print_error, print_success

class ModuleOptionsAggregator(type):

    def __new__(cls, name, bases, attrs):
        try:
            base_exploit_attributes = chain([base.exploit_attributes for base in bases])
        except AttributeError:
            attrs["exploit_attributes"] = {}
        else:
            attrs["exploit_attributes"] = {
                k: v for d in base_exploit_attributes for k, v in iteritems(d)
            }
        for key, value in list(iteritems(attrs)):
            if isinstance(value, Option):
                value.label = key
                attrs["exploit_attributes"].update(
                    {
                        key: [
                            value.display_value,
                            value.required,
                            value.description,
                            value.advanced,
                        ]
                    }
                )
            elif key == "__info__":
                attrs["_{}{}".format(name, key)] = value
                del attrs[key]
            elif key in attrs["exploit_attributes"]:
                del attrs["exploit_attributes"][key]
        return super(ModuleOptionsAggregator, cls).__new__(cls, name, bases, attrs)


class BaseModule(with_metaclass(ModuleOptionsAggregator, object)):
    """
    Base module class
    """

    MODULE_PATH = None
    LICENSE = "BDS 3 claude"
    
    @property
    def options(self) -> List:
        return list(self.exploit_attributes.keys())

    def __str__(self):
        return self.__module__.split(".")[-1]

    def default_options(self):
        return False