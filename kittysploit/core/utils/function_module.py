import importlib
from sqlalchemy import or_
from kittysploit.core.base.io import print_error
from kittysploit.core.base.exceptions import KittyException
from kittysploit.core.database.schema import db, Modules
import os


def pythonize_path(path):
    """Replaces argument to valid python dotted notation.

    ex. foo/bar/baz -> foo.bar.baz

    :param str path: path to pythonize
    :return str: pythonized path
    """

    return path.replace("/", ".")


def humanize_path(path):
    """Replace python dotted path to directory-like one.

    ex. foo.bar.baz -> foo/bar/baz

    :param str path: path to humanize
    :return str: humanized path
    """

    return path.replace(".", "/")


def check_and_load_module(module_name: str) -> bool:
    """Check if a module exists"""
    module_path = pythonize_path(module_name)
    module_path = ".".join(("modules", module_path))
    try:
        loaded_module = import_module(module_path)
        if loaded_module:
            return loaded_module
        return False
    except SyntaxError as e:
        print_error(e)
        return False


def import_module(path: str):
    """Imports exploit module

    :param str path: absolute path to exploit e.g. modules.exploits.asus_auth_bypass
    :return: exploit module or error
    """

    try:
        module = importlib.import_module(path)
        if hasattr(module, "Module"):
            return getattr(module, "Module")
        else:
            raise ImportError("No module named '{}'".format(path))

    except (ImportError, AttributeError, KeyError) as err:
        raise KittyException(
            "Error during loading '{}'\n\n"
            "Error: {}\n\n"
            "It should be valid path to the module. "
            "Use <tab> key multiple times for completion.".format(path, err)
        )


def module_metadata(module):

    metadata = getattr(module, "_Module__info__")
    return metadata

def index_modules():
    """Returns list of all exploits modules

    :param str modules_directory: path to modules directory
    :return list: list of found modules
    """

    modules_query = (
        db.query(Modules.path)
        .filter(
            or_(
                Modules.type_module == "exploit",
                Modules.type_module == "auxiliary",
                Modules.type_module == "post",
                Modules.type_module == "browser_exploit",
                Modules.type_module == "browser_auxiliary",
                Modules.type_module == "backdoor",
                Modules.type_module == "listener",
                Modules.type_module == "payload",
                Modules.type_module == "dev",
            )
        )
        .all()
    )
    modules = [value for value, in modules_query]
    return modules


def file_exists(filename):
    return os.path.exists(filename)
