import argparse
from kittysploit.core.base.io import print_info
from kittysploit.core.base.exceptions import KittyException


class MyParserException(Exception):
    """Custom exception."""

    pass


class ModuleArgumentParser(argparse.ArgumentParser):
    """Forced to override argparse methods."""

    def __init__(self, *args, **kwargs):
        argparse.ArgumentParser.__init__(self, *args, **kwargs)

    def parse_known_args(self, args=None, namespace=None):
        """Override method to prevent -h from printing then calling sys.exit()."""

        try:
            return argparse.ArgumentParser.parse_known_args(self, args, namespace)
        except SystemExit:
            pass

        return None, None

    def error(self, message):
        """Override method to prevent argparse from calling sys.exit()."""

        self.print_usage()
        raise KittyException

    def _print_message(self, message, file=None):
        print_info(message)
