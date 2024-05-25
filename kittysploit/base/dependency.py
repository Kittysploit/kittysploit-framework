try:
    import importlib
    import pkg_resources
except:
    print("Install importlib and pkg_resources")

PIP_TO_PYTHON_NAME = {
    "pyOpenSSL": "OpenSSL",
    "Pygments": "pygments",
    "BeautifulSoup4": "bs4",
    "flask-restx": "flask_restx",
}

def check_requirements_file(filename):
    print("ici")
    with open(filename, "r") as f:
        for line in f:
            print(line)
            package_info = line.strip().split("==")
            package_name = package_info[0]
            python_name = PIP_TO_PYTHON_NAME.get(package_name, package_name)
            try:
                module = importlib.import_module(python_name)
                if len(package_info) == 2:
                    required_version = package_info[1]
                    installed_version = pkg_resources.get_distribution(package_name).version
                    if installed_version != required_version:
                        print(f"[-] Package {package_name} has version {installed_version}, but version {required_version} is required.")
            except ImportError:
                print(f"[-] Package {package_name} is NOT installed.")
    return True