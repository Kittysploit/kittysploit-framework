from kittysploit import *

class Module(BrowserAuxiliary):

	__info__ = {
		"name": "xss alert",
		"description": "Execute alert on browser victim",
		"target": (
			"all",
		),
	}	
	
	message = OptString("Python rocks", "Write message into alert", True)

	def run(self):
		self.send_js(f"alert('{self.message}');")