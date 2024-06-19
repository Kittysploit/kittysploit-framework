import sys
try:
    import importlib
    import importlib.metadata
except:
    print("Install importlib")

PIP_TO_PYTHON_NAME = {
    "pyOpenSSL": "OpenSSL",
    "Pygments": "pygments",
    "BeautifulSoup4": "bs4",
    "flask-restx": "flask_restx",
}

if sys.version_info < (3, 10):
    print("Python 3.10 or higher is required to run kittysploit.")
    raise SystemExit(0)

def check_requirements_file(filename):
    missing = False
    with open(filename, "r") as f:
        for line in f:
            package_info = line.strip().split("==")
            package_name = package_info[0]
            python_name = PIP_TO_PYTHON_NAME.get(package_name, package_name)
            try:
                module = importlib.import_module(python_name)
                if len(package_info) == 2:
                    required_version = package_info[1]
                    installed_version = importlib.metadata.distribution(package_name).version
                    if installed_version != required_version:
                        missing = True
                        print(f"[-] Package {package_name} has version {installed_version}, but version {required_version} is required.")
            except ImportError:
                missing = True
                print(f"[-] Package {package_name} is NOT installed.")
    return missing

print("Check dependency...")
if check_requirements_file("install/requirements.txt"):
	print("Missing lib: pip3 install -r install/requirements.txt")
	raise SystemExit(0)

from kittysploit.runtime import main_console
import pretty_errors

if __name__ == "__main__":
    main_console()
