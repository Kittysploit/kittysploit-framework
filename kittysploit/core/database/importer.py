from kittysploit.core.base.io import print_info, print_status, print_success
from kittysploit.core.database.schema import db, Modules, Cve
from kittysploit.core.base.storage import LocalStorage
from kittysploit.core.utils.function_module import (
    import_module,
    pythonize_path,
    module_metadata,
)
from kittysploit.base.kitty_path import base_path
from sqlalchemy import distinct
import os

def check_if_double() -> None:

    # Get a list of distinct records
    distinct_records = db.query(distinct(Modules.path))

    # Delete duplicates
    for record in distinct_records:
        duplicate_records = db.query(Modules).filter(Modules.path == record[0]).all()
        for duplicate_record in duplicate_records[1:]:  # Keep the first record, delete the rest
            db.delete(duplicate_record)

    # Commit the changes
    db.commit()

def init_count_modules() -> None:
    """
    Initial number of modules
    """
    check_if_double()

    local_storage = LocalStorage()
    exploits = db.query(Modules).filter(Modules.type_module == "exploit").filter(Modules.dev_mode == False).count()
    auxiliary = db.query(Modules).filter(Modules.type_module == "auxiliary").filter(Modules.dev_mode == False).count()
    post = db.query(Modules).filter(Modules.type_module == "post").filter(Modules.dev_mode == False).count()
    payloads = db.query(Modules).filter(Modules.type_module == "payload").filter(Modules.dev_mode == False).count()
    browser_exploits = db.query(Modules).filter(Modules.type_module == "browser_exploit").filter(Modules.dev_mode == False).count()
    browser_auxiliary = db.query(Modules).filter(Modules.type_module == "browser_auxiliary").filter(Modules.dev_mode == False).count()
    encoders = db.query(Modules).filter(Modules.type_module == "encoder").filter(Modules.dev_mode == False).count()
    listeners = db.query(Modules).filter(Modules.type_module == "listener").filter(Modules.dev_mode == False).count()
    plugins = db.query(Modules).filter(Modules.type_module == "plugin").filter(Modules.dev_mode == False).count()
    backdoors = db.query(Modules).filter(Modules.type_module == "backdoor").filter(Modules.dev_mode == False).count()
    bots = db.query(Modules).filter(Modules.type_module == "bot").filter(Modules.dev_mode == False).count()
    remotescan = db.query(Modules).filter(Modules.type_module == "remotescan").filter(Modules.dev_mode == False).count()
    localscan = db.query(Modules).filter(Modules.type_module == "localscan").filter(Modules.dev_mode == False).count()
    dev = db.query(Modules).filter(Modules.dev_mode == True).count()
    cve = db.query(Cve).count()
    local_storage.set("exploits", exploits)
    local_storage.set("auxiliary", auxiliary)
    local_storage.set("post", post)
    local_storage.set("payloads", payloads)
    local_storage.set("browser_exploits", browser_exploits)
    local_storage.set("browser_auxiliary", browser_auxiliary)
    local_storage.set("encoders", encoders)
    local_storage.set("listeners", listeners)
    local_storage.set("plugins", plugins)
    local_storage.set("backdoors", backdoors)
    local_storage.set("bots", bots)
    local_storage.set("remotescan", remotescan)
    local_storage.set("localscan", localscan)
    local_storage.set("dev", dev)
    local_storage.set("cve", cve)


def clean_modules() -> None:
    """
    Clean modules
    """

    all_modules = db.query(Modules).all()
    for module in all_modules:
        db.delete(module)
    db.commit()

def load_modules():
    print_status("Loading modules...")
    all_modules = db.query(Modules.path).all()
    all_modules_list = [value for value, in all_modules]
    for dirpath, dirnames, filenames in os.walk("modules"):

        for filename in filenames:
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = filename[:-3]
                module_path = os.path.join(dirpath, filename)
                relative_module_path = os.path.relpath(module_path, "modules")
                try:
                    current_module = pythonize_path(module_path[:-3])
                    load_module = import_module(current_module)
                    if load_module.TYPE_MODULE == "remotescan":
                        metadata = getattr(load_module, "__info__")
                    else:
                        metadata = getattr(load_module, "_Module__info__")
                    name = ""
                    description = ""
                    cve = ""
                    rank = ""
                    platform = ""
                    arch = ""
                    plugin = ""
                    protocol = ""
                    dev_mode = False
                    if hasattr(load_module, "DEV_MODE"):
                        if load_module.DEV_MODE:
                            dev_mode = True
                        else:
                            dev_mode = False
                    if "name" in metadata:
                        name = metadata["name"]
                    if "description" in metadata:
                        description = metadata["description"]
                    if "cve" in metadata:
                        cve = metadata["cve"]
                    if "rank" in metadata:
                        rank = metadata["rank"]
                    if "plugin" in metadata:
                        plugin = metadata["plugin"]
                    if "protocol" in metadata:
                        protocol = metadata["protocol"]
                    type_module = load_module.TYPE_MODULE
                    existing_module = db.query(Modules).filter(Modules.path == relative_module_path[:-3]).first()
                    if existing_module:
                        if (existing_module.type_module != type_module or
                            existing_module.dev_mode != dev_mode or
                            existing_module.name != name or
                            existing_module.description != description or
                            existing_module.cve != cve):

                            existing_module.type_module = type_module
                            existing_module.dev_mode = dev_mode
                            existing_module.name = name
                            existing_module.description = description
                            existing_module.cve = cve
                            db.commit()
                    else:
                        new_module = Modules(
                            type_module=type_module,
                            dev_mode=dev_mode,
                            path=relative_module_path[:-3],
                            name=name,
                            description=description,
                            rank=rank,
                            cve=cve,
                            plugin=plugin,
                            platform=platform,
                            arch=arch,
                            protocol=protocol
                        )
                        db.add(new_module)
                        db.commit()
                        print_success(f"{type_module}: {module_name} added")
                except:
                    continue
    print_status("Done")


def load_plugins():
    print_status("Loading plugins...")
    all_plugins = db.query(Modules.path).all()
    all_plugins_list = [value for value, in all_plugins]
    for dirpath, dirnames, filenames in os.walk("plugins"):
        for filename in filenames:
            if filename.endswith(".py") and filename != "__init__.py":
                plugin_name = filename[:-3]
                plugin_path = os.path.join(dirpath, filename)
                if plugin_path not in all_plugins_list:
                    try:
                        current_plugin = pythonize_path(plugin_path[:-3])
                        load_plugin = import_module(current_plugin)

                        metadata = load_plugin.__info__
                        type_module = load_plugin.TYPE_MODULE
                        new_plugin = Modules(
                            type_module=type_module,
                            path=plugin_path[:-3],
                            name=metadata["name"],
                            description=metadata["description"],
                            rank="",
                            cve="",
                            plugin="",
                            platform="",
                            arch="",
                        )
                        db.add(new_plugin)
                        db.commit()
                        print_success(f"Plugin {plugin_name} loaded")
                    except:
                        continue
